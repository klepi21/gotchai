'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuditStore } from '@/store/auditStore';
import { UploadCloud, FileText, ArrowUpRight } from 'lucide-react';
import BoxLoader from '@/components/ui/box-loader'; // Import the new loader
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

export default function DragDropUpload() {
    const { setFile, setIsAnalyzing, setAnalysisResult, isAnalyzing } = useAuditStore();
    const [isDragging, setIsDragging] = useState(false);
    const [loadingText, setLoadingText] = useState("Initializing AI...");

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    // Status message rotation
    useEffect(() => {
        if (!isAnalyzing) return;
        const messages = ["Reading Document...", "Analyzing Clauses...", "Identifying Traps...", "Calculating Risk Score..."];
        let i = 0;
        const interval = setInterval(() => {
            setLoadingText(messages[i % messages.length]);
            i++;
        }, 800);
        return () => clearInterval(interval);
    }, [isAnalyzing]);

    // Helper for Base64 -> Blob
    const base64ToBlob = (base64: string, type: string) => {
        const binStr = atob(base64);
        const len = binStr.length;
        const arr = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            arr[i] = binStr.charCodeAt(i);
        }
        return new Blob([arr], { type: type });
    };

    const uploadFiles = useCallback(async (files: File[]) => {
        if (files.length === 0) return;

        // Validation
        const isPdf = files.length === 1 && files[0].type === 'application/pdf';
        const areImages = files.every(f => ['image/jpeg', 'image/png', 'image/heic', 'image/jpg'].includes(f.type));

        if (!isPdf && !areImages) {
            alert("Please upload either a single PDF or a set of Images (JPG/PNG).");
            return;
        }

        // Don't set file yet - wait for loader
        setIsAnalyzing(true);

        const formData = new FormData();
        files.forEach(f => formData.append('file', f));

        try {
            // Enforce minimum 3.5s delay for the "cool loader" to be seen
            const minDelayPromise = new Promise(resolve => setTimeout(resolve, 3500));

            // Use Env Var for API URL in production
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';

            const analysisPromise = fetch(`${API_URL}/analyze`, {
                method: 'POST',
                body: formData,
            });

            // Wait for both
            const [_, response] = await Promise.all([minDelayPromise, analysisPromise]);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ detail: 'Analysis failed' }));
                throw new Error(errData.detail || 'Analysis failed');
            }

            const data = await response.json();

            // Critical: Set result FIRST
            setAnalysisResult(data);

            // Handle File Setting
            if (data.pdf_base64) {
                // If backend returned a generated PDF (e.g. from images), use it
                const blob = base64ToBlob(data.pdf_base64, 'application/pdf');
                const generatedFile = new File([blob], "scanned_contract.pdf", { type: "application/pdf" });
                setFile(generatedFile);
            } else {
                // Otherwise use the original file (if it was a PDF)
                setFile(files[0]);
            }

        } catch (error) {
            console.error(error);
            alert(`Error analyzing file: ${error instanceof Error ? error.message : "Unknown error"}`);
        } finally {
            setIsAnalyzing(false);
        }
    }, [setFile, setIsAnalyzing, setAnalysisResult]);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            uploadFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            uploadFiles(Array.from(e.target.files));
        }
    };

    return (
        <div className="w-full max-w-sm mx-auto">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={clsx(
                    "relative flex flex-col items-center justify-center h-64 rounded-[2rem] border-2 transition-all duration-300 cursor-pointer overflow-hidden group",
                    isDragging
                        ? "border-blue-500 bg-blue-500/10"
                        : "border-neutral-800 bg-black hover:border-neutral-700"
                )}
            >
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_100%)] group-hover:opacity-40 transition-opacity" />

                {/* Subtle Glow */}
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-900/0 via-neutral-900/0 to-neutral-900/50 pointer-events-none" />
                <input
                    type="file"
                    accept="application/pdf, image/png, image/jpeg, image/jpg"
                    multiple
                    capture="environment"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-50"
                    onChange={handleFileInput}
                    disabled={isAnalyzing}
                />

                <AnimatePresence mode="wait">
                    {isAnalyzing ? (
                        <motion.div
                            key="scanning"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex flex-col items-center justify-center"
                        >
                            {/* BOX LOADER HERE */}
                            <div className="scale-75 mb-8">
                                <BoxLoader />
                            </div>
                            <h3 className="text-lg font-bold text-white mt-4">{loadingText}</h3>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="idle"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col items-center text-center p-6"
                        >
                            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mb-4 shadow-xl">
                                <ArrowUpRight className="w-6 h-6 text-black" />
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
                                Upload Contract
                            </h3>
                            <p className="text-neutral-500 text-sm">
                                PDF or Photos (Multiple)
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div >
    );
}
