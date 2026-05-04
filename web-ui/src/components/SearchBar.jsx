import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const SearchBar = ({ onSearch, loading, topK, setTopK }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col md:flex-row w-full shadow-lg group-hover:shadow-indigo-500/20 transition-all duration-300">
      <div className="relative flex-grow flex">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
          <Search className="h-6 w-6 text-indigo-400" />
        </div>
        <input
          type="text"
          className="w-full pl-12 pr-4 py-4 bg-gray-800 border border-gray-700 md:rounded-l-2xl rounded-t-2xl md:rounded-tr-none text-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:z-10 relative"
          placeholder="Ask something..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      
      <div className="relative flex items-center justify-center md:justify-start bg-gray-800 border border-gray-700 -mt-px md:mt-0 md:-ml-px focus-within:ring-2 focus-within:ring-indigo-500 focus-within:z-10 transition-all w-full md:w-32 shrink-0">
        <label htmlFor="topK" className="pl-4 text-gray-400 font-medium whitespace-nowrap">
          Top-K:
        </label>
        <input
          id="topK"
          type="number"
          min="1"
          max="20"
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="w-16 bg-transparent text-white text-lg px-2 py-4 focus:outline-none"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="flex items-center justify-center px-8 py-4 bg-indigo-600 hover:bg-indigo-500 border border-indigo-600 -mt-px md:mt-0 md:-ml-px md:rounded-r-2xl rounded-b-2xl md:rounded-bl-none text-white font-semibold text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:z-10 disabled:opacity-70 relative shrink-0"
      >
        {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : 'Search'}
      </button>
    </form>
  );
};

export default SearchBar;
