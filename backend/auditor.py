from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import opik
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

# Initialize Opik
if os.getenv("OPIK_API_KEY"):
    os.environ["OPIK_PROJECT_NAME"] = "fine-print-xray"
    try:
        opik.configure(use_local=False)
    except Exception as e:
        print(f"Failed to configure Opik Cloud: {e}")
else:
    print("OPIK_API_KEY not found. Defaulting to local/disabled mode.")

# --- Pydantic Models for Structured Output ---
class DetectionObject(BaseModel):
    original_text: str = Field(description="The exact text quoted from the document")
    risk_level: str = Field(description="CRITICAL | CAUTION | INFO")
    category: str = Field(description="Hidden Fees | Privacy | Contract Length | Other")
    plain_english_explanation: str = Field(description="Explain why this is a trap for a 5th grader")
    estimated_cost_impact: str = Field(description="$ value or 'High' if unquantifiable")
    remediation: str = Field(description="What should the user ask for or do instead?")

class AuditResult(BaseModel):
    detected_traps: List[DetectionObject]
    overall_predatory_score: int = Field(description="0-100 score, where 100 is extremely predatory")

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a Senior Financial Forensic Auditor and Consumer Advocate. Your goal is to "X-ray" Terms & Conditions (T&C) and Contracts to find "Financial Traps"—clauses that are mathematically disadvantageous, legally restrictive, or intentionally obscure.

### CAPABILITIES
1. MULTILINGUAL ANALYSIS: If the text is not in English, first identify the language, translate the core concepts internally, but report findings in English.
2. ZERO-TRUST MINDSET: Assume the contract writer is adversarial. Scrutinize every sentence.
3. BIAS FOR DETECTION: It is better to flag a "CAUTION" item that turns out to be minor, than to miss a real trap. Do not be lenient.
4. TRAP DETECTION: Look for:
    - "Zombie Fees": Hidden recurring charges.
    - "Arbitrary Price Hikes": Clauses allowing the company to change rates without notice.
    - "The Friction Trap": Excessive requirements for cancellation.
    - "Data Monetization": Permission to sell financial behavior (CRITICAL).
    - "Data Sovereignty/Location": Storage in lower-privacy jurisdictions (CAUTION).
    - "Liability Shifts": Making the user responsible for platform errors.
    - "Mandatory Arbitration / Class Action Waiver": Forcing users to waive their right to sue (Common in Banks/Gyms).
    - "Liquidated Damages": Excessive penalties for breaking the contract early.
    - "Unilateral Term Changes": Right to change T&Cs at any time (CRITICAL).

### FEW-SHOT EXAMPLES (Validation Pattern)
(See prompt engineering file for full examples)

### SELF-CRITIQUE PROTOCOL
Before outputting, ask yourself:
1. Is this actually a trap, or just standard legal boilerplate?
2. Is the 'original_text' exact? (Do not paraphrase).
3. If the trap is weak, classify as 'INFO' or ignore it.

### OUTPUT INSTRUCTIONS
Return a JSON object matching the schema provided. 
MANDATORY: The 'original_text' field must be an EXACT copy of the substring found in the document. Do not paraphrase the quote.
"""

def get_auditor_chain():
    # Use Grok 4.1 Fast (xAI) via OpenAI SDK
    llm = ChatOpenAI(
        model="grok-4-1-fast-non-reasoning",
        openai_api_key=os.getenv("XAI_API_KEY"),
        openai_api_base="https://api.x.ai/v1",
        temperature=0
    )
    parser = PydanticOutputParser(pydantic_object=AuditResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "AUDIT THE FOLLOWING DOCUMENT:\n----------\n{contract_text}\n----------\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser
    return chain

@opik.track(name="contract_audit")
def analyze_contract_text(text: str) -> AuditResult:
    # Use Grok 3 Mini
    chain = get_auditor_chain()
    parser = PydanticOutputParser(pydantic_object=AuditResult)
    
    # Retry Logic
    MAX_RETRIES = 3
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🤖 Analyzing with Grok 4.1 Fast (Attempt {attempt+1})...")
            
            # We invoke the chain
            result = chain.invoke({
                "contract_text": text,
                "format_instructions": parser.get_format_instructions()
            })
            
            # --- DETERMINISTIC SCORING ALGORITHM ---
            calculated_score = 0
            for trap in result.detected_traps:
                risk = trap.risk_level.upper()
                if "CRITICAL" in risk:
                    calculated_score += 20
                elif "CAUTION" in risk:
                    calculated_score += 5
                else:
                    calculated_score += 1
            
            # Cap score at 100
            result.overall_predatory_score = min(calculated_score, 100)
            
            return result

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 * (attempt + 1)
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                return AuditResult(
                    detected_traps=[
                        DetectionObject(
                            original_text="System Error",
                            risk_level="INFO",
                            category="System",
                            plain_english_explanation="The AI service is currently overloaded. Please wait 10 seconds and try again.",
                            estimated_cost_impact="None",
                            remediation="Retry shortly."
                        )
                    ], 
                    overall_predatory_score=0
                )
    
class NegotiationResult(BaseModel):
    subject_line: str = Field(description="A formal, punchy subject line for the email")
    email_body: str = Field(description="The body of the email. Formal but firm.")

def generate_negotiation_email(trap_text: str, category: str, explanation: str) -> NegotiationResult:
    llm = ChatOpenAI(
        model="grok-4-1-fast-non-reasoning",
        openai_api_key=os.getenv("XAI_API_KEY"),
        openai_api_base="https://api.x.ai/v1",
        temperature=0.1
    )
    parser = PydanticOutputParser(pydantic_object=NegotiationResult)

    negotiation_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an aggressive Consumer Rights Lawyer specialized in contract law.
        Your goal is to write a SPECIFIC, LEGALLY GROUNDED email to opt-out, dispute, or negotiate a predatory clause.

        ### STRATEGY BY CATEGORY:
        1. **Mandatory Arbitration / Class Action Waiver**:
           - SUBJECT: "NOTICE OF OPT-OUT: Arbitration Agreement - [Your Name]"
           - BODY: Explicitly state: "I hereby reject the arbitration agreement and class action waiver provisions."
           - CITE: "My right to opt-out within 30 days of service activation."

        2. **Hidden Fees / Price Hikes**:
           - SUBJECT: "Notice of Objection: Materially Adverse Change to Terms"
           - BODY: Argue "Lack of Mutual Assent" or "Unfair/Deceptive Practice."
           - DEMAND: "Confirmation that my original grandfathered rate will be honored."

        3. **Data Privacy / Selling Data**:
           - SUBJECT: "NOTICE: Revocation of Consent for Data Sale (CCPA/GDPR)"
           - BODY: Exercise specific rights (e.g., "Do Not Sell My Personal Information").
           - DEMAND: "Immediate removal of my data from 3rd party sharing lists."

        4. **Cancellation Friction**:
           - SUBJECT: "NOTICE OF TERMINATION: Effective Immediately"
           - BODY: "I am providing written notice of termination. Any further charges will be disputed with my bank as unauthorized."

        ### TONE INSTRUCTIONS:
        - Be FORMAL, FIRM, and AUTHORITATIVE.
        - Do not ask for permission; state the client's rights.
        - Use legal terms like "Material Breach," "Unconscionable," "Adhesion Contract," "Reservation of Rights" where appropriate.
        - Keep it under 150 words.
        """),
        ("user", """
        CLAUSE: "{trap_text}"
        CATEGORY: {category}
        ISSUE: {explanation}
        """)
    ])
    
    chain = negotiation_prompt | llm | parser
    try:
        return chain.invoke({
            "trap_text": trap_text,
            "category": category,
            "explanation": explanation
        })
    except Exception as e:
        print(f"Error generating negotiation email: {e}")
        return NegotiationResult(
            subject_line=f"Inquiry regarding {category} clause",
            email_body=f"To Whom It May Concern,\n\nI am writing to request clarification regarding the following clause in my contract:\n\n\"{trap_text}\"\n\nPlease provide a written explanation of this term or options for opting out.\n\nSincerely,\n[Your Name]"
        )
