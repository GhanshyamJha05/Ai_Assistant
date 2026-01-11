import { motion } from 'framer-motion';
import { Activity, Cpu, HardDrive } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const SystemStats = () => {
  const { systemStats, setSelectedView } = useDashboard();

  const stats = [
    { icon: Cpu, label: 'CPU Usage', value: `${systemStats.cpu}%`, color: '#3B82F6' },
    { icon: HardDrive, label: 'Memory', value: `${systemStats.memory}%`, color: '#3B82F6' },
    { icon: Activity, label: 'Network', value: systemStats.network, color: '#3B82F6' },
  ];

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4 cursor-pointer hover:border-[#3B82F6]/50 transition-all"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      whileHover={{ scale: 1.02 }}
      onClick={() => setSelectedView('dashboard')}
    >
      <h3 className="text-sm font-medium text-white mb-4">System Stats</h3>
      <div className="grid grid-cols-3 gap-3">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.label}
            className="bg-[#1F2228] rounded-lg p-3 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * index }}
            whileHover={{ scale: 1.05 }}
          >
            <stat.icon className="w-5 h-5 mx-auto mb-2" style={{ color: stat.color }} strokeWidth={1.5} />
            <p className="text-[10px] text-[#9CA3AF] mb-1">{stat.label}</p>
            <p className="text-lg font-bold text-white">{stat.value}</p>
            <div className="mt-2 h-8 relative">
              <div className="absolute bottom-0 left-0 right-0 h-full flex items-end justify-center gap-0.5">
                {[...Array(10)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-[#3B82F6] rounded-t"
                    initial={{ height: 0 }}
                    animate={{
                      height: `${Math.random() * 100}%`,
                    }}
                    transition={{
                      duration: 0.5,
                      delay: i * 0.05,
                      repeat: Infinity,
                      repeatType: 'reverse',
                      repeatDelay: Math.random() * 2,
                    }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default SystemStats;
