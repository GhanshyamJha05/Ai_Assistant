import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { useState } from 'react';

const CommandInput = () => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      console.log('Command:', input);
      setInput('');
    }
  };

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <form onSubmit={handleSubmit} className="flex gap-3">
        <motion.input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Type a command or ask anything..."
          className="flex-1 bg-[#1F2228] text-white placeholder-[#6B7280] px-5 py-3.5 rounded-lg outline-none transition-all duration-200 border-2 border-transparent focus:border-[#3B82F6] focus:bg-[#0A0E12]"
          animate={{
            boxShadow: isFocused
              ? '0 0 0 4px rgba(59, 130, 246, 0.1)'
              : '0 0 0 0px rgba(59, 130, 246, 0)',
          }}
          transition={{ duration: 0.2 }}
        />

        <motion.button
          type="submit"
          className="bg-[#3B82F6] hover:bg-[#60A5FA] text-white px-6 py-3.5 rounded-lg font-medium flex items-center gap-2 transition-all duration-200 relative overflow-hidden group"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={!input.trim()}
          animate={{
            opacity: input.trim() ? 1 : 0.5,
          }}
        >
          <motion.div
            className="absolute inset-0 bg-white"
            initial={{ x: '-100%', opacity: 0 }}
            whileHover={{ x: '100%', opacity: 0.1 }}
            transition={{ duration: 0.5 }}
          />
          <span className="relative z-10">SEND</span>
          <Send className="w-4 h-4 relative z-10" strokeWidth={2} />
        </motion.button>
      </form>
    </motion.div>
  );
};

export default CommandInput;
