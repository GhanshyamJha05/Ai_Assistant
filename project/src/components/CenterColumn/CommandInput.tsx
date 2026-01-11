import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { useState } from 'react';
import { useDashboard } from '../../contexts/DashboardContext';

const CommandInput = () => {
  const [command, setCommand] = useState('');
  const { sendCommand } = useDashboard();

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!command.trim()) return;

    sendCommand(command);
    setCommand('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      className="flex-shrink-0"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="bg-[#16181D] border border-[#1F2228] rounded-lg p-0.5 sm:p-1 flex items-center gap-1.5 sm:gap-2 focus-within:border-[#3B82F6]/50 transition-colors">
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a command or ask anything..."
          className="flex-1 bg-transparent text-white placeholder-[#6B7280] px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm focus:outline-none"
        />
        <motion.button
          onClick={() => handleSubmit()}
          disabled={!command.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-[#3B82F6] text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-md flex items-center gap-1.5 font-medium text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <Send className="w-3 h-3 sm:w-4 sm:h-4" />
          Send
        </motion.button>
      </div>
    </motion.div>
  );
};

export default CommandInput;
