const SkeletonCard = () => {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-sm animate-pulse">
      <div className="flex justify-between items-start mb-4">
        <div className="h-6 bg-gray-700 rounded-md w-2/3"></div>
        <div className="h-5 bg-gray-700 rounded-md w-16 shrink-0"></div>
      </div>
      
      <div className="space-y-3 mb-6">
        <div className="h-4 bg-gray-700 rounded-md w-full"></div>
        <div className="h-4 bg-gray-700 rounded-md w-5/6"></div>
        <div className="h-4 bg-gray-700 rounded-md w-4/6"></div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="h-4 bg-gray-700 rounded-md w-20"></div>
        <div className="h-4 bg-gray-700 rounded-md w-10"></div>
        <div className="h-4 bg-gray-700 rounded-md w-10"></div>
        <div className="h-4 bg-gray-700 rounded-md w-24 ml-auto"></div>
      </div>
    </div>
  );
};

export default SkeletonCard;
