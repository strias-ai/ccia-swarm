'use client';
import { use } from 'react';

export default function BountyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 max-w-4xl mx-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <span className="text-xs text-purple-400 font-mono">Bounty ID: #{resolvedParams.id}</span>
            <h1 className="text-3xl font-bold mt-1">Detalle del Trabajo</h1>
          </div>
          <span className="text-3xl font-extrabold text-purple-400">500 XLM</span>
        </div>
        <p className="text-slate-300">Integración de firma de transacciones con Freighter Wallet en Soroban.</p>
        <button className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
          Entregar Solución
        </button>
      </div>
    </div>
  );
}