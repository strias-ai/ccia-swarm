'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function BountiesListPage() {
  const [bounties] = useState([
    { id: '1', title: 'Conector Freighter Wallet', reward: '500', token: 'XLM', status: 'OPEN' },
    { id: '2', title: 'Auditoría Soroban WorkContract', reward: '1200', token: 'XLM', status: 'IN_PROGRESS' }
  ]);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Bounties Activos</h1>
        <Link href="/create" className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-md text-sm font-medium">
          + Nuevo Bounty
        </Link>
      </div>
      <div className="grid gap-4">
        {bounties.map((b) => (
          <div key={b.id} className="p-6 bg-slate-900 border border-slate-800 rounded-xl flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold">{b.title}</h2>
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400">{b.status}</span>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-purple-400">{b.reward} {b.token}</p>
              <Link href={`/bounties/${b.id}`} className="text-sm text-slate-400 underline">Ver Detalles →</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}