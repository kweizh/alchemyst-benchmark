import { AlchemystAI } from '@alchemystai/sdk';
import { NextResponse } from 'next/server';

const client = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY || '',
});

export async function POST(request: Request) {
  try {
    const { content, file_name, group_name } = await request.json();

    let currentFileName = file_name;
    let success = false;
    let response;

    while (!success) {
      try {
        response = await client.v1.context.add({
          context_type: 'resource',
          source: 'docs',
          scope: 'internal',
          documents: [{ content }],
          metadata: {
            file_name: currentFileName,
            group_name: group_name,
          } as any,
        });
        success = true;
      } catch (error: any) {
        // Friction Point Handling: Attempting to add a document with an existing file_name triggers a 409 Conflict.
        if (error.status === 409 || error.statusCode === 409 || (error.message && error.message.includes('409'))) {
          currentFileName = `${file_name}_${Date.now()}`;
        } else {
          throw error;
        }
      }
    }

    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Ingest error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
