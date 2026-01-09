import { motion } from 'framer-motion';
import { Wifi, Bell, Battery, Mic } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDashboard } from '../../contexts/DashboardContext';

const StatusBar = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const { isVoiceActive, socket } = useDashboard();

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
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

  const isConnected = socket?.connected || false;

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg px-6 py-3 flex items-center justify-between"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="flex items-center gap-6">
        <motion.div
          className="relative"
          whileHover={{ scale: 1.1 }}
        >
          <Bell className="w-5 h-5 text-[#9CA3AF] hover:text-white transition-colors" strokeWidth={1.5} />
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#EF4444] rounded-full text-[10px] flex items-center justify-center text-white font-bold">
            3
          </span>
        </motion.div>

        <div className="flex items-center gap-2">
          <Wifi className={`w-5 h-5 ${isConnected ? 'text-[#10B981]' : 'text-[#EF4444]'} transition-colors`} strokeWidth={1.5} />
          <span className="text-xs text-[#9CA3AF]">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <motion.div
        className="flex items-center gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center gap-2">
          <Battery className="w-5 h-5 text-[#10B981]" strokeWidth={1.5} />
          <span className="text-xs text-[#9CA3AF]">85%</span>
        </div>

        <div className="flex items-center gap-2">
          <Mic className={`w-5 h-5 ${isVoiceActive ? 'text-[#3B82F6] animate-pulse' : 'text-[#9CA3AF]'} transition-colors`} strokeWidth={1.5} />
          <span className={`text-xs ${isVoiceActive ? 'text-[#3B82F6] font-semibold' : 'text-[#9CA3AF]'}`}>
            {isVoiceActive ? 'LISTENING' : 'READY'}
          </span>
        </div>

        <div className="px-4 py-1.5 bg-[#3B82F6]/10 rounded-lg">
          <span className="text-sm font-mono text-white font-semibold tracking-wider">
            {formatTime(currentTime)}
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default StatusBar;
