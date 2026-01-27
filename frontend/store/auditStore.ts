import { create } from 'zustand';

export interface Trap {
    original_text: string;
    risk_level: 'CRITICAL' | 'CAUTION' | 'INFO';
    category: string;
    plain_english_explanation: string;
    estimated_cost_impact: string;
    remediation: string;
    coordinates: number[][]; // [[x, y, w, h], ...]
    pages: number[];
}

export interface AuditResult {
    overall_predatory_score: number;
    detected_traps: Trap[];
    filename: string;
}

interface AuditState {
    file: File | null;
    pdfUrl: string | null;
    isAnalyzing: boolean;
    analysisResult: AuditResult | null;

    setFile: (file: File) => void;
    setAnalysisResult: (result: AuditResult) => void;
    setIsAnalyzing: (isAnalyzing: boolean) => void;
    reset: () => void;
}

export const useAuditStore = create<AuditState>((set) => ({
    file: null,
    pdfUrl: null,
    isAnalyzing: false,
    analysisResult: null,

    setFile: (file) => set({
        file,
        pdfUrl: URL.createObjectURL(file),
        // analysisResult: null // removed to allow setting result before file
    }),

    setAnalysisResult: (result) => set({ analysisResult: result }),

    setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),

    reset: () => set({
        file: null,
        pdfUrl: null,
        isAnalyzing: false,
        analysisResult: null
    })
}));
