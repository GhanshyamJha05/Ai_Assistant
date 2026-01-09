import { motion } from 'framer-motion';
import { Video } from 'lucide-react';
import { useState } from 'react';

const CameraFeed = () => {
  const [isRecording] = useState(true);

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <h3 className="text-sm font-medium text-white mb-3">Camera Feed</h3>

      <div className="relative bg-[#0A0E12] rounded-lg overflow-hidden aspect-video flex items-center justify-center group cursor-pointer">
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-[#16181D] to-[#0A0E12]"
          animate={{
            opacity: [0.5, 0.7, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {isRecording && (
          <motion.div
            className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-full"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            <motion.div
              className="w-2 h-2 bg-red-500 rounded-full"
              animate={{
                opacity: [1, 0.3, 1],
                scale: [1, 0.8, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            <span className="text-xs font-medium text-white">REC</span>
          </motion.div>
        )}

        <motion.div
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.2 }}
        >
          <Video className="w-12 h-12 text-[#3B82F6] opacity-60 group-hover:opacity-100 transition-opacity" strokeWidth={1.5} />
        </motion.div>
      </div>
    </motion.div>
  );
};

export default CameraFeed;
