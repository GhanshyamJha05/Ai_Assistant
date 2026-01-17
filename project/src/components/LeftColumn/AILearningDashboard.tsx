import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { Database, Activity, MessageSquare, Brain } from 'lucide-react';
import { useEffect } from 'react';
import { useDashboard } from '../../contexts/DashboardContext';

const StatCard = ({ icon: Icon, label, value, targetValue, delay, onClick }: { icon: any; label: string; value: string; targetValue: number; delay: number; onClick?: () => void }) => {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => {
    if (label === 'Database Stats') return `${latest.toFixed(1)}TB`;
    if (label === 'Active Systems') return `${Math.round(latest)}/27`;
    if (label === 'Model Accuracy') return `${latest.toFixed(1)}%`;
    return `${(latest / 1000).toFixed(1)}K`;
  });

  useEffect(() => {
    const controls = animate(count, targetValue, {
      duration: 2,
      delay: delay,
      ease: 'easeOut',
    });

    return controls.stop;
  }, [count, targetValue, delay]);

  return (
    <motion.div
      className="glass-panel rounded-lg p-2 sm:p-2.5 flex items-center gap-2 sm:gap-2.5 hover:border-neon-cyan/30 transition-all duration-200 cursor-pointer"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="p-1.5 sm:p-2 bg-neon-cyan/10 rounded-lg">
        <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-neon-cyan" strokeWidth={1.5} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[9px] sm:text-[11px] text-[#9CA3AF] mb-0.5 truncate">{label}</p>
        <p className="text-sm sm:text-base font-semibold text-white truncate">
          <motion.span>{rounded}</motion.span>
        </p>
      </div>
    </motion.div>
  );
};

const AILearningDashboard = () => {
  const { learningStats, setSelectedView } = useDashboard();

  // Parse values to get numeric targets
  const dbValue = parseFloat(learningStats.database.replace('TB', '')) || 1.2;
  const systemsValue = parseInt(learningStats.systems.split('/')[0]) || 27;
  const convsValue = parseFloat(learningStats.conversations.replace('K', '')) * 1000 || 54300;
  const accuracyValue = 96.8;

  const stats = [
    { icon: Database, label: 'Database Stats', value: learningStats.database, targetValue: dbValue, onClick: () => setSelectedView('database') },
    { icon: Activity, label: 'Active Systems', value: learningStats.systems, targetValue: systemsValue, onClick: () => setSelectedView('systems') },
    { icon: MessageSquare, label: 'Conversations', value: learningStats.conversations, targetValue: convsValue, onClick: () => setSelectedView('conversations') },
    { icon: Brain, label: 'Model Accuracy', value: '96.8%', targetValue: accuracyValue, onClick: () => setSelectedView('ai-learning') },
  ];

  return (
    <motion.div
      className="space-y-2 sm:space-y-2.5 flex-shrink-0"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <h3 className="text-xs sm:text-sm font-medium text-white px-1">AI Learning Dashboard</h3>
      <div className="grid grid-cols-2 gap-2 sm:gap-2.5">
        {stats.map((stat, index) => (
          <StatCard key={stat.label} {...stat} delay={0.4 + index * 0.1} />
        ))}
      </div>
    </motion.div>
  );
};

export default AILearningDashboard;
