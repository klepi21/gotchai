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

    const processFile = useCallback(async (file: File) => {
        if (file.type !== 'application/pdf') {
            alert("Only PDFs are supported!");
            return;
        }

        // Don't set file yet - wait for loader
        setIsAnalyzing(true);

        const formData = new FormData();
        formData.append('file', file);

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
                throw new Error('Analysis failed');
            }

            const data = await response.json();

            // Critical: Set result FIRST, then set file to switch views
            setAnalysisResult(data);
            setFile(file);
        } catch (error) {
            console.error(error);
            alert("Error analyzing file. Is the backend running?");
        } finally {
            setIsAnalyzing(false);
        }
    }, [setFile, setIsAnalyzing, setAnalysisResult]);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0]);
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
                    accept="application/pdf"
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
                                PDFs up to 10MB
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div >
    );
}
