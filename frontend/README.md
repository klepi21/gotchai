# GotchAI Frontend 💎

The user interface for **GotchAI**, built to feel like a premium financial instrument ("Revolut for Contracts").

## ✨ Features

- **Glassmorphism Design**: Multi-layered transparency and blurs for a modern, high-tech feel.
- **Real-Time Analysis**: Streamed status updates from the AI backend via WebSocket-like polling.
- **Interactive PDF Viewer**: Highlights "Traps" directly on the document using coordinate mapping from the backend.
- **"Fight This" Generator**: One-click generation of legally grounded negotiation emails.
- **Responsive**: Fully optimized for Desktop and Tablet auditing.

## 🛠️ Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS + Custom "Glass" Utilities
- **UI Library**: Shadcn/UI (Radix Primitives)
- **Icons**: Lucide React
- **Animations**: Framer Motion

## 🚀 Development

```bash
npm install
npm run dev
```

The app will connect to the backend at `http://localhost:8005`.
Ensure the backend is running before uploading a document!
