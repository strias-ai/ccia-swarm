import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl text-center space-y-6">
        <h1 className="text-5xl font-extrabold bg-gradient-to-r from-purple-400 to-indigo-500 bg-clip-text text-transparent">
          Stellar Forge
        </h1>
        <p className="text-xl text-slate-300">
          Mercado descentralizado de Bounties y Escrow en tiempo real sobre Soroban.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <Link href="/bounties" className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold">
            Explorar Bounties
          </Link>
          <Link href="/create" className="px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg font-semibold">
            Crear Recompensa
          </Link>
        </div>
      </div>
    </main>
  );
}