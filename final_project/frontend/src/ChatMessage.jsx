import React, { useState, useRef, useEffect } from 'react';

/**
 * Single chat message bubble.
 *
 * Agent messages: rendered safely (no dangerouslySetInnerHTML).
 * User messages: hover reveals action bar (Copy / Edit / Delete).
 */
export default function ChatMessage({ role, content, index, onEdit, onDelete, isLast }) {
  const isUser = role === 'user';
  const [hovering, setHovering] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(content);
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (editing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(editText.length, editText.length);
    }
  }, [editing]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = content;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const handleSaveEdit = () => {
    const trimmed = editText.trim();
    if (trimmed && trimmed !== content) {
      onEdit(index, trimmed);
    }
    setEditing(false);
  };

  const handleCancelEdit = () => {
    setEditText(content);
    setEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSaveEdit();
    }
    if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  // ── Agent message ──────────────────────────────
  if (!isUser) {
    return (
      <div className={`flex items-start gap-3 max-w-[85%] animate-slide-in-left`}>
        {/* Agent Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-emerald-500/20">
          🌿
        </div>
        {/* Bubble */}
        <div className="bg-slate-800/70 border border-slate-700/50 rounded-2xl rounded-tl-md px-4 py-3 text-slate-200 text-sm leading-relaxed backdrop-blur-sm shadow-lg">
          {renderFormattedText(content)}
        </div>
      </div>
    );
  }

  // ── User message ───────────────────────────────
  return (
    <div
      className="flex flex-col items-end max-w-[85%] ml-auto group"
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      {/* Action bar */}
      <div
        className={`flex items-center gap-1.5 mb-1.5 transition-all duration-200 ${
          hovering && !editing ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-1 pointer-events-none'
        }`}
      >
        <ActionButton
          label={copied ? 'Copied' : 'Copy text'}
          icon={copied 
            ? <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            : <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
          }
          onClick={handleCopy}
          aria-label="Copy message"
        />
        <ActionButton
          label="Edit message"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>}
          onClick={() => { setEditText(content); setEditing(true); }}
          aria-label="Edit message"
        />
        <ActionButton
          label="Delete message"
          icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>}
          onClick={() => onDelete(index)}
          className="hover:bg-red-500/20 hover:text-red-400"
          aria-label="Delete message"
        />
      </div>

      {/* Message body */}
      {editing ? (
        <div className="w-full bg-slate-800/80 border border-emerald-500/40 rounded-2xl p-3 backdrop-blur-sm animate-fade-in-up">
          <textarea
            ref={textareaRef}
            className="w-full bg-transparent text-slate-100 text-sm resize-none outline-none min-h-[60px] leading-relaxed"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            maxLength={2000}
            aria-label="Edit message text"
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={handleCancelEdit}
              className="px-3 py-1 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-700/50 transition-colors"
              aria-label="Cancel edit"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              className="px-3 py-1 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg transition-colors shadow-sm"
              aria-label="Save edit and resubmit"
            >
              Save & Resubmit
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-2xl rounded-tr-md px-4 py-3 text-white text-sm leading-relaxed shadow-lg shadow-emerald-500/10 animate-slide-in-right">
          {content}
        </div>
      )}
    </div>
  );
}

/** Small action button that appears on hover */
function ActionButton({ label, icon, onClick, className = '', ...rest }) {
  return (
    <button
      onClick={onClick}
      title={label}
      className={`p-1.5 text-slate-400 hover:text-slate-100 bg-slate-800/80 hover:bg-slate-700/90 rounded-md transition-all duration-200 backdrop-blur-md border border-slate-600/30 shadow-sm ${className}`}
      {...rest}
    >
      {icon}
    </button>
  );
}

/**
 * Safely render formatted text (basic markdown-style).
 * Handles: **bold**, *italic*, `code`, newlines.
 * Never uses dangerouslySetInnerHTML.
 */
function renderFormattedText(text) {
  if (!text) return null;

  return text.split('\n').map((line, i) => (
    <React.Fragment key={i}>
      {i > 0 && <br />}
      {formatLine(line)}
    </React.Fragment>
  ));
}

function formatLine(line) {
  // Split by bold **...**
  const parts = line.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-emerald-300">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={i} className="italic text-slate-300">{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="px-1 py-0.5 bg-slate-900/60 rounded text-emerald-400 text-xs font-mono">{part.slice(1, -1)}</code>;
    }
    return part;
  });
}
