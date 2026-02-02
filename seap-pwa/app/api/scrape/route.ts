import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// Citeste datele din fisierul JSON generat de scriptul Python
async function readSeapData() {
  try {
    const filePath = path.join(process.cwd(), '..', 'seap_data.json');
    const data = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // Daca fisierul nu exista, returneaza date default
    const today = new Date();
    return {
      date: today.toLocaleDateString('ro-RO', { day: '2-digit', month: '2-digit', year: 'numeric' }),
      todayCount: 0,
      totalInSystem: 0,
      lastUpdate: today.toISOString(),
      note: 'Ruleaza scriptul Python pentru a actualiza datele'
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

export async function POST(request: Request) {
  // Endpoint pentru a primi date de la scriptul Python
  try {
    const body = await request.json();
    
    // Salveaza datele in fisier
    const filePath = path.join(process.cwd(), '..', 'seap_data.json');
    await fs.writeFile(filePath, JSON.stringify(body, null, 2), 'utf-8');
    
    return NextResponse.json({
      success: true,
      saved: true
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Eroare la salvarea datelor'
    }, { status: 500 });
  }
}
