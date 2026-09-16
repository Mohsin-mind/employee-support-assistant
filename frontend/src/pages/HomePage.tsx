import React from 'react';
import { useHealth } from '../hooks/useHealth';
import { 
  Activity, 
  Database, 
  Server, 
  Bot, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  Layers, 
  FileText, 
  Cpu, 
  GitBranch, 
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { Button } from '../components/common/Button';

export const HomePage: React.FC = () => {
  const { data: healthResp, isLoading, isError, refetch, isFetching } = useHealth();
  const health = healthResp?.data;

  const phases = [
    {
      num: "01",
      title: "Project Setup & Foundations",
      desc: "FastAPI + React/Vite scaffolding, PostgreSQL connection, health monitoring & Alembic.",
      status: "active",
      tech: "FastAPI • SQLAlchemy • Vite • Tailwind v4",
      icon: <Layers size={18} className="text-indigo-400" />,
    },
    {
      num: "02",
      title: "Database & Core Domain APIs",
      desc: "Employee, Leave Balances/Requests, Documents, and Conversation schema CRUD.",
      status: "pending",
      tech: "Router → Service → Repository Pattern",
      icon: <Database size={18} className="text-cyan-400" />,
    },
    {
      num: "03",
      title: "Manual PDF RAG Pipeline",
      desc: "Raw text chunking, embedding generation, and vector cosine search in pgvector (HNSW).",
      status: "pending",
      tech: "pgvector • Cosine Distance • BackgroundTasks",
      icon: <FileText size={18} className="text-emerald-400" />,
    },
    {
      num: "04",
      title: "Conversation Memory & SSE",
      desc: "Sliding window token budgeting, history injection, and live Server-Sent Events token streaming.",
      status: "pending",
      tech: "SSE Streaming • Token Budgeting",
      icon: <Bot size={18} className="text-amber-400" />,
    },
    {
      num: "05",
      title: "Manual Tool Calling",
      desc: "Model function calling: get_leave_balance, check_calendar, apply_leave without frameworks.",
      status: "pending",
      tech: "Function Calling • Tool Execution",
      icon: <Cpu size={18} className="text-rose-400" />,
    },
    {
      num: "06",
      title: "LangChain RAG Migration",
      desc: "Re-architecting RAG with LangChain Document Loaders, VectorStores, and LCEL chains.",
      status: "pending",
      tech: "LangChain • LCEL Chains",
      icon: <Sparkles size={18} className="text-purple-400" />,
    },
    {
      num: "07",
      title: "LangChain Agents & Tools",
      desc: "Transitioning manual tool orchestration to dynamic LangChain Agent Executors.",
      status: "pending",
      tech: "LangChain Agents • Tool Abstractions",
      icon: <GitBranch size={18} className="text-indigo-400" />,
    },
    {
      num: "08",
      title: "LangGraph Stateful Workflow",
      desc: "State machine with cyclic graphs, approval gates, and multi-step leave application workflows.",
      status: "pending",
      tech: "LangGraph • State Machines • Human-in-the-loop",
      icon: <GitBranch size={18} className="text-emerald-400" />,
    },
    {
      num: "09",
      title: "Testing & Production Hardening",
      desc: "Integration tests, auth security, evaluation benchmarks, and error boundaries.",
      status: "pending",
      tech: "Pytest • Auth • Evaluation Benchmarks",
      icon: <ShieldCheck size={18} className="text-cyan-400" />,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col min-h-screen">
      {/* Top Header */}
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-8 border-b border-white/10 mb-8 gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 shrink-0">
            <Bot size={26} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              Employee Support Assistant
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">Enterprise HR Intelligence • Full-Stack FastAPI & React</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold backdrop-blur-md border ${
            health?.status === 'healthy'
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-lg shadow-emerald-500/20'
              : isError
              ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
          }`}>
            <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
            <span>
              {isLoading ? 'Checking Health...' : health?.status === 'healthy' ? 'System Online' : 'System Degraded'}
            </span>
          </div>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()} 
            isLoading={isFetching}
            icon={<RefreshCw size={14} />}
          >
            Refresh
          </Button>
        </div>
      </header>

      {/* Main Metric Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Backend Status Card */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>FastAPI Server</span>
            <Server size={18} className="text-indigo-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight text-white mb-3">
            {isLoading ? 'Checking...' : isError ? 'Offline' : health?.status?.toUpperCase()}
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 pt-3 border-t border-white/5">
            <Activity size={14} className="text-indigo-400" />
            <span>Environment: <strong className="text-slate-200">{health?.environment || 'development'}</strong></span>
          </div>
        </div>

        {/* Database Status Card */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>PostgreSQL Database</span>
            <Database size={18} className="text-emerald-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight mb-3">
            {isLoading ? (
              <span className="text-slate-400">Connecting...</span>
            ) : health?.database === 'connected' ? (
              <span className="text-emerald-400 inline-flex items-center gap-2">
                <CheckCircle2 size={24} /> Connected
              </span>
            ) : (
              <span className="text-rose-400">Disconnected</span>
            )}
          </div>
          <div className="flex justify-between items-center text-xs text-slate-400 pt-3 border-t border-white/5">
            <span>Database: <strong className="text-slate-200">{health?.db_name || 'employee_support_assistant'}</strong></span>
            {health?.db_latency_ms !== undefined && (
              <span className="font-mono text-emerald-400 font-medium">
                {health.db_latency_ms}ms
              </span>
            )}
          </div>
        </div>

        {/* Active Phase Card */}
        <div className="glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center text-slate-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>Current Stage</span>
            <Clock size={18} className="text-amber-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight text-indigo-400 mb-3">
            Phase 1
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 pt-3 border-t border-white/5">
            <span>Project Setup & Connection Validation</span>
          </div>
        </div>
      </section>

      {/* Development Roadmap Section */}
      <section className="mb-12">
        <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <Sparkles size={20} className="text-indigo-400" />
          Progressive Development Phases (1 → 9)
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {phases.map((p) => (
            <div 
              key={p.num} 
              className={`glass-panel rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between ${
                p.status === 'active' ? 'border-indigo-500/50 shadow-lg shadow-indigo-500/10' : ''
              }`}
            >
              {p.status === 'active' && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 to-cyan-400" />
              )}
              <div>
                <div className="flex justify-between items-start mb-3">
                  <span className={`text-[11px] font-mono font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-md ${
                    p.status === 'active' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-white/5 text-slate-400'
                  }`}>
                    Phase {p.num}
                  </span>
                  {p.icon}
                </div>
                <h3 className="text-base font-semibold text-slate-100 mb-2">{p.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">{p.desc}</p>
              </div>
              <div className="pt-3 border-t border-white/5 text-[11px] font-mono text-slate-400">
                {p.tech}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500 gap-3">
        <div>
          Employee Support Assistant • Built with FastAPI, SQLAlchemy 2.0 & React + Tailwind v4
        </div>
        <div>
          API Health: <code className="text-cyan-400 font-mono">/api/v1/health</code>
        </div>
      </footer>
    </div>
  );
};
