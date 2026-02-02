'use client';

import { useState, useEffect } from 'react';

interface DayEntry {
  date: string;
  count: number;
}

interface SeapData {
  history: DayEntry[];
  totalAllTime: number;
  lastUpdate: string;
}

export default function Home() {
  const [data, setData] = useState<SeapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Gist URL - actualizat de scriptul Python local
  const GIST_URL = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json';
  
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Citeste din Gist (actualizat de scriptul Selenium cu filtrele corecte)
      const res = await fetch(`${GIST_URL}?t=${Date.now()}`, {
        cache: 'no-store'
      });
      
      if (res.ok) {
        const data = await res.json();
        setData(data);
      } else {
        throw new Error('Gist fetch error');
      }
    } catch (err) {
      setError('Eroare la încărcare. Rulează scriptul Python pentru date noi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white/10 backdrop-blur-lg rounded-2xl mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">SEAP Monitor</h1>
          <p className="text-blue-200 text-lg">Licitații Construcții - Monitorizare Zilnică</p>
        </header>

        {/* Main Card */}
        <div className="max-w-md mx-auto">
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/20">
            {loading ? (
              <div className="flex flex-col items-center py-12">
                <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-blue-200">Se încarcă datele...</p>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-red-300 mb-4">{error}</p>
                <button 
                  onClick={fetchData}
                  className="px-6 py-2 bg-white/20 hover:bg-white/30 rounded-full text-white transition-all"
                >
                  Reîncearcă
                </button>
              </div>
            ) : data && (
              <>
                {/* Today's Count - Big Number */}
                <div className="text-center mb-6">
                  <p className="text-blue-200 text-sm uppercase tracking-wider mb-2">Licitații Azi</p>
                  <div className="text-7xl font-bold text-white mb-2">
                    {data.history.length > 0 ? data.history[data.history.length - 1].count : 0}
                  </div>
                  <p className="text-blue-300 text-lg">
                    {data.history.length > 0 ? data.history[data.history.length - 1].date : '-'}
                  </p>
                </div>

                {/* Total All Time */}
                <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-2xl p-4 text-center mb-6 border border-green-400/30">
                  <p className="text-green-300 text-xs uppercase tracking-wider mb-1">Total Toate Zilele</p>
                  <p className="text-4xl font-bold text-white">{data.totalAllTime.toLocaleString()}</p>
                </div>

                {/* Daily History */}
                <div className="mb-6">
                  <p className="text-blue-200 text-xs uppercase tracking-wider mb-3">Istoric Zilnic</p>
                  <div className="bg-white/5 rounded-2xl p-3 max-h-48 overflow-y-auto">
                    {data.history.slice().reverse().map((day, idx) => (
                      <div key={idx} className="flex justify-between items-center py-2 border-b border-white/10 last:border-0">
                        <span className="text-blue-200">{day.date}</span>
                        <span className="text-white font-semibold">{day.count} licitații</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stats */}
                <div className="bg-white/5 rounded-2xl p-4 text-center mb-4">
                  <p className="text-blue-300 text-xs uppercase tracking-wider mb-1">Ultima Actualizare</p>
                  <p className="text-lg font-semibold text-white">
                    {new Date(data.lastUpdate).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                {/* Auto-update note */}
                <p className="text-blue-300/70 text-xs text-center mb-4">
                  Datele se actualizează automat la fiecare oră (Luni-Vineri, 8:00-18:00)
                </p>

                {/* SEAP Link */}
                <a 
                  href="https://www.e-licitatie.ro/pub/notices/contract-notices/list/0/0"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-4 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 rounded-2xl text-white font-semibold transition-all flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Deschide SEAP
                </a>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
