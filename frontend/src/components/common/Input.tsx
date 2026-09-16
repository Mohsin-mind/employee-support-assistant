import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full bg-slate-900/60 border rounded-xl px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 transition-all ${
            error
              ? 'border-rose-500/60 focus:ring-rose-500/30'
              : 'border-white/10 focus:border-indigo-500/60 focus:ring-indigo-500/20'
          } ${className}`}
          {...props}
        />
        {error && (
          <span className="text-xs text-rose-400 mt-0.5">{error}</span>
        )}
        {helperText && !error && (
          <span className="text-xs text-slate-400 mt-0.5">{helperText}</span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
