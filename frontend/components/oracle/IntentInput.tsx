'use client';
import { useState, useRef } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';

const EXAMPLE_INTENTS = [
  "Re-engage high-value customers who haven't purchased in 60 days",
  'Win back lapsed VIP customers from Mumbai and Delhi',
  'Target footwear buyers and recommend matching accessories',
  'Re-activate customers with churn probability above 70%',
  'Drive weekend sales for price-sensitive customers',
];

interface Props {
  onSubmit: (intent: string) => void;
  isLoading?: boolean;
}

export function IntentInput({ onSubmit, isLoading }: Props) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
    setValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-4">
      {/* Main input */}
      <div className={`relative rounded-xl border transition-all ${
        focused ? 'border-indigo-400 shadow-[0_0_0_3px_rgba(99,102,241,0.12)]' : 'border-[var(--border)]'
      } bg-white`}>
        <div className="flex items-start gap-3 p-3">
          <div className="mt-1 w-7 h-7 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          </div>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Describe your marketing goal in plain English..."
            rows={3}
            className="flex-1 bg-transparent text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none text-sm leading-relaxed"
            disabled={isLoading}
          />
        </div>
        <div className="flex items-center justify-between px-4 py-2.5 border-t border-[var(--border)] bg-[var(--bg-muted)] rounded-b-xl">
          <span className="text-[11px] text-[var(--text-muted)]">
            {value.length > 0 ? `${value.length} chars · Enter to launch` : 'Shift+Enter for new line'}
          </span>
          <button
            onClick={handleSubmit}
            disabled={!value.trim() || isLoading}
            className="btn-primary text-xs px-4 py-1.5 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Running...</>
            ) : (
              <><Send className="w-3.5 h-3.5" /> Launch Oracle</>
            )}
          </button>
        </div>
      </div>

      {/* Example intents */}
      {!isLoading && (
        <div className="space-y-2">
          <p className="text-[11px] text-[var(--text-muted)] uppercase tracking-wider">Try these →</p>
          <div className="flex flex-wrap gap-1.5">
            {EXAMPLE_INTENTS.map((ex, i) => (
              <button
                key={i}
                onClick={() => { setValue(ex); textareaRef.current?.focus(); }}
                className="text-[11px] px-2.5 py-1 rounded-full bg-[var(--bg-muted)] border border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--accent-light)] hover:text-[var(--accent)] hover:border-indigo-200 transition-all truncate max-w-[280px]"
              >
                {ex.slice(0, 55)}…
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
