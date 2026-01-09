import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';

const TaskStatus = () => {
  const progress = useMotionValue(0);
  const progressPercent = useTransform(progress, (value) => Math.round(value));

  useEffect(() => {
    const controls = animate(progress, 78, {
      duration: 2,
      delay: 0.5,
      ease: 'easeOut',
    });

    return controls.stop;
  }, [progress]);

  const circumference = 2 * Math.PI * 60;

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-8 flex flex-col items-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <h3 className="text-sm font-medium text-white mb-6">Task Status</h3>

      <div className="relative">
        <svg className="w-[140px] h-[140px] -rotate-90" viewBox="0 0 140 140">
          <circle
            cx="70"
            cy="70"
            r="60"
            fill="none"
            stroke="#1F2228"
            strokeWidth="8"
          />

          <motion.circle
            cx="70"
            cy="70"
            r="60"
            fill="none"
            stroke="#3B82F6"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={useTransform(
              progress,
              [0, 100],
              [circumference, 0]
            )}
            style={{
              filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))',
            }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div className="text-4xl font-bold text-white">
            {progressPercent}
            <span className="text-2xl text-[#9CA3AF]">%</span>
          </motion.div>
        </div>
      </div>

      <motion.div
        className="mt-6 px-4 py-2 bg-[#3B82F6]/10 rounded-full"
        animate={{
          opacity: [1, 0.6, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <span className="text-sm font-medium text-[#3B82F6]">ACTIVE</span>
      </motion.div>

      <p className="mt-4 text-sm text-[#9CA3AF] text-center max-w-xs">
        Processing natural language queries and executing tasks
      </p>
    </motion.div>
  );
};

export default TaskStatus;
