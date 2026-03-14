import React, { useState, useEffect } from 'react';

const PHASES = [
  "Thinking…",
  "Analyzing data…",
  "Formulating response…",
  "Finalizing output…",
];

/**
 * Animated status indicator that cycles through processing phases.
 * Shows English-language status messages while the agent is generating a response.
 */
export default function StatusChip() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % PHASES.length);
    }, 2200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-3 px-4 py-2 animate-fade-in-up">
      {/* Animated dots */}
      <div className="flex gap-1">
        <span className="typing-dot w-2 h-2 rounded-full bg-emerald-400 inline-block" />
        <span className="typing-dot w-2 h-2 rounded-full bg-emerald-400 inline-block" />
        <span className="typing-dot w-2 h-2 rounded-full bg-emerald-400 inline-block" />
      </div>
      {/* Phase text */}
      <span className="text-sm italic text-emerald-300/80 transition-all duration-300">
        {PHASES[phaseIndex]}
      </span>
    </div>
  );
}
