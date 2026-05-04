import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Database, Plus, Trash2, Loader2, AlertCircle } from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [records, setRecords] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingRecords, setLoadingRecords] = useState(true);
  const [loadingAdd, setLoadingAdd] = useState(false);
  const [error, setError] = useState('');
  
  // Form State
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const fetchStats = async () => {
    try {
      const res = await apiClient.get('/stats');
      setStats(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingStats(false);
    }
  };

  const fetchRecords = async () => {
    try {
      const res = await apiClient.get('/list?limit=20');
      setRecords(res.data || []);
    } catch (err) {
      console.error(err);
      setError('Lỗi khi tải danh sách dữ liệu.');
    } finally {
      setLoadingRecords(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchRecords();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    
    setLoadingAdd(true);
    setError('');
    try {
      await apiClient.post('/add', { title, content });
      setTitle('');
      setContent('');
      fetchStats();
      fetchRecords();
    } catch (err) {
      console.error(err);
      setError('Lỗi khi thêm dữ liệu.');
    } finally {
      setLoadingAdd(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bạn có chắc chắn muốn xóa bản ghi này?')) return;
    
    try {
      await apiClient.delete(`/vectors/${id}`);
      fetchStats();
      fetchRecords();
    } catch (err) {
      console.error(err);
      setError('Lỗi khi xóa dữ liệu.');
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center gap-3 mb-6">
        <Database className="w-8 h-8 text-indigo-400" />
        <h2 className="text-3xl font-bold text-white">Quản lý dữ liệu</h2>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Stats Section */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-semibold text-gray-200 mb-4">Tổng quan</h3>
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-700 flex items-center justify-between">
          <span className="text-gray-400 font-medium text-lg">Tổng số bản ghi trong CSDL</span>
          {loadingStats ? (
            <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
          ) : (
            <span className="text-3xl font-bold text-indigo-400">
              {stats?.total_vector_count?.toLocaleString() || 0}
            </span>
          )}
        </div>
      </div>

      {/* Add New Record Section */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 shadow-lg">
        <h3 className="text-xl font-semibold text-gray-200 mb-4 flex items-center gap-2">
          <Plus className="w-5 h-5 text-green-400" /> Thêm dữ liệu mới
        </h3>
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="block text-gray-400 text-sm mb-2" htmlFor="title">Tiêu đề (Title)</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              placeholder="Nhập tiêu đề..."
              required
            />
          </div>
          <div>
            <label className="block text-gray-400 text-sm mb-2" htmlFor="content">Nội dung (Content)</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all min-h-[120px]"
              placeholder="Nhập nội dung văn bản để lưu trữ..."
              required
            />
          </div>
          <button
            type="submit"
            disabled={loadingAdd}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-3 rounded-xl transition-colors disabled:opacity-70 w-full sm:w-auto"
          >
            {loadingAdd ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
            Thêm dữ liệu
          </button>
        </form>
      </div>

      {/* Data Table Section */}
      <div className="bg-gray-800 border border-gray-700 rounded-2xl shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-700 flex justify-between items-center">
          <h3 className="text-xl font-semibold text-gray-200">Danh sách bản ghi gần đây</h3>
          {loadingRecords && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-900 border-b border-gray-700 text-gray-400 text-sm uppercase tracking-wider">
                <th className="px-6 py-4 font-medium">ID</th>
                <th className="px-6 py-4 font-medium">Tiêu đề</th>
                <th className="px-6 py-4 font-medium">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700 text-gray-300">
              {records.length === 0 && !loadingRecords ? (
                <tr>
                  <td colSpan="3" className="px-6 py-8 text-center text-gray-500">Chưa có dữ liệu.</td>
                </tr>
              ) : (
                records.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4 font-mono text-sm max-w-[150px] truncate" title={record.id}>
                      {record.id}
                    </td>
                    <td className="px-6 py-4 truncate max-w-[300px]" title={record.metadata?.title || ''}>
                      {record.metadata?.title || 'Không có tiêu đề'}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleDelete(record.id)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-400/10 p-2 rounded-lg transition-colors inline-flex items-center gap-1 text-sm font-medium"
                      >
                        <Trash2 className="w-4 h-4" /> Xóa
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
