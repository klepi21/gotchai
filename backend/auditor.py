from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import opik
import os
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
    # Prevent interactive prompts in production
    # try:
    #     opik.configure(use_local=True)
    # except:
    #     pass

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
2. TRAP DETECTION: Look for:
    - "Zombie Fees": Hidden recurring charges.
    - "Arbitrary Price Hikes": Clauses allowing the company to change rates without notice.
    - "The Friction Trap": Excessive requirements for cancellation.
    - "Data Monetization": Permission to sell financial behavior (CRITICAL).
    - "Data Sovereignty/Location": Storage in lower-privacy jurisdictions (CAUTION).
    - "Liability Shifts": Making the user responsible for platform errors.
    - "Mandatory Arbitration / Class Action Waiver": Forcing users to waive their right to sue (Common in Banks/Gyms).
    - "Liquidated Damages": Excessive penalties for breaking the contract early.

### FEW-SHOT EXAMPLES (Validation Pattern)
Here are examples of how you should analyze text:

Input: "We reserve the right to share your transaction history with unnamed affiliate partners."
Analysis:
{{
    "original_text": "We reserve the right to share your transaction history with unnamed affiliate partners.",
    "risk_level": "CRITICAL",
    "category": "Privacy",
    "plain_english_explanation": "They can sell your private bank data to strangers for profit.",
    "estimated_cost_impact": "Privacy Breach/Targeted Ads",
    "remediation": "Opt-out of data sharing immediately."
}}

Input: "Your data is stored in servers located in jurisdictions with lower privacy standards."
Analysis:
{{
    "original_text": "Your data is stored in servers located in jurisdictions with lower privacy standards.",
    "risk_level": "CAUTION",
    "category": "Privacy",
    "plain_english_explanation": "Your data is stored in a country with weaker privacy laws, but they aren't explicitly selling it.",
    "estimated_cost_impact": "Low (hypothetical risk)",
    "remediation": "Ask for data residency options."
}}

Input: "The monthly subscription fee is $9.99. We reserve the right to change this fee at any time without prior notice."
Analysis:
{{
    "original_text": "We reserve the right to change this fee at any time without prior notice.",
    "risk_level": "CRITICAL",
    "category": "Hidden Fees",
    "plain_english_explanation": "They can raise your price whenever they want, and they don't even have to tell you first.",
    "estimated_cost_impact": "Unlimited potential increase",
    "remediation": "Ask for a 'fixed price guarantee' for the first 12 months."
}}

Input: "To cancel, send a certified letter to our headquarters in Caymans."
Analysis:
{{
    "original_text": "To cancel, send a certified letter to our headquarters in Caymans.",
    "risk_level": "CAUTION",
    "category": "Contract Length",
    "plain_english_explanation": "They make it incredibly hard to cancel by forcing you to mail a physical letter internationally.",
    "estimated_cost_impact": "High (Travel/Postage + Unwanted renewal)",
    "remediation": "Demand an online cancellation option or email termination rights."
}}

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
    # Use Gemini 1.5 Flash for high speed and low latency
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    parser = PydanticOutputParser(pydantic_object=AuditResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "AUDIT THE FOLLOWING DOCUMENT:\n----------\n{contract_text}\n----------\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser
    return chain

@opik.track(name="contract_audit")
def analyze_contract_text(text: str) -> AuditResult:
    # Use Gemini 1.5 Flash (via get_auditor_chain default)
    chain = get_auditor_chain()
    parser = PydanticOutputParser(pydantic_object=AuditResult)
    
    # Simple Retry Logic for network blips
    MAX_RETRIES = 2
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🤖 Analyzing with Gemini 1.5 Flash (Attempt {attempt+1})...")
            
            # We invoke the chain
            result = chain.invoke({
                "contract_text": text,
                "format_instructions": parser.get_format_instructions()
            })
            
            # --- DETERMINISTIC SCORING ALGORITHM ---
            # Instead of relying on the LLM to hallucinate a score, we calculate it mathematically
            # based on the findings. This ensures consistency (e.g., same traps = same score).
            
            calculated_score = 0
            for trap in result.detected_traps:
                risk = trap.risk_level.upper()
                if "CRITICAL" in risk:
                    calculated_score += 25
                elif "CAUTION" in risk:
                    calculated_score += 10
                else:
                    calculated_score += 2
            
            # Cap score at 100
            result.overall_predatory_score = min(calculated_score, 100)
            
            return result

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            if attempt == MAX_RETRIES - 1:
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
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
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
