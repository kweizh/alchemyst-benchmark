'use client';

import { useState } from 'react';

export default function Home() {
  const [ingestStatus, setIngestStatus] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const handleIngest = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIngestStatus(false);
    const formData = new FormData(e.currentTarget);
    const content = formData.get('content') as string;
    const file_name = formData.get('filename') as string;
    const group_name = (formData.get('groupname') as string).split(',').map(s => s.trim()).filter(Boolean);

    try {
      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, file_name, group_name }),
      });
      if (res.ok) {
        setIngestStatus(true);
      }
    } catch (error) {
      console.error('Ingest failed', error);
    }
  };

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const query = formData.get('query') as string;
    const group_name = (formData.get('search-groupname') as string).split(',').map(s => s.trim()).filter(Boolean);

    try {
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, group_name }),
      });
      const data = await res.json();
      setSearchResults(data.contexts || []);
    } catch (error) {
      console.error('Search failed', error);
    }
  };

  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Alchemyst AI Context Search Dashboard</h1>

      <section className="mb-12 border p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Ingest Section</h2>
        <form id="ingest-form" onSubmit={handleIngest} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Content</label>
            <textarea 
              id="content-input" 
              name="content" 
              className="w-full border p-2 rounded h-32" 
              placeholder="Enter document content here..."
              required 
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">File Name</label>
            <input 
              id="filename-input" 
              name="filename" 
              type="text" 
              className="w-full border p-2 rounded" 
              placeholder="document.txt"
              required 
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Group Names (comma-separated)</label>
            <input 
              id="groupname-input" 
              name="groupname" 
              type="text" 
              className="w-full border p-2 rounded" 
              placeholder="group1, group2"
              required 
            />
          </div>
          <button 
            id="ingest-btn" 
            type="submit" 
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition-colors"
          >
            Ingest Document
          </button>
        </form>
        {ingestStatus && (
          <div id="ingest-success" className="mt-4 p-3 bg-green-100 text-green-700 rounded border border-green-200">
            Document ingested successfully!
          </div>
        )}
      </section>

      <section className="border p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Search Section</h2>
        <form id="search-form" onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block mb-1 font-medium">Query</label>
            <input 
              id="query-input" 
              name="query" 
              type="text" 
              className="w-full border p-2 rounded" 
              placeholder="Search query..."
              required 
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Group Names (comma-separated)</label>
            <input 
              id="search-groupname-input" 
              name="search-groupname" 
              type="text" 
              className="w-full border p-2 rounded" 
              placeholder="group1, group2"
              required 
            />
          </div>
          <button 
            id="search-btn" 
            type="submit" 
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded font-medium transition-colors"
          >
            Search Context
          </button>
        </form>
        <div id="search-results" className="mt-8 space-y-4">
          <h3 className="text-lg font-medium mb-2">Results:</h3>
          {searchResults.length === 0 ? (
            <p className="text-gray-500 italic">No results found or search not performed yet.</p>
          ) : (
            searchResults.map((result, index) => (
              <div key={index} className="border p-4 rounded bg-gray-50 shadow-inner">
                <p className="whitespace-pre-wrap">{result.content}</p>
                {result.score !== undefined && (
                  <div className="mt-2 flex items-center">
                    <span className="text-xs font-semibold uppercase tracking-wider text-gray-400 mr-2">Similarity Score:</span>
                    <span className="text-sm font-mono bg-gray-200 px-2 py-0.5 rounded">{result.score.toFixed(4)}</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}
