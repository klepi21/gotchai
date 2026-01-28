from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import opik
import os

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
    try:
        opik.configure(use_local=True)
    except:
        pass

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
    - "Data Monetization": Permission to sell financial behavior.
    - "Liability Shifts": Making the user responsible for platform errors.
    - "Mandatory Arbitration / Class Action Waiver": Forcing users to waive their right to sue (Common in Banks/Gyms).
    - "Liquidated Damages": Excessive penalties for breaking the contract early.

### FEW-SHOT EXAMPLES (Validation Pattern)
Here are examples of how you should analyze text:

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
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    parser = PydanticOutputParser(pydantic_object=AuditResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "AUDIT THE FOLLOWING DOCUMENT:\n----------\n{contract_text}\n----------\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser
    return chain

@opik.track(name="contract_audit")
def analyze_contract_text(text: str) -> AuditResult:
    chain = get_auditor_chain()
    parser = PydanticOutputParser(pydantic_object=AuditResult)
    
    try:
        # We invoke the chain
        result = chain.invoke({
            "contract_text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"Error in audit chain: {e}")
        # Return visible error as a "Trap" so user sees it
        return AuditResult(
            detected_traps=[
                DetectionObject(
                    original_text="System Error",
                    risk_level="INFO",
                    category="System",
                    plain_english_explanation="The AI service is currently overloaded. Please wait 30 seconds and try again.",
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
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
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
