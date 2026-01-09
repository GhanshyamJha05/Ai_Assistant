import { motion } from 'framer-motion';
import { Bell, Wifi, Signal, Battery, Mic } from 'lucide-react';
import { useState, useEffect } from 'react';

const StatusBar = () => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg px-6 py-4 flex items-center justify-between"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center gap-4">
        <motion.div
          className="relative cursor-pointer group"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Bell className="w-5 h-5 text-[#9CA3AF] group-hover:text-[#3B82F6] transition-colors" strokeWidth={1.5} />
          <motion.div
            className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-[#3B82F6] rounded-full"
            animate={{
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </motion.div>

        <div className="w-px h-5 bg-[#1F2228]" />

        <motion.div
          whileHover={{ scale: 1.1 }}
          className="cursor-pointer"
        >
          <Wifi className="w-5 h-5 text-[#9CA3AF] hover:text-[#3B82F6] transition-colors" strokeWidth={1.5} />
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.1 }}
          className="cursor-pointer"
        >
          <Signal className="w-5 h-5 text-[#9CA3AF] hover:text-[#3B82F6] transition-colors" strokeWidth={1.5} />
        </motion.div>
      </div>

      <div className="flex items-center gap-4">
        <motion.div
          className="flex items-center gap-2 cursor-pointer group"
          whileHover={{ scale: 1.05 }}
        >
          <Battery className="w-5 h-5 text-[#9CA3AF] group-hover:text-[#3B82F6] transition-colors" strokeWidth={1.5} />
          <span className="text-sm font-medium text-[#9CA3AF] group-hover:text-white transition-colors">87%</span>
        </motion.div>

        <div className="w-px h-5 bg-[#1F2228]" />

        <motion.div
          whileHover={{ scale: 1.1 }}
          className="cursor-pointer"
        >
          <Mic className="w-5 h-5 text-[#3B82F6]" strokeWidth={1.5} />
        </motion.div>

        <div className="w-px h-5 bg-[#1F2228]" />

        <motion.div
          className="font-mono text-sm text-white font-medium min-w-[80px] text-right"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {formatTime(time)}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default StatusBar;
