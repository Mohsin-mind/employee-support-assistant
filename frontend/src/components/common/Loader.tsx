import React from 'react';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export const Loader: React.FC<LoaderProps> = ({ size = 'md', label }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }[size];

  return (
    <div className="flex flex-col items-center justify-center gap-3 p-8">
      <div className={`${sizeClasses} border-white/10 border-t-indigo-500 rounded-full animate-spin`} />
      {label && <span className="text-xs font-medium text-slate-400">{label}</span>}
    </div>
  );
};
