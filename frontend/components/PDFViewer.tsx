import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { useAuditStore, Trap } from '@/store/auditStore';
import { clsx } from 'clsx';
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import { Copy, X, Loader2, Zap } from 'lucide-react';

// Configure worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function PDFViewer() {
    const { file, analysisResult } = useAuditStore();
    const [numPages, setNumPages] = useState<number>(0);
    const [scale, setScale] = useState(1.2);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages);
    }

    return (
        <div className="w-full h-full flex justify-center">
            <Document
                file={file}
                onLoadSuccess={onDocumentLoadSuccess}
                className="flex flex-col gap-4"
                loading={<div className="text-neutral-500 p-10">Loading Document...</div>}
            >
                {Array.from(new Array(numPages), (el, index) => (
                    <div key={`page_wrapper_${index + 1}`} className="relative">
                        <Page
                            key={`page_${index + 1}`}
                            pageNumber={index + 1}
                            scale={scale}
                            className="shadow-lg"
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                        />

                        {/* Heatmap Overlay */}
                        <OverlayLayer pageNumber={index + 1} scale={scale} traps={analysisResult?.detected_traps} />
                    </div>
                ))}
            </Document>
        </div>
    );
}

function OverlayLayer({ pageNumber, scale, traps }: { pageNumber: number, scale: number, traps?: Trap[] }) {
    const [hoveredTrapIndex, setHoveredTrapIndex] = useState<number | null>(null);
    const [negotiationData, setNegotiationData] = useState<{ subject: string, body: string } | null>(null);
    const [isNegotiating, setIsNegotiating] = useState(false);
    const [activeTrapId, setActiveTrapId] = useState<number | null>(null); // To show spinner on specific button

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

    if (!traps) return null;

    // Filter traps relevant to this page
    const pageTraps = traps.filter(t => t.pages.includes(pageNumber));

    return (
        <>
            <div className="absolute inset-0 pointer-events-none">
                {pageTraps.map((trap, i) => {
                    const firstRect = trap.coordinates[0];
                    const isProcessingThis = isNegotiating && activeTrapId === i;

                    return (
                        <div key={i}>
                            {/* 1. RENDER HIGHLIGHTS */}
                            {trap.coordinates.map((rect, j) => (
                                <div
                                    key={`${i}-${j}`}
                                    className={clsx(
                                        "absolute transition-colors cursor-help pointer-events-auto",
                                        hoveredTrapIndex === i ? "bg-red-500/40 border-red-500" : "bg-red-500/20 border-red-500/50",
                                        "border-2"
                                    )}
                                    style={{
                                        left: `${rect[0] * scale}px`,
                                        top: `${rect[1] * scale}px`,
                                        width: `${rect[2] * scale}px`,
                                        height: `${rect[3] * scale}px`,
                                    }}
                                    onMouseEnter={() => setHoveredTrapIndex(i)}
                                    onMouseLeave={() => setHoveredTrapIndex(null)}
                                />
                            ))}

                            {/* 2. RENDER TOOLTIP */}
                            {hoveredTrapIndex === i && firstRect && (
                                <div
                                    className="absolute z-50 pointer-events-auto"
                                    style={{
                                        left: `${firstRect[0] * scale}px`,
                                        top: `${firstRect[1] * scale}px`,
                                        transform: 'translateY(-105%) translateX(-10%)'
                                    }}
                                    onMouseEnter={() => setHoveredTrapIndex(i)}
                                    onMouseLeave={() => setHoveredTrapIndex(null)}
                                >
                                    <div className="w-80 bg-[#111111] text-white text-xs p-4 rounded-xl border border-neutral-800 shadow-2xl animate-in fade-in slide-in-from-bottom-2 duration-150 ring-1 ring-white/10">
                                        <div className="flex items-center justify-between mb-2">
                                            <p className="font-bold text-red-500 uppercase tracking-wider">{trap.category}</p>
                                            <span className="px-1.5 py-0.5 rounded bg-red-500/10 border border-red-500/20 text-[10px] text-red-500 font-bold">
                                                {trap.risk_level}
                                            </span>
                                        </div>
                                        <p className="text-neutral-300 leading-relaxed mb-3 text-[13px]">{trap.plain_english_explanation}</p>

                                        <div className="border-t border-white/10 pt-3 flex items-center justify-between gap-2">
                                            <div className="flex items-center gap-2">
                                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                                <span className="text-neutral-400 font-medium text-[10px]">Tap to fix</span>
                                            </div>

                                            <button
                                                onClick={() => handleNegotiate(trap, i)}
                                                disabled={isNegotiating}
                                                className="group flex items-center gap-2 bg-white text-black px-3 py-1.5 rounded-lg font-bold hover:bg-neutral-200 transition-colors disabled:opacity-50"
                                            >
                                                {isProcessingThis ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3 fill-current" />}
                                                {isProcessingThis ? "Writing..." : "Fight This"}
                                            </button>
                                        </div>
                                    </div>
                                    <div className="w-3 h-3 bg-[#111111] border-b border-r border-neutral-800 transform rotate-45 absolute bottom-[-6px] left-6 ring-1 ring-white/10 ring-t-0 ring-l-0"></div>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            {/* 3. NEGOTIATION MODAL */}
            {negotiationData && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden ring-1 ring-white/10">
                        {/* Header */}
                        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-[#111]">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                                    <Zap className="w-5 h-5 text-blue-500 fill-current" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white">Auto-Negotiator</h3>
                                    <p className="text-neutral-500 text-xs">AI-generated legal opt-out script</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setNegotiationData(null)}
                                className="p-2 hover:bg-white/5 rounded-full transition-colors text-neutral-400 hover:text-white"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-8 space-y-6">
                            <div>
                                <label className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-2 block">Subject Line</label>
                                <div className="flex items-center gap-2 bg-neutral-900/50 p-3 rounded-lg border border-white/5">
                                    <span className="text-white font-medium flex-1 select-all">{negotiationData.subject}</span>
                                    <button
                                        onClick={() => navigator.clipboard.writeText(negotiationData.subject)}
                                        className="p-2 text-neutral-500 hover:text-white transition-colors"
                                        title="Copy Subject"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-2 block">Email Body</label>
                                <div className="relative group">
                                    <textarea
                                        readOnly
                                        className="w-full h-64 bg-neutral-900/50 p-4 rounded-xl border border-white/5 text-neutral-300 leading-relaxed resize-none focus:outline-none focus:ring-1 focus:ring-blue-500/50 custom-scrollbar"
                                        value={negotiationData.body}
                                    />
                                    <button
                                        onClick={() => navigator.clipboard.writeText(negotiationData.body)}
                                        className="absolute top-4 right-4 p-2 bg-black/50 backdrop-blur border border-white/10 rounded-lg text-neutral-400 hover:text-white opacity-0 group-hover:opacity-100 transition-all hover:scale-105"
                                        title="Copy Body"
                                    >
                                        <Copy className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 bg-[#111] border-t border-white/5 flex justify-end">
                            <button
                                onClick={() => {
                                    navigator.clipboard.writeText(`${negotiationData.subject}\n\n${negotiationData.body}`);
                                    alert("Copied entire email to clipboard!");
                                }}
                                className="bg-white text-black px-6 py-2 rounded-lg font-bold hover:bg-neutral-200 transition-colors flex items-center gap-2"
                            >
                                <Copy className="w-4 h-4" />
                                Copy Everything
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
