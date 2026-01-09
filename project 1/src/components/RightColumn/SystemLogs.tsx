import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useRef } from 'react';

interface Log {
  id: number;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  message: string;
  timestamp: string;
}

const SystemLogs = () => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [logs, setLogs] = useState<Log[]>([
    { id: 1, type: 'INFO', message: 'System initialization complete', timestamp: '14:20:15' },
    { id: 2, type: 'SUCCESS', message: 'Connected to database successfully', timestamp: '14:20:18' },
    { id: 3, type: 'INFO', message: 'Loading user preferences', timestamp: '14:20:22' },
    { id: 4, type: 'WARNING', message: 'High memory usage detected', timestamp: '14:20:45' },
    { id: 5, type: 'SUCCESS', message: 'Task queue processed', timestamp: '14:21:03' },
    { id: 6, type: 'INFO', message: 'Syncing data with cloud', timestamp: '14:21:30' },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const types: Log['type'][] = ['INFO', 'SUCCESS', 'WARNING', 'ERROR'];
      const messages = [
        'Processing request',
        'Cache updated',
        'Background task started',
        'API response received',
        'User action logged',
        'System health check passed',
      ];

      const newLog: Log = {
        id: Date.now(),
        type: types[Math.floor(Math.random() * types.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
        timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      };

      setLogs((prev) => [...prev.slice(-9), newLog]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogColor = (type: Log['type']) => {
    switch (type) {
      case 'INFO':
        return 'text-[#60A5FA]';
      case 'SUCCESS':
        return 'text-[#10B981]';
      case 'WARNING':
        return 'text-[#F59E0B]';
      case 'ERROR':
        return 'text-[#EF4444]';
    }
  };

  const getLogBadgeColor = (type: Log['type']) => {
    switch (type) {
      case 'INFO':
        return 'bg-[#3B82F6]/10 text-[#60A5FA] border-[#3B82F6]/20';
      case 'SUCCESS':
        return 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20';
      case 'WARNING':
        return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
      case 'ERROR':
        return 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20';
    }
  };

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <h3 className="text-sm font-medium text-white mb-4">System Logs</h3>

      <div
        ref={scrollRef}
        className="space-y-2 max-h-[320px] overflow-y-auto scrollbar-thin scrollbar-thumb-[#3B82F6] scrollbar-track-[#1F2228]"
      >
        <AnimatePresence initial={false}>
          {logs.map((log, index) => (
            <motion.div
              key={log.id}
              className="flex items-start gap-3 p-2.5 bg-[#0A0E12] rounded-lg hover:bg-[#1F2228]/30 transition-colors group"
              initial={{ opacity: 0, y: -10, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              layout
            >
              <span className="text-[10px] font-mono text-[#6B7280] whitespace-nowrap mt-0.5">
                [{log.timestamp}]
              </span>

              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${getLogBadgeColor(
                  log.type
                )} whitespace-nowrap`}
              >
                {log.type}
              </span>

              <motion.span
                className={`text-xs ${getLogColor(log.type)} flex-1 font-mono`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                {log.message}
              </motion.span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default SystemLogs;
