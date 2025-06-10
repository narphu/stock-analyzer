import { useState } from "react";
import { Combobox } from '@headlessui/react';
import sp500 from '../data/sp500.json'; // Make sure this file exists

export default function SearchBar({ onSelect }) {
  const [query, setQuery] = useState("");
  const filtered = sp500.filter(ticker =>
    ticker.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Combobox value={query} onChange={onSelect}>
      <div className="relative w-full max-w-md mx-auto">
        <Combobox.Input
          className="w-full border rounded px-4 py-2"
          placeholder="Search ticker (e.g. AAPL)..."
          onChange={(e) => setQuery(e.target.value)}
        />
        {filtered.length > 0 && (
          <Combobox.Options className="absolute z-10 bg-white w-full border rounded mt-1 max-h-60 overflow-y-auto">
            {filtered.map((ticker) => (
              <Combobox.Option key={ticker} value={ticker} className="px-4 py-2 hover:bg-gray-100">
                {ticker}
              </Combobox.Option>
            ))}
          </Combobox.Options>
        )}
      </div>
    </Combobox>
  );
}
