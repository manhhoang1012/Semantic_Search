import { MessageSquare, ArrowBigUp } from 'lucide-react';

const ResultCard = ({ item }) => {
  const meta = item.metadata || {};
  const score = item.score ? (item.score * 100).toFixed(1) : 0;

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-indigo-500 transition-colors duration-300 shadow-sm hover:shadow-indigo-500/10">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xl font-bold text-white mb-2">{meta.title || "Untitled Post"}</h3>
        <span className="bg-indigo-900 text-indigo-300 text-xs font-semibold px-2.5 py-0.5 rounded ml-3 shrink-0">
          Match: {score}%
        </span>
      </div>
      
      <div className="flex items-center text-sm text-gray-400 gap-4 mt-4">
        {meta.subreddit && (
          <span className="text-indigo-400 font-medium hover:underline cursor-pointer">
            r/{meta.subreddit}
          </span>
        )}
        <div className="flex items-center gap-1">
          <ArrowBigUp className="w-4 h-4" />
          {meta.score || 0}
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare className="w-4 h-4" />
          {meta.comments || 0}
        </div>
        {meta.username && (
          <span className="text-gray-500 ml-auto">
            u/{meta.username}
          </span>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
