import { motion } from 'framer-motion';
import { LayoutDashboard, Grid3x3, MessageSquare, Mic, Settings, BarChart3 } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const FeatureCard = ({ icon: Icon, label, description, color, onClick, delay }: { 
  icon: any; 
  label: string; 
  description: string;
  color: string;
  onClick: () => void;
  delay: number;
}) => {
  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4 hover:border-[#3B82F6]/50 transition-all duration-200 cursor-pointer group"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      whileHover={{ scale: 1.03, boxShadow: '0 0 20px rgba(59, 130, 246, 0.2)' }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="p-2.5 rounded-lg" style={{ backgroundColor: `${color}15` }}>
          <Icon className="w-5 h-5" style={{ color }} strokeWidth={1.5} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-white mb-1 group-hover:text-[#3B82F6] transition-colors">
            {label}
          </h4>
          <p className="text-xs text-[#9CA3AF] line-clamp-2">{description}</p>
        </div>
      </div>
    </motion.div>
  );
};

const FeatureCards = () => {
  const { setSelectedView } = useDashboard();

  const features = [
    {
      icon: LayoutDashboard,
      label: 'Dashboard',
      description: 'System overview and metrics',
      color: '#3B82F6',
      onClick: () => setSelectedView('dashboard')
    },
    {
      icon: Grid3x3,
      label: 'Apps',
      description: 'Integrated applications',
      color: '#8B5CF6',
      onClick: () => setSelectedView('apps')
    },
    {
      icon: MessageSquare,
      label: 'Chat',
      description: 'Conversation history',
      color: '#10B981',
      onClick: () => setSelectedView('chat')
    },
    {
      icon: Mic,
      label: 'Voice',
      description: 'Voice commands & controls',
      color: '#F59E0B',
      onClick: () => setSelectedView('voice')
    },
    {
      icon: Settings,
      label: 'Settings',
      description: 'Configure your assistant',
      color: '#EF4444',
      onClick: () => setSelectedView('settings')
    },
    {
      icon: BarChart3,
      label: 'Stats',
      description: 'System statistics',
      color: '#06B6D4',
      onClick: () => setSelectedView('stats')
    },
  ];

  return (
    <motion.div
      className="space-y-3"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <h3 className="text-sm font-medium text-white px-1">Features</h3>
      <div className="grid grid-cols-2 gap-3">
        {features.map((feature, index) => (
          <FeatureCard key={feature.label} {...feature} delay={0.1 + index * 0.05} />
        ))}
      </div>
    </motion.div>
  );
};

export default FeatureCards;
