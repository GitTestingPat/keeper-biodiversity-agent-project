import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import StatusChip from './StatusChip';
import useAgentChat from './useAgentChat';

/**
 * Main chat panel component.
 * Renders the message list, streaming indicator, and input bar.
 */
export default function ChatInterface() {
  const {
    messages,
    sendMessage,
    editMessage,
    deleteMessage,
    isLoading,
    bottomRef,
    scrollToBottom,
  } = useAgentChat();

  const [inputText, setInputText] = useState('');
  const inputRef = useRef(null);

  // Auto-scroll when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    setInputText('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Filter out system/metadata messages, keep only user and assistant
  const chatMessages = messages.filter(
    (m) => m.role === 'user' || m.role === 'assistant'
  );

  return (
    <div className="flex flex-col w-full h-full">
      {/* ── Message List ────────────────────────── */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-6 space-y-5">
        {/* Welcome state */}
        {chatMessages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in-up">
            <div className="text-5xl mb-4">🌍</div>
            <h2 className="text-xl font-semibold text-emerald-300 mb-2">
              Alert Status: Monitoring Active
            </h2>
            <p className="text-slate-400 text-sm max-w-md leading-relaxed">
              I am connected to global satellite feeds and wildlife sensors.
              How can I assist you in protecting our ecosystems today?
            </p>
          </div>
        )}

        {/* Messages */}
        {chatMessages.map((msg, idx) => (
          <ChatMessage
            key={msg.id || idx}
            role={msg.role}
            content={msg.content}
            index={messages.indexOf(msg)}
            onEdit={editMessage}
            onDelete={deleteMessage}
            isLast={idx === chatMessages.length - 1}
          />
        ))}

        {/* Streaming indicator */}
        {isLoading && <StatusChip />}

        {/* Scroll anchor */}
        <div ref={bottomRef} />
      </div>

      {/* ── Input Bar ───────────────────────────── */}
      <form
        onSubmit={handleSubmit}
        className="flex-shrink-0 border-t border-slate-700/50 bg-slate-900/80 backdrop-blur-md px-4 py-3"
      >
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe a region, species, or threat to analyze…"
              rows={1}
              maxLength={2000}
              disabled={isLoading}
              className="w-full bg-slate-800/60 border border-slate-600/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 resize-none outline-none transition-all duration-200 focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 disabled:opacity-50"
              style={{ minHeight: '44px', maxHeight: '120px' }}
              aria-label="Type your message"
            />
            {/* Character counter */}
            {inputText.length > 1500 && (
              <span className="absolute bottom-1 right-2 text-[10px] text-slate-500">
                {inputText.length}/2000
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="flex-shrink-0 w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center transition-all duration-200 hover:from-emerald-400 hover:to-teal-500 disabled:opacity-30 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20 pulse-glow"
            aria-label="Send message"
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
