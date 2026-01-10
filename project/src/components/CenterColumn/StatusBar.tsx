import { motion } from 'framer-motion';
import { Wifi, Bell, Battery, Mic } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDashboard } from '../../contexts/DashboardContext';

const StatusBar = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [batteryLevel, setBatteryLevel] = useState<number>(0);
  const [isCharging, setIsCharging] = useState(false);
  const { isVoiceActive, socket } = useDashboard();

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Get battery status
  useEffect(() => {
    const getBatteryStatus = async () => {
      if ('getBattery' in navigator) {
        try {
          const battery: any = await (navigator as any).getBattery();

          const updateBattery = () => {
            setBatteryLevel(Math.round(battery.level * 100));
            setIsCharging(battery.charging);
          };

          updateBattery();

          battery.addEventListener('levelchange', updateBattery);
          battery.addEventListener('chargingchange', updateBattery);

          return () => {
            battery.removeEventListener('levelchange', updateBattery);
            battery.removeEventListener('chargingchange', updateBattery);
          };
        } catch (error) {
          console.log('Battery API not available:', error);
          // Fallback to a reasonable default
          setBatteryLevel(100);
        }
      } else {
        // Battery API not supported
        setBatteryLevel(100);
      }
    };

    getBatteryStatus();
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

  const getBatteryIcon = () => {
    if (isCharging) return '🔌';
    if (batteryLevel > 80) return '🔋';
    if (batteryLevel > 20) return '🔋';
    return '🪫';
  };

  const getBatteryColor = () => {
    if (isCharging) return 'text-[#3B82F6]';
    if (batteryLevel > 20) return 'text-[#10B981]';
    return 'text-[#EF4444]';
  };

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
          <motion.span
            animate={isCharging ? {
              scale: [1, 1.1, 1],
            } : {}}
            transition={isCharging ? {
              duration: 1,
              repeat: Infinity,
              ease: 'easeInOut',
            } : {}}
          >
            {getBatteryIcon()}
          </motion.span>
          <Battery className={`w-5 h-5 ${getBatteryColor()}`} strokeWidth={1.5} />
          <span className={`text-xs ${getBatteryColor()}`}>
            {batteryLevel}%{isCharging ? ' ⚡' : ''}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <motion.div
            animate={isVoiceActive ? {
              scale: [1, 1.2, 1],
            } : {}}
            transition={isVoiceActive ? {
              duration: 0.8,
              repeat: Infinity,
              ease: 'easeInOut',
            } : {}}
          >
            <Mic className={`w-5 h-5 ${isVoiceActive ? 'text-[#3B82F6]' : 'text-[#9CA3AF]'} transition-colors`} strokeWidth={1.5} />
          </motion.div>
          <motion.span
            className={`text-xs font-semibold ${isVoiceActive ? 'text-[#3B82F6]' : 'text-[#9CA3AF]'}`}
            animate={isVoiceActive ? {
              opacity: [1, 0.6, 1],
            } : {}}
            transition={isVoiceActive ? {
              duration: 1,
              repeat: Infinity,
              ease: 'easeInOut',
            } : {}}
          >
            {isVoiceActive ? '● LISTENING' : 'READY'}
          </motion.span>
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
