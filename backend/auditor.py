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

# --- Async Chains ---
def get_auditor_chain():
    # Use Grok 3 Mini (xAI) via OpenAI SDK
    llm = ChatOpenAI(
        model="grok-3-mini",
        openai_api_key=os.getenv("XAI_API_KEY"),
        openai_api_base="https://api.x.ai/v1",
        temperature=0
    )
    parser = PydanticOutputParser(pydantic_object=AuditResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "AUDIT THE FOLLOWING SEGMENT:\n----------\n{contract_text}\n----------\n\n{format_instructions}")
    ])

    # Convert to async runnable
    chain = prompt | llm | parser
    return chain

import asyncio

@opik.track(name="contract_audit_async")
async def analyze_contract_text(text: str) -> AuditResult:
    """
    Asynchronously analyzes contract text in parallel chunks to reduce latency.
    """
    chain = get_auditor_chain()
    parser = PydanticOutputParser(pydantic_object=AuditResult)
    
    # 1. Chunking Strategy
    # Overlap avoids cutting a clause in half
    CHUNK_SIZE = 6000
    OVERLAP = 500
    
    chunks = []
    if len(text) <= CHUNK_SIZE:
        chunks.append(text)
    else:
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            # Extend to nearest newline if possible to avoid clean cuts
            if end < len(text):
                 next_newline = text.find('\n', end)
                 if next_newline != -1 and next_newline - end < 200:
                     end = next_newline
            
            chunks.append(text[start:end])
            start = end - OVERLAP
            
    print(f"🚀 Splitting document into {len(chunks)} parallel parallel chunks...")

    # 2. Define Async Task
    async def process_chunk(chunk_text, index):
        try:
            # print(f"Processing chunk {index+1}/{len(chunks)}...")
            result = await chain.ainvoke({
                "contract_text": chunk_text,
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"⚠️ Chunk {index+1} failed: {e}")
            return None

    # 3. Execute in Parallel
    tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    
    # 4. Merge Results
    all_traps = []
    total_score = 0
    
    valid_results = [r for r in results if r is not None]
    
    if not valid_results:
         # Fallback if everything failed
         return AuditResult(detected_traps=[], overall_predatory_score=0)
         
    seen_texts = set()
    
    for res in valid_results:
        # Avoid duplicate traps (from overlaps)
        for trap in res.detected_traps:
            # Simple dedup by exact text + category
            dedup_key = f"{trap.original_text[:20]}-{trap.category}"
            if dedup_key not in seen_texts:
                all_traps.append(trap)
                seen_texts.add(dedup_key)
                
                # Add to score
                risk = trap.risk_level.upper()
                if "CRITICAL" in risk: total_score += 20
                elif "CAUTION" in risk: total_score += 5
                else: total_score += 1
    
    # Cap score
    overall_score = min(total_score, 100)
    
    return AuditResult(detected_traps=all_traps, overall_predatory_score=overall_score)
    
class NegotiationResult(BaseModel):
    subject_line: str = Field(description="A formal, punchy subject line for the email")
    email_body: str = Field(description="The body of the email. Formal but firm.")

def generate_negotiation_email(trap_text: str, category: str, explanation: str) -> NegotiationResult:
    llm = ChatOpenAI(
        model="grok-3-mini",
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
