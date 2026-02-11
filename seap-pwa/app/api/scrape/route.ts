import { NextResponse } from 'next/server';

// GitHub Gist URL pentru date live
const GIST_RAW_URL = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json';

// Citeste datele din GitHub Gist (live, dinamic)
async function readSeapData() {
  try {
    // Fetch din GitHub Gist cu cache bust
    const response = await fetch(`${GIST_RAW_URL}?t=${Date.now()}`, {
      cache: 'no-store'
    });
    if (response.ok) {
      return await response.json();
    }
    throw new Error('Gist fetch failed');
  } catch {
    // Daca fetch-ul esueaza, returneaza date default
    const today = new Date();
    return {
      date: today.toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit', year: 'numeric' }),
      todayCount: 0,
      totalInSystem: 0,
      lastUpdate: today.toISOString(),
      note: 'Eroare la obtinerea datelor din Gist'
    };
  }
}

export async function GET() {
  try {
    const data = await readSeapData();
    
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Eroare la obtinerea datelor'
    }, { status: 500 });
  }
}

// POST nu mai e necesar - datele vin din GitHub Gist
