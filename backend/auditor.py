from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import opik
import os

# Initialize Opik
os.environ["OPIK_PROJECT_NAME"] = "fine-print-xray"
opik.configure(use_local=False)

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
    
    # We invoke the chain
    result = chain.invoke({
        "contract_text": text,
        "format_instructions": parser.get_format_instructions()
    })
    
    return result
