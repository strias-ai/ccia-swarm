'use client';
import { useState } from 'react';

export default function CreateBountyPage() {
  const [form, setForm] = useState({ title: '', reward: '', description: '' });

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Crear Nuevo Bounty</h1>
      <form className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
        <input 
          type="text" 
          placeholder="Título del Bounty" 
          className="w-full bg-slate-950 border border-slate-800 p-2.5 rounded-md text-white"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />
        <input 
          type="number" 
          placeholder="Recompensa en XLM" 
          className="w-full bg-slate-950 border border-slate-800 p-2.5 rounded-md text-white"
          value={form.reward}
          onChange={(e) => setForm({ ...form, reward: e.target.value })}
        />
        <button type="submit" className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
          Bloquear Fondos y Publicar
        </button>
      </form>
    </div>
  );
}