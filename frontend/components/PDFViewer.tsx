'use client';

import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { useAuditStore, Trap } from '@/store/auditStore';
import { clsx } from 'clsx';
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

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
            {/* 
               Remvoed internal headers/containers. 
               This component now just renders the PDF, style is controlled by parent.
            */}
            <Document
                file={file}
                onLoadSuccess={onDocumentLoadSuccess}
                className="flex flex-col gap-4"
                // Removed bg-gray-800 p-8 to allow Parent padding/bg to take over.
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

    if (!traps) return null;

    // Filter traps relevant to this page
    const pageTraps = traps.filter(t => t.pages.includes(pageNumber));

    return (
        <div className="absolute inset-0 pointer-events-none">
            {pageTraps.map((trap, i) => {
                // Find the first rectangle on this page to position the single tooltip
                // We use Filter just to be safe, though traps logic guarantees this.
                const firstRect = trap.coordinates[0];

                return (
                    <div key={i}>
                        {/* 1. RENDER HIGHLIGHTS (All Rects) */}
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

                        {/* 2. RENDER ONE SINGLE TOOLTIP (If Hovered) */}
                        {hoveredTrapIndex === i && firstRect && (
                            <div
                                className="absolute z-50 pointer-events-auto"
                                style={{
                                    left: `${firstRect[0] * scale}px`,
                                    top: `${firstRect[1] * scale}px`,
                                    transform: 'translateY(-105%) translateX(-10%)' // Position above and slightly centered
                                }}
                                onMouseEnter={() => setHoveredTrapIndex(i)} // Keep open if moving to tooltip
                                onMouseLeave={() => setHoveredTrapIndex(null)}
                            >
                                <div className="w-72 bg-[#111] text-white text-xs p-4 rounded-xl border border-neutral-800 shadow-2xl animate-in fade-in slide-in-from-bottom-2 duration-150">
                                    <div className="flex items-center justify-between mb-2">
                                        <p className="font-bold text-red-500 uppercase tracking-wider">{trap.category}</p>
                                        <span className="px-1.5 py-0.5 rounded bg-red-500/10 border border-red-500/20 text-[10px] text-red-500 font-bold">
                                            {trap.risk_level}
                                        </span>
                                    </div>
                                    <p className="text-neutral-300 leading-relaxed mb-3 text-[13px]">{trap.plain_english_explanation}</p>

                                    <div className="border-t border-white/10 pt-2 flex items-start gap-2">
                                        <div className="w-3 h-3 rounded-full bg-emerald-500/20 flex items-center justify-center mt-0.5">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                        </div>
                                        <p className="text-neutral-400 font-medium">To Fix: <span className="text-emerald-400">{trap.remediation}</span></p>
                                    </div>
                                </div>
                                {/* Tooltip Arrow */}
                                <div className="w-3 h-3 bg-[#111] border-b border-r border-neutral-800 transform rotate-45 absolute bottom-[-6px] left-6"></div>
                            </div>
                        )}
                    </div>
                )
            })}
        </div>
    );
}
