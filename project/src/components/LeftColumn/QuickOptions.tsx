import { motion } from 'framer-motion';
import { Smartphone, BarChart3, Settings, MoreHorizontal } from 'lucide-react';

const QuickOptions = () => {
  const options = [
    { icon: Smartphone, label: 'Apps' },
    { icon: BarChart3, label: 'Stats' },
    { icon: Settings, label: 'Settings' },
    { icon: MoreHorizontal, label: 'More' },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {options.map((option, index) => (
        <motion.button
          key={option.label}
          className="relative bg-[#16181D] border border-[#1F2228] rounded-lg p-6 flex flex-col items-center justify-center gap-3 group overflow-hidden transition-all duration-200 hover:scale-[1.02]"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <motion.div
            className="absolute inset-0 border-2 border-[#3B82F6] rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            initial={false}
          />
          <motion.div
            className="absolute inset-0 bg-[#3B82F6] opacity-0 group-hover:opacity-5 rounded-lg transition-opacity duration-200"
            initial={false}
          />
          <option.icon className="w-6 h-6 text-[#9CA3AF] group-hover:text-[#3B82F6] transition-colors duration-200" strokeWidth={1.5} />
          <span className="text-xs font-medium text-[#9CA3AF] group-hover:text-white transition-colors duration-200">
            {option.label}
          </span>
        </motion.button>
      ))}
    </div>
  );
};

export default QuickOptions;
