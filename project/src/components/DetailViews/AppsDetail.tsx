import { motion } from 'framer-motion';
import { ExternalLink, Star, Clock } from 'lucide-react';

const AppsDetail = () => {
  const apps = [
    { name: 'Browser', icon: '🌐', status: 'active', lastUsed: '2 min ago', color: '#3B82F6' },
    { name: 'Code Editor', icon: '💻', status: 'active', lastUsed: '5 min ago', color: '#10B981' },
    { name: 'Terminal', icon: '⌨️', status: 'active', lastUsed: '1 min ago', color: '#F59E0B' },
    { name: 'File Manager', icon: '📁', status: 'inactive', lastUsed: '1 hour ago', color: '#8B5CF6' },
    { name: 'Music Player', icon: '🎵', status: 'inactive', lastUsed: '3 hours ago', color: '#EF4444' },
    { name: 'Email Client', icon: '✉️', status: 'active', lastUsed: '15 min ago', color: '#06B6D4' },
    { name: 'Calculator', icon: '🔢', status: 'inactive', lastUsed: '2 days ago', color: '#EC4899' },
    { name: 'Notes', icon: '📝', status: 'active', lastUsed: '10 min ago', color: '#14B8A6' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-white mb-2">Integrated Applications</h3>
        <p className="text-[#9CA3AF]">Manage and control all your connected applications</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {apps.map((app, index) => (
          <motion.div
            key={app.name}
            className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-5 hover:border-[#3B82F6]/50 transition-all cursor-pointer group"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.03 }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{app.icon}</div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                app.status === 'active' 
                  ? 'bg-[#10B981]/20 text-[#10B981]' 
                  : 'bg-[#6B7280]/20 text-[#6B7280]'
              }`}>
                {app.status}
              </div>
            </div>

            <h4 className="text-lg font-semibold text-white mb-2 group-hover:text-[#3B82F6] transition-colors">
              {app.name}
            </h4>

            <div className="flex items-center gap-2 text-sm text-[#9CA3AF]">
              <Clock className="w-4 h-4" />
              <span>{app.lastUsed}</span>
            </div>

            <div className="mt-4 flex gap-2">
              <button className="flex-1 px-3 py-2 bg-[#3B82F6]/20 text-[#3B82F6] rounded hover:bg-[#3B82F6]/30 transition-colors text-sm font-medium">
                Open
              </button>
              <button className="px-3 py-2 bg-[#2A2D35] text-[#9CA3AF] rounded hover:bg-[#3A3D45] transition-colors" aria-label="Add to favorites">
                <Star className="w-4 h-4" />
              </button>
              <button className="px-3 py-2 bg-[#2A2D35] text-[#9CA3AF] rounded hover:bg-[#3A3D45] transition-colors" aria-label="Open in new window">
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Quick Actions</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button className="px-4 py-3 bg-[#3B82F6]/20 text-[#3B82F6] rounded-lg hover:bg-[#3B82F6]/30 transition-colors font-medium">
            Launch All
          </button>
          <button className="px-4 py-3 bg-[#10B981]/20 text-[#10B981] rounded-lg hover:bg-[#10B981]/30 transition-colors font-medium">
            Recent Apps
          </button>
          <button className="px-4 py-3 bg-[#F59E0B]/20 text-[#F59E0B] rounded-lg hover:bg-[#F59E0B]/30 transition-colors font-medium">
            Favorites
          </button>
          <button className="px-4 py-3 bg-[#8B5CF6]/20 text-[#8B5CF6] rounded-lg hover:bg-[#8B5CF6]/30 transition-colors font-medium">
            Add New
          </button>
        </div>
      </div>
    </div>
  );
};

export default AppsDetail;
