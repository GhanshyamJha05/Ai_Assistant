import { motion } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const VoiceButton = () => {
  const { isVoiceActive, toggleVoice } = useDashboard();

  return (
    <motion.div
      className="flex justify-center items-center"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2, duration: 0.5 }}
    >
      <motion.button
        onClick={toggleVoice}
        className="relative w-[180px] h-[180px] rounded-full bg-[#16181D] border-4 border-[#3B82F6] flex items-center justify-center cursor-pointer group"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={isVoiceActive ? {
          scale: [1, 1.08, 1],
        } : {}}
        transition={isVoiceActive ? {
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        } : {}}
      >
        <motion.div
          className="absolute inset-0 rounded-full bg-[#3B82F6] opacity-0 group-hover:opacity-30 blur-xl transition-opacity"
        />

        {isVoiceActive ? (
          <Mic className="w-16 h-16 text-[#3B82F6] z-10" strokeWidth={1.5} />
        ) : (
          <MicOff className="w-16 h-16 text-[#3B82F6] z-10 group-hover:scale-110 transition-transform" strokeWidth={1.5} />
        )}

        {isVoiceActive && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-[#3B82F6]"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 0, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        )}
      </motion.button>
    </motion.div>
  );
};

export default VoiceButton;
