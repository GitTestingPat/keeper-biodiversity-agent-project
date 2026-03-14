import { useState, useCallback, useRef, useEffect } from 'react';
import { useCopilotChatInternal } from '@copilotkit/react-core';

/**
 * Maximum allowed message length (client-side advisory).
 */
const MAX_MESSAGE_LENGTH = 2000;

/**
 * Suspicious prompt-injection patterns (client-side advisory).
 * Only logs a warning; the message is still sent.
 */
const INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)/i,
  /system\s*:\s*/i,
  /\bdo\s+not\s+follow\b.*\brules\b/i,
  /\bjailbreak\b/i,
  /\bDAN\b/,
];

/**
 * Custom hook wrapping CopilotKit's useCopilotChatInternal.
 * Uses the internal API (messages, sendMessage, setMessages) to properly manage
 * AG-UI message format without requiring a paid headless key.
 */
export default function useAgentChat() {
  const {
    messages,
    sendMessage,
    setMessages,
    isLoading,
    stopGeneration,
    reset,
  } = useCopilotChatInternal();

  const [truncatePoint, setTruncatePoint] = useState(-1);
  const bottomRef = useRef(null);

  /**
   * Scroll chat to bottom.
   */
  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  }, []);

  /**
   * Sanitize user input before sending.
   */
  const sanitize = useCallback((text) => {
    let sanitized = text.trim();
    sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    sanitized = sanitized.replace(/<[^>]*>/g, '');
    if (sanitized.length > MAX_MESSAGE_LENGTH) {
      sanitized = sanitized.slice(0, MAX_MESSAGE_LENGTH);
    }
    return sanitized;
  }, []);

  /**
   * Check for prompt injection patterns (advisory only).
   */
  const checkInjection = useCallback((text) => {
    for (const pattern of INJECTION_PATTERNS) {
      if (pattern.test(text)) {
        console.warn('[Security] Potential prompt injection detected:', text.substring(0, 80));
        return true;
      }
    }
    return false;
  }, []);

  /**
   * Send a new message to the agent.
   */
  const handleSendMessage = useCallback(
    async (text) => {
      const sanitized = sanitize(text);
      if (!sanitized) return;

      checkInjection(sanitized);
      setTruncatePoint(-1);

      try {
        await sendMessage({
          id: crypto.randomUUID(),
          role: 'user',
          content: sanitized,
        });
      } catch (error) {
        console.error('Failed to send message:', error);
      }

      scrollToBottom();
    },
    [sendMessage, sanitize, checkInjection, scrollToBottom]
  );

  /**
   * Edit a message at a given index and re-submit.
   * Truncates all messages after the edited one and re-sends.
   */
  const editMessage = useCallback(
    async (index, newText) => {
      const sanitized = sanitize(newText);
      if (!sanitized) return;

      checkInjection(sanitized);

      if (isLoading) {
        stopGeneration();
      }

      // 1. Truncate array exactly before the edited message
      const truncated = messages.slice(0, index);
      setTruncatePoint(index);
      
      // Update state
      setMessages(truncated);

      try {
        // Give React/CopilotKit a moment to flush the truncated array to the engine
        await new Promise(resolve => setTimeout(resolve, 300));
        setTruncatePoint(-1);

        // Send the new edited message to trigger the agent again
        await sendMessage({
          id: crypto.randomUUID(),
          role: 'user',
          content: sanitized,
        });
      } catch (error) {
        console.error('Failed to re-send edited message:', error);
      }

      scrollToBottom();
    },
    [messages, sanitize, checkInjection, setMessages, sendMessage, isLoading, stopGeneration, scrollToBottom]
  );

  /**
   * Delete a message and everything after it.
   * Resets context from that point.
   */
  const deleteMessage = useCallback(
    (index) => {
      if (isLoading) {
        stopGeneration();
      }

      if (index === 0) {
        setTruncatePoint(0);
        reset();
        return;
      }

      const truncated = messages.slice(0, index);
      setTruncatePoint(index);
      setMessages(truncated);
    },
    [messages, setMessages, reset, isLoading, stopGeneration]
  );

  // Auto-scroll when messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return {
    messages,
    sendMessage: handleSendMessage,
    editMessage,
    deleteMessage,
    isLoading,
    stopGeneration,
    bottomRef,
    scrollToBottom,
  };
}
