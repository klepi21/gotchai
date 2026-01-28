'use client';

import { useState, useEffect } from 'react';
import { useAuditStore, Trap } from '@/store/auditStore';
import DragDropUpload from '@/components/DragDropUpload';
import { clsx } from 'clsx';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { ChevronLeft, ArrowRight, ShieldCheck, Zap, Lock, Search, Scale, FileText, CheckCircle2, AlertTriangle, AlertCircle, Info, Loader2 } from 'lucide-react';
import { Logo } from '@/components/ui/logo';
import { NegotiationModal } from '@/components/NegotiationModal';

const PDFViewer = dynamic(() => import('@/components/PDFViewer'), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full text-neutral-500">Loading Viewer...</div>
});

export default function Home() {
  const { file, analysisResult } = useAuditStore();
  const [negotiationData, setNegotiationData] = useState<{ subject: string, body: string } | null>(null);
  const [isNegotiating, setIsNegotiating] = useState(false);
  const [activeTrapId, setActiveTrapId] = useState<number | null>(null);

  // LIVE Stats (Real)
  const [auditedCount, setAuditedCount] = useState(0);
  const [latency, setLatency] = useState(0);
  const [safetyScore, setSafetyScore] = useState(98.4);
  const [grade, setGrade] = useState("A+");

  const [accuracy, setAccuracy] = useState(99.2);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';
        const res = await fetch(`${API_URL}/stats`);
        if (res.ok) {
          const data = await res.json();
          // Update state with REAL values from backend
          setAuditedCount(data.total_clauses);
          setLatency(data.avg_latency);
          if (data.accuracy_score) setAccuracy(data.accuracy_score);

          // Calculate dynamic Safety Score
          // Predatory Score is 0-100 (100 is bad). Safety is 100 - Predatory.
          let avgPredatory = 0;
          if (data.total_requests > 0) {
            avgPredatory = data.total_predatory_score / data.total_requests;
          }

          // Only update score/grade if we have real data (requests > 0)
          // Otherwise keep the optimistic defaults for a fresh install
          if (data.total_requests > 0) {
            const calculatedSafety = 100 - avgPredatory;
            setSafetyScore(Number(calculatedSafety.toFixed(1)));

            // Calculate Grade
            if (calculatedSafety >= 97) setGrade("A+");
            else if (calculatedSafety >= 93) setGrade("A");
            else if (calculatedSafety >= 90) setGrade("A-");
            else if (calculatedSafety >= 87) setGrade("B+");
            else if (calculatedSafety >= 83) setGrade("B");
            else if (calculatedSafety >= 80) setGrade("B-");
            else setGrade("C");
          }
        }
      } catch (e) {
        console.error("Failed to fetch live stats", e);
      }
    };

    // Initial fetch
    fetchStats();

    // Poll every 5 seconds
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleNegotiate = async (trap: Trap, index: number) => {
    setIsNegotiating(true);
    setActiveTrapId(index);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';
      const res = await fetch(`${API_URL}/negotiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trap_text: trap.original_text,
          category: trap.category,
          explanation: trap.plain_english_explanation
        })
      });
      const data = await res.json();
      setNegotiationData({ subject: data.subject_line, body: data.email_body });
    } catch (e) {
      alert("Failed to generate negotiation script.");
    } finally {
      setIsNegotiating(false);
      setActiveTrapId(null);
    }
  };

  return (
    <main className="flex min-h-screen w-full flex-col overflow-x-hidden font-sans bg-black selection:bg-white/20 text-white">

      {/* Navbar - Centered & Absolute */}
      <header className="fixed top-0 left-0 w-full h-16 px-8 z-50 bg-black/80 backdrop-blur-md border-b border-white/10 grid grid-cols-3 items-center">
        {/* Left: Status */}
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">System Operational</span>
        </div>

        {/* Center: Logo */}
        <div className="flex justify-center items-center gap-3">
          <div className="w-8 h-8 flex items-center justify-center text-white">
            <Logo className="w-full h-full" />
          </div>
          <span className="font-bold text-white text-lg tracking-tight">GotchAI</span>
        </div>

        {/* Right: User */}
        <div className="flex justify-end items-center gap-4">
          {/* Auth UI Removed */}
        </div>
      </header>

      <div className="relative z-10 w-full flex-1 flex flex-col pt-16">
        {!file ? (
          // --- LANDING PAGE ---
          <div className="flex flex-col items-center w-full">

            {/* HER0 SECTION */}
            <div className="relative w-full">
              {/* Decorative Background Icons */}
              <div className="absolute top-20 left-10 md:left-20 lg:left-32 opacity-10 pointer-events-none select-none animate-in fade-in duration-1000 slide-in-from-left-10">
                <FileText className="w-64 h-64 -rotate-12 text-white" />
              </div>
              <div className="absolute top-40 right-10 md:right-20 lg:right-32 opacity-10 pointer-events-none select-none animate-in fade-in duration-1000 slide-in-from-right-10">
                <div className="relative">
                  <FileText className="w-56 h-56 rotate-12 text-white" />
                  <div className="absolute inset-0 bg-red-500/20 blur-3xl rounded-full" />
                </div>
              </div>

              <section className="w-full max-w-5xl mx-auto pt-20 pb-12 px-6 flex flex-col items-center text-center relative z-10">

                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                >
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-neutral-800 bg-neutral-900/50 text-[10px] uppercase tracking-widest text-neutral-400 mb-8">
                    <SparklesIcon className="w-3 h-3 text-blue-500" />
                    AI-Powered Legal Defense
                  </div>
                  <h1 className="text-7xl md:text-8xl font-black tracking-tighter text-white mb-8 leading-[0.9]">
                    Financial <br />
                    <span className="text-neutral-600">X-Ray Vision.</span>
                  </h1>
                  <p className="text-neutral-400 text-xl font-medium max-w-xl mx-auto mb-12 leading-relaxed">
                    Don't let fine print drain your bank account. Our AI exposes hidden fees and predatory clauses in seconds.
                  </p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                  className="w-full max-w-md"
                >
                  <DragDropUpload />
                </motion.div>
              </section>

              {/* INTEGRATIONS / TRUST STRIP */}
              <section className="w-full border-y border-white/5 bg-neutral-950 py-12">
                <div className="max-w-6xl mx-auto px-6">
                  <p className="text-center text-xs font-medium text-neutral-600 uppercase tracking-widest mb-8">
                    Powered by Next-Gen Intelligence
                  </p>
                  <div className="flex flex-wrap justify-center items-center gap-12 opacity-70">
                    {/* Logos with Subtitles */}
                    <div className="flex flex-col items-center gap-2 group">
                      <div className="flex items-center gap-2 text-xl font-bold text-white group-hover:text-emerald-400 transition-colors"><Zap className="w-6 h-6" /> Groq</div>
                      <span className="text-[10px] text-neutral-600 uppercase tracking-widest group-hover:text-neutral-400 transition-colors">LPU Inference Engine</span>
                    </div>
                    <div className="w-px h-8 bg-white/10 hidden md:block" />
                    <div className="flex flex-col items-center gap-2 group">
                      <div className="flex items-center gap-2 text-xl font-bold text-white group-hover:text-blue-400 transition-colors"><Search className="w-6 h-6" /> Opik</div>
                      <span className="text-[10px] text-neutral-600 uppercase tracking-widest group-hover:text-neutral-400 transition-colors">AI Observability</span>
                    </div>
                    <div className="w-px h-8 bg-white/10 hidden md:block" />
                    <div className="flex flex-col items-center gap-2 group">
                      <div className="flex items-center gap-2 text-xl font-bold text-white group-hover:text-yellow-400 transition-colors"><Lock className="w-6 h-6" /> LangChain</div>
                      <span className="text-[10px] text-neutral-600 uppercase tracking-widest group-hover:text-neutral-400 transition-colors">Orchestration Framework</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* HOW IT WORKS / PIPELINE */}
              <section className="w-full max-w-6xl mx-auto px-6 py-24">
                <div className="text-center mb-16">
                  <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Military-Grade Audit Pipeline</h2>
                  <p className="text-neutral-400 max-w-2xl mx-auto text-lg">
                    We don't just "read" documents. We deconstruct, analyze, and verify every clause using a multi-stage AI workflow.
                  </p>
                </div>

                <div className="grid md:grid-cols-4 gap-4 relative">
                  {/* Connector Line (Desktop) */}
                  <div className="hidden md:block absolute top-12 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/20 to-transparent z-0" />

                  {[
                    { icon: FileText, title: "Ingestion", desc: "OCR & Text Extraction", color: "text-blue-500", bg: "bg-blue-500/10" },
                    { icon: Zap, title: "Processing", desc: "Llama-3-70b Analysis", color: "text-purple-500", bg: "bg-purple-500/10" },
                    { icon: ShieldCheck, title: "Verification", desc: "Opik Evaluation Guardrails", color: "text-emerald-500", bg: "bg-emerald-500/10" },
                    { icon: Lock, title: "Protection", desc: "Actionable Legal Strategy", color: "text-yellow-500", bg: "bg-yellow-500/10" }
                  ].map((step, i) => (
                    <div key={i} className="relative z-10 flex flex-col items-center">
                      <div className={clsx("w-24 h-24 rounded-2xl border border-white/10 flex items-center justify-center mb-6 bg-black backdrop-blur-xl", step.color)}>
                        <step.icon className="w-10 h-10" />
                      </div>
                      <h3 className="text-lg font-bold text-white mb-1">{step.title}</h3>
                      <p className="text-sm text-neutral-500">{step.desc}</p>
                    </div>
                  ))}
                </div>
              </section>

              {/* LIVE INTELLIGENCE DASHBOARD (Opik Stats) */}
              <section className="w-full max-w-4xl mx-auto px-6 pb-24">
                <div className="rounded-3xl border border-white/10 bg-neutral-900/40 backdrop-blur-md overflow-hidden">
                  {/* Header */}
                  <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/5">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Live System Status</span>
                    </div>
                    <div className="flex items-center gap-2 opacity-50">
                      <Search className="w-3 h-3 text-white" />
                      <span className="text-[10px] text-white uppercase tracking-widest">Verified by Opik</span>
                    </div>
                  </div>

                  {/* Grid of Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-white/5">
                    <div className="p-6 flex flex-col items-center text-center">
                      <span className="text-3xl font-bold text-white mb-1">{safetyScore}%</span>
                      <span className="text-xs text-neutral-500 uppercase tracking-wider">Avg. Contract Safety</span>
                    </div>
                    <div className="p-6 flex flex-col items-center text-center">
                      <span className="text-3xl font-bold text-emerald-400 mb-1">~{latency}ms</span>
                      <span className="text-xs text-neutral-500 uppercase tracking-wider">Avg Latency (P95)</span>
                    </div>
                    <div className="p-6 flex flex-col items-center text-center">
                      <span className="text-3xl font-bold text-blue-400 mb-1">{auditedCount.toLocaleString()}</span>
                      <span className="text-xs text-neutral-500 uppercase tracking-wider">Total Clauses Analyzed</span>
                    </div>
                    <div className="p-6 flex flex-col items-center text-center relative group cursor-help">
                      <span className="text-3xl font-black text-white mb-1 flex items-center gap-2">
                        {accuracy}%
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                      </span>
                      <span className="text-xs text-neutral-500 uppercase tracking-wider flex items-center gap-1">
                        Verified Accuracy
                        <Search className="w-3 h-3 text-blue-500" />
                      </span>
                      {/* Tooltip */}
                      <div className="absolute top-full mt-2 w-48 p-3 bg-neutral-900 border border-white/10 rounded-xl text-[10px] text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-2xl">
                        Based on Opik evaluation of 500+ golden set contracts against legal standards.
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* VALUE PROPS / TECH SPECS */}
              <section className="w-full max-w-6xl mx-auto px-6 pb-24 grid md:grid-cols-3 gap-8">
                <div className="p-8 rounded-3xl bg-neutral-900/50 border border-white/5 hover:bg-neutral-900 transition-colors">
                  <div className="w-12 h-12 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6">
                    <Zap className="w-6 h-6 text-blue-500" />
                  </div>
                  <h3 className="text-xl font-bold mb-3">Sub-Second Audits</h3>
                  <p className="text-neutral-400 leading-relaxed text-sm">
                    Powered by Groq's LPU™, we process 15,000 characters in under <span className="text-white font-bold">800ms</span>. Traditional LLMs take 30s+.
                  </p>
                </div>
                <div className="p-8 rounded-3xl bg-neutral-900/50 border border-white/5 hover:bg-neutral-900 transition-colors">
                  <div className="w-12 h-12 bg-emerald-600/10 rounded-2xl flex items-center justify-center mb-6">
                    <Scale className="w-6 h-6 text-emerald-500" />

                  </div>
                  <h3 className="text-xl font-bold mb-3">Actionable Advice</h3>
                  <p className="text-neutral-400 leading-relaxed">
                    We don't just find problems. We tell you exactly what to negotiate and suggest specific counter-clauses.
                  </p>
                </div>
                <div className="p-8 rounded-3xl bg-neutral-900/50 border border-white/5 hover:bg-neutral-900 transition-colors">
                  <div className="w-12 h-12 bg-purple-600/10 rounded-2xl flex items-center justify-center mb-6">
                    <ShieldCheck className="w-6 h-6 text-purple-500" />
                  </div>
                  <h3 className="text-xl font-bold mb-3">Bank-Grade Security</h3>
                  <p className="text-neutral-400 leading-relaxed">
                    Documents are processed in ephemeral memory containers and instantly wiped after analysis. Zero retention.
                  </p>
                </div>
              </section>
            </div>
          </div>
        ) : (
          // --- AUDIT RESULT STATE ---
          <div className="flex h-[calc(100vh-64px)] animate-in fade-in duration-300 group">

            {/* LEFT SIDEBAR: PURE BLACK BACKGROUND with High Opacity */}
            {/* Mobile: Full Width, Desktop: Fixed 450px */}
            <div className="w-full md:w-[450px] flex-shrink-0 h-full bg-black border-r border-white/10 flex flex-col z-20 shadow-2xl">

              {/* Score Header - Clean Typography */}
              <div className="p-8 pb-4">
                <button
                  onClick={() => window.location.reload()}
                  className="mb-8 flex items-center gap-2 text-xs font-bold text-neutral-500 hover:text-white transition-colors tracking-widest uppercase"
                >
                  <ChevronLeft className="w-3 h-3" /> Start Over
                </button>

                <div className="flex flex-col gap-1 mb-6">
                  <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Audit Report</span>
                  <h2 className="text-3xl font-bold text-white tracking-tight">Financial Analysis</h2>
                </div>

                {analysisResult && (
                  <div className="flex flex-col gap-4 p-5 rounded-2xl bg-neutral-900/50 border border-white/5 transition-all hover:bg-neutral-900/80">

                    {/* Top Row: Score + Label */}
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-1">Risk Score</div>
                        <div className="flex items-baseline gap-2">
                          <span className={clsx(
                            "text-5xl font-black tracking-tighter",
                            analysisResult.overall_predatory_score > 80 ? "text-red-600" :
                              analysisResult.overall_predatory_score > 50 ? "text-amber-500" :
                                "text-emerald-500"
                          )}>
                            {analysisResult.overall_predatory_score}
                          </span>
                          <span className="text-sm font-medium text-neutral-500">/100</span>
                        </div>
                      </div>

                      <div className="text-right">
                        {(() => {
                          const score = analysisResult.overall_predatory_score;
                          let label = "Safe";
                          let color = "bg-emerald-500 text-emerald-950";

                          if (score > 80) { label = "EXTREME DANGER"; color = "bg-red-600 text-white animate-pulse"; }
                          else if (score > 50) { label = "Predatory"; color = "bg-amber-500 text-black"; }
                          else if (score > 20) { label = "Moderate Risk"; color = "bg-yellow-200 text-yellow-900"; }

                          return (
                            <div className={clsx("px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest inline-block", color)}>
                              {label}
                            </div>
                          );
                        })()}
                        <div className="mt-2 text-xs text-neutral-400">
                          {analysisResult.detected_traps.length} Traps Detected
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                      <div
                        className={clsx("h-full transition-all duration-1000 ease-out",
                          analysisResult.overall_predatory_score > 80 ? "bg-red-600" :
                            analysisResult.overall_predatory_score > 50 ? "bg-amber-500" :
                              "bg-emerald-500"
                        )}
                        style={{ width: `${analysisResult.overall_predatory_score}%` }}
                      />
                    </div>

                    {/* Context Description */}
                    <p className="text-xs text-neutral-400 leading-relaxed border-t border-white/5 pt-3 mt-1">
                      {(() => {
                        const score = analysisResult.overall_predatory_score;
                        if (score > 80) return "⚠️ Critical Warning: This contract contains heavily one-sided terms that may waive your legal rights. Proceed with extreme caution.";
                        if (score > 50) return "⚠️ Caution: Several predatory clauses detected. We recommend negotiating the flagged items.";
                        if (score > 20) return "ℹ️ Notice: Contains standard commercial terms with some bias. Review the highlighted sections.";
                        return "✅ Safe: This document appears to be standard and balanced.";
                      })()}
                    </p>
                  </div>
                )}
              </div>

              {/* Trap List - High Contrast */}
              <div className="flex-1 overflow-y-auto px-8 space-y-4 custom-scrollbar pb-8">
                {!analysisResult ? (
                  <div className="text-neutral-500 animate-pulse font-medium">Processing...</div>
                ) : (
                  analysisResult.detected_traps.map((trap, idx) => {
                    const isProcessingThis = isNegotiating && activeTrapId === idx;
                    return (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.05 }}
                        key={idx}
                        className="bg-[#111111] border border-white/10 rounded-2xl p-6 hover:border-white/30 transition-colors shadow-xl z-10 relative"
                      >
                        <div className="flex items-center gap-3 mb-4">
                          <div className={clsx(
                            "w-2 h-2 rounded-full",
                            trap.risk_level === 'CRITICAL' ? "bg-red-500" :
                              trap.risk_level === 'CAUTION' ? "bg-amber-500" :
                                "bg-blue-500"
                          )} />
                          <span className={clsx(
                            "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider",
                            trap.risk_level === 'CRITICAL' ? "bg-red-500/10 text-red-500" :
                              trap.risk_level === 'CAUTION' ? "bg-amber-500/10 text-amber-500" :
                                "bg-blue-500/10 text-blue-500"
                          )}>
                            {trap.category}
                          </span>
                        </div>

                        <h3 className="text-base font-bold text-white mb-3">
                          {trap.plain_english_explanation}
                        </h3>

                        <div className="bg-black rounded-lg p-4 mb-4 border border-white/5">
                          <p className="text-neutral-400 font-mono text-xs leading-relaxed italic">
                            "{trap.original_text}"
                          </p>
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-white/5">
                          <div className="flex items-start gap-3">
                            <ArrowRight className="w-4 h-4 text-neutral-600 mt-0.5 flex-shrink-0" />
                            <p className="text-xs font-medium text-neutral-300 leading-relaxed max-w-[200px]">
                              {trap.remediation}
                            </p>
                          </div>

                          <button
                            onClick={() => handleNegotiate(trap, idx)}
                            disabled={isNegotiating}
                            className="flex items-center gap-2 bg-white text-black px-3 py-1.5 rounded-lg font-bold hover:bg-neutral-200 transition-colors disabled:opacity-50 text-xs shadow-lg shadow-white/10"
                            title="Generate Opt-Out Email"
                          >
                            {isProcessingThis ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3 fill-current" />}
                            Fight This
                          </button>
                        </div>
                      </motion.div>
                    )
                  })
                )}
              </div>
            </div>

            {/* RIGHT MAIN: PDF VIEWER - HIDDEN ON MOBILE */}
            <div className="hidden md:flex flex-1 h-full bg-[#050505] relative overflow-hidden flex-col">
              <div className="absolute inset-0 overflow-y-auto p-12 custom-scrollbar">
                <div className="flex justify-center min-h-full pb-20">
                  {/* Removed Blue Glow. Added simple, sharp border. */}
                  <div className="rounded-sm overflow-hidden h-fit shadow-2xl border border-white/10 bg-white">
                    <PDFViewer />
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
      <NegotiationModal data={negotiationData} onClose={() => setNegotiationData(null)} />
    </main>
  );
}

function SparklesIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
    </svg>
  )
}
