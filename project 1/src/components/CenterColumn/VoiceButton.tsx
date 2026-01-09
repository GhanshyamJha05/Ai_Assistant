import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';
import { useState } from 'react';

const VoiceButton = () => {
  const [isListening, setIsListening] = useState(false);

  const handleClick = () => {
    setIsListening(!isListening);
  };

  return (
    <motion.div
      className="flex flex-col items-center justify-center py-12"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <motion.button
        className="relative w-[180px] h-[180px] rounded-full bg-gradient-to-br from-[#16181D] to-[#0A0E12] border-2 border-[#3B82F6] flex items-center justify-center group cursor-pointer overflow-visible"
        onClick={handleClick}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: isListening
            ? [
                '0 0 0 0 rgba(59, 130, 246, 0.7)',
                '0 0 0 20px rgba(59, 130, 246, 0)',
                '0 0 0 0 rgba(59, 130, 246, 0)',
              ]
            : '0 0 40px rgba(59, 130, 246, 0.5)',
        }}
        transition={{
          boxShadow: {
            duration: isListening ? 1.5 : 2,
            repeat: Infinity,
            ease: 'easeOut',
          },
        }}
      >
        <motion.div
          className="absolute inset-0 rounded-full bg-[#3B82F6]"
          animate={{
            opacity: isListening ? [0.1, 0.2, 0.1] : 0.05,
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        <motion.div
          className="absolute inset-0 rounded-full border-2 border-[#3B82F6]"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {isListening && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-[#3B82F6]"
              animate={{
                scale: [1, 1.4, 1],
                opacity: [0.3, 0, 0.3],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-[#3B82F6]"
              animate={{
                scale: [1, 1.6, 1],
                opacity: [0.2, 0, 0.2],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
          </>
        )}

        <motion.div
          animate={{
            scale: isListening ? [1, 1.1, 1] : 1,
          }}
          transition={{
            duration: 0.8,
            repeat: isListening ? Infinity : 0,
            ease: 'easeInOut',
          }}
        >
          <Mic className="w-16 h-16 text-[#3B82F6] relative z-10" strokeWidth={1.5} />
        </motion.div>
      </motion.button>

      <motion.p
        className="mt-6 text-sm font-medium text-[#9CA3AF]"
        animate={{
          opacity: isListening ? [1, 0.5, 1] : 1,
        }}
        transition={{
          duration: 1.5,
          repeat: isListening ? Infinity : 0,
          ease: 'easeInOut',
        }}
      >
        {isListening ? 'Listening...' : 'Click to speak'}
      </motion.p>
    </motion.div>
  );
};

export default VoiceButton;
