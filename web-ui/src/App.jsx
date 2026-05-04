import { useState } from 'react';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import SkeletonCard from './components/SkeletonCard';
import AdminDashboard from './components/AdminDashboard';
import { apiClient } from './api/client';
import { Search, Database } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [results, setResults] = useState([]);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [topK, setTopK] = useState(5);
  const [currentQuery, setCurrentQuery] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 5;

  const handleSearch = async (query) => {
    if (!query.trim()) return;
    setCurrentQuery(query);
    setLoading(true);
    setError('');
    setCurrentPage(1); // Reset page on new search
    
    try {
      const res = await apiClient.post('/search', { query, top_k: topK });
      setResults(res.data.results || []);
      setLatency(res.data.latency);
    } catch (err) {
      setError('Failed to fetch results from the server.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(results.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const endIndex = startIndex + resultsPerPage;
  const currentResults = results.slice(startIndex, endIndex);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navigation Bar */}
      <nav className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 max-w-5xl h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Search className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight text-gray-100">Pinecone Search</span>
          </div>
          <div className="flex bg-gray-900 rounded-lg p-1 border border-gray-700">
            <button
              onClick={() => setActiveTab('search')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'search'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              <Search className="w-4 h-4" /> Tra cứu
            </button>
            <button
              onClick={() => setActiveTab('admin')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'admin'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              <Database className="w-4 h-4" /> Quản lý
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-10 max-w-4xl">
        {activeTab === 'search' ? (
          <div className="animate-in fade-in duration-500">
            <div className="text-center mb-10">
              <h1 className="text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
                Semantic Knowledge Base
              </h1>
              <p className="text-gray-400">Tra cứu cơ sở dữ liệu vector bằng ngôn ngữ tự nhiên.</p>
            </div>

            <SearchBar onSearch={handleSearch} loading={loading} topK={topK} setTopK={setTopK} />

            {error && <div className="text-red-400 mt-4 text-center">{error}</div>}

            <div className="mt-8">
              {!loading && latency !== null && !error && (
                <div className="text-sm text-gray-500 mb-4 text-right animate-in fade-in">
                  Thời gian phản hồi: {(latency * 1000).toFixed(2)} ms
                </div>
              )}
              
              <div className="flex flex-col gap-4">
                {loading ? (
                  <>
                    <SkeletonCard />
                    <SkeletonCard />
                    <SkeletonCard />
                    <SkeletonCard />
                  </>
                ) : (
                  <>
                    {currentResults.map((item, idx) => (
                      <ResultCard key={item.id || idx} item={item} query={currentQuery} />
                    ))}
                    
                    {results.length > 0 && (
                      <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-800 animate-in fade-in">
                        <span className="text-sm text-gray-400">
                          Hiển thị {startIndex + 1} - {Math.min(endIndex, results.length)} trong tổng số {results.length} kết quả
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="px-4 py-2 bg-gray-800 border border-gray-700 hover:bg-gray-700 text-gray-300 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Trước
                          </button>
                          <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages || totalPages === 0}
                            className="px-4 py-2 bg-gray-800 border border-gray-700 hover:bg-gray-700 text-gray-300 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Tiếp
                          </button>
                        </div>
                      </div>
                    )}

                    {results.length === 0 && latency !== null && !error && (
                      <div className="text-center text-gray-500 mt-8 animate-in fade-in">Không tìm thấy kết quả phù hợp.</div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        ) : (
          <AdminDashboard />
        )}
      </main>
    </div>
  );
}

export default App;
