'use client';

import { useState, useEffect } from 'react';

interface SeapData {
  date: string;
  todayCount: number;
  totalInSystem: number;
  lastUpdate: string;
}

export default function Home() {
  const [data, setData] = useState<SeapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const FIRECRAWL_API_KEY = 'fc-3d6cd173506e48d5a99e3c1b189af34d';
  const SEAP_URL = 'https://www.e-licitatie.ro/pub/notices/contract-notices/list/0/0';
  
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Apelam Firecrawl API direct
      const res = await fetch('https://api.firecrawl.dev/v1/scrape', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: SEAP_URL,
          formats: ['markdown'],
          waitFor: 5000
        })
      });
      
      if (res.ok) {
        const json = await res.json();
        const content = json.data?.markdown || '';
        
        // Extrage numarul din "dintr-un total de: X"
        const match = content.toLowerCase().match(/dintr-un\s+total\s+de[:\s]+(\d[\d\.,]*)/);
        const total = match ? parseInt(match[1].replace(/\./g, '').replace(',', '')) : 0;
        
        const today = new Date();
        setData({
          date: today.toLocaleDateString('ro-RO'),
          todayCount: total,
          totalInSystem: total,
          lastUpdate: today.toISOString()
        });
      } else {
        throw new Error('Firecrawl error');
      }
    } catch (err) {
      // Fallback: citeste din Gist
      try {
        const GIST_URL = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json';
        const gistRes = await fetch(`${GIST_URL}?t=${Date.now()}`);
        if (gistRes.ok) {
          setData(await gistRes.json());
        }
      } catch {
        setError('Eroare la încărcare. Reîncearcă.');
      }
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
                <div className="text-center mb-8">
                  <p className="text-blue-200 text-sm uppercase tracking-wider mb-2">Licitații Construcții Azi</p>
                  <div className="text-8xl font-bold text-white mb-2">{data.todayCount}</div>
                  <p className="text-blue-300 text-lg">{data.date}</p>
                </div>

                {/* Divider */}
                <div className="border-t border-white/20 my-6"></div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-white/5 rounded-2xl p-4 text-center">
                    <p className="text-blue-300 text-xs uppercase tracking-wider mb-1">Total în Sistem</p>
                    <p className="text-2xl font-semibold text-white">{data.totalInSystem.toLocaleString()}</p>
                  </div>
                  <div className="bg-white/5 rounded-2xl p-4 text-center">
                    <p className="text-blue-300 text-xs uppercase tracking-wider mb-1">Ultima Actualizare</p>
                    <p className="text-lg font-semibold text-white">
                      {new Date(data.lastUpdate).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>

                {/* Manual Input */}
                <div className="mb-4">
                  <label className="text-blue-200 text-xs uppercase tracking-wider mb-2 block">Actualizare manuală:</label>
                  <div className="flex gap-2">
                    <input 
                      type="number" 
                      placeholder="Nr. licitații azi"
                      className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-blue-300 focus:outline-none focus:border-blue-400"
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (!isNaN(val) && data) {
                          setData({...data, todayCount: val, lastUpdate: new Date().toISOString()});
                        }
                      }}
                    />
                    <button 
                      onClick={fetchData}
                      className="px-4 py-3 bg-white/20 hover:bg-white/30 rounded-xl text-white transition-all"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  </div>
                </div>

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
