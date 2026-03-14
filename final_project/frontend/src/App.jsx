import React from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import "./index.css";
import ChatInterface from './ChatInterface';

function App() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-indigo-950 via-slate-900 to-emerald-950 items-center justify-center p-2 md:p-6 overflow-hidden">
      <header className="mb-4 mt-2 text-center max-w-4xl animate-fade-in-down z-10">
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-2xl shadow-lg shadow-emerald-500/30">
            🛡️
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-teal-200 to-emerald-200 tracking-tight drop-shadow-md">
            Biodiversity Sentinel
          </h1>
        </div>
        <p className="text-emerald-100/70 text-sm md:text-base font-medium leading-relaxed max-w-2xl mx-auto">
          Real-time AI monitoring for deforestation, illegal fishing, and poaching
          using satellite imagery and sensor networks.
        </p>
      </header>

      {/* Decorative background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />

      <main className="w-full max-w-[1400px] h-[80vh] flex flex-col rounded-[2.5rem] overflow-hidden shadow-[0_20px_80px_rgba(0,0,0,0.4)] border border-white/5 bg-slate-900/40 backdrop-blur-2xl z-10 relative">
        {/* CopilotKit runtime — keeps SDK hooks + telemetry active.
            The pre-built CopilotChat UI widget is replaced by our custom ChatInterface. */}
        <CopilotKit runtimeUrl="http://127.0.0.1:8000/chat">
          <ChatInterface />
        </CopilotKit>
      </main>

      {/* Footer: branding text removed per requirements */}
      <footer className="mt-4 text-xs text-slate-500/50 font-medium tracking-wide select-none z-10" aria-hidden="true">
        Biodiversity Sentinel v1.0
      </footer>
    </div>
  );
}

export default App;
