import { motion } from 'framer-motion';
import { Grid3x3, BarChart3, Settings, MoreHorizontal } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const QuickOptions = () => {
  const { sendCommand } = useDashboard();

  const options = [
    {
      icon: Grid3x3,
      label: 'Apps',
      onClick: () => {
        sendCommand('Show available apps');
      }
    },
    {
      icon: BarChart3,
      label: 'Stats',
      onClick: () => {
        sendCommand('Show system statistics');
      }
    },
    {
      icon: Settings,
      label: 'Settings',
      onClick: () => {
        sendCommand('Open settings');
      }
    },
    {
      icon: MoreHorizontal,
      label: 'More',
      onClick: () => {
        sendCommand('Show more options');
      }
    },
  ];

  return (
    <motion.div
      className="space-y-3"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <h3 className="text-sm font-medium text-white px-1">Quick Options</h3>
      <div className="grid grid-cols-2 gap-3">
        {options.map((option, index) => (
          <motion.button
            key={option.label}
            onClick={option.onClick}
            className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4 flex flex-col items-center justify-center gap-2 hover:border-[#3B82F6] hover:shadow-[0_0_12px_rgba(59,130,246,0.3)] transition-all duration-200 cursor-pointer group"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * index }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <option.icon
              className="w-6 h-6 text-[#3B82F6] group-hover:scale-110 transition-transform"
              strokeWidth={1.5}
            />
            <span className="text-xs text-[#9CA3AF] group-hover:text-white transition-colors font-medium">
              {option.label}
            </span>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

export default QuickOptions;
