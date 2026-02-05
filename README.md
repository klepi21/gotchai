# GotchAI: Stop Signing Things You Haven't Read. �️

**We all do it. You see a 50-page "Terms and Conditions" wall of text, and you just click "Agree" because you have a life. GotchAI reads that wall for you and spots the traps in about 1000ms.**

---

## 🛑 The Problem: You're being tricked.
Most contracts are written by lawyers to protect companies, not you. They hide things like hidden fees, weird cancellation rules, and clauses that say you can't even sue them if they mess up. You shouldn't need to spend $300 an hour on a lawyer just to sign up for a gym or a lease.

## 🛡️ The Solution: GotchAI.
I built this to give regular people a fighting chance. You drop in a PDF or take a photo of a paper contract, and the app tells you exactly what's wrong with it. No legal jargon—just real talk about where you're at risk.

---

## ⚡ How I Built This
I didn't want this to be another "nice" AI that just summarizes things. I wanted it to be a skeptic.

*   **The Brain:** I'm using **Grok 4.1 Fast**. I tuned it to be paranoid—it assumes the contract is trying to screw you over, and its job is to find out how.
*   **The Gut Check:** I used **Opik** to actually test the AI. I fed it a bunch of "Golden Traps" (real predatory clauses) to make sure it was actually catching them. It's sitting at **93.3% accuracy** right now.
*   **Vision:** If you have a physical contract, just snap a photo. The OCR reads the text (even if the photo is a bit shaky) and analyzes it instantly.
*   **The "Fight Back" Button:** This is my favorite part. Once it finds a bad clause, you click one button and the app writes a firm, professional email for you to send back to the company to dispute it.

---

## �️ Get it running locally

### 1. The Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Put your XAI_API_KEY in .env
uvicorn main:app --reload --port 8005
```

### 2. The Frontend
```bash
cd frontend
npm install && npm run dev
```

Visit `http://localhost:3000` and start auditing. ✨

---

*Built for the 2026 AI Hackathon because I'm tired of bad contracts.*

