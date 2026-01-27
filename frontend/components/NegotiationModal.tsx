'use client';

import { Copy, X, Zap } from 'lucide-react';

interface NegotiationModalProps {
    data: { subject: string; body: string } | null;
    onClose: () => void;
}

export function NegotiationModal({ data, onClose }: NegotiationModalProps) {
    if (!data) return null;

    return (
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
                        onClick={onClose}
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
                            <span className="text-white font-medium flex-1 select-all">{data.subject}</span>
                            <button
                                onClick={() => navigator.clipboard.writeText(data.subject)}
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
                                value={data.body}
                            />
                            <button
                                onClick={() => navigator.clipboard.writeText(data.body)}
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
                            navigator.clipboard.writeText(`${data.subject}\n\n${data.body}`);
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
    );
}
