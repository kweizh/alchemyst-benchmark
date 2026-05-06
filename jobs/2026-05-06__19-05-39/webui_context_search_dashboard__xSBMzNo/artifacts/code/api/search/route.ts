import { AlchemystAI } from '@alchemystai/sdk';
import { NextResponse } from 'next/server';

const client = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY || '',
});

export async function POST(request: Request) {
  try {
    const { query, group_name } = await request.json();

    // Crucial TS SDK Detail: storage uses group_name (snake_case) inside metadata, 
    // but search uses groupName (camelCase) at the root level of the search parameters.
    const response = await client.v1.context.search({
      query,
      similarity_threshold: 0.5,
      minimum_similarity_threshold: 0.5,
      groupName: group_name,
    } as any);

    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Search error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
