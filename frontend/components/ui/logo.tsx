import React from "react";

export const Logo: React.FC<{ className?: string }> = ({ className }) => {
    return (
        <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
            aria-label="GotchAI Logo"
        >
            {/* 
        Minimalist 'G' / Eye Concept:
        1. Outer ring (open circle) representing the 'G' and the lens.
        2. Inner dot representing the 'Search/Focus' point.
        3. Clean, variable width stroke styles.
      */}
            <path
                d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C15.5 3 18.5 5 20 8"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
            <path
                d="M21 12H13M12 12V12.01"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />

            {/* The 'Pupil' / Center of 'G' */}
            <circle cx="12" cy="12" r="2" fill="currentColor" />
        </svg>
    );
};
