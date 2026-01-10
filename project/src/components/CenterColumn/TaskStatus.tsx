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

  const circumference = 2 * Math.PI * 27;

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-3 flex flex-col items-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <h3 className="text-xs font-medium text-white mb-2">Task Status</h3>

      <div className="relative">
        <svg className="w-[63px] h-[63px] -rotate-90" viewBox="0 0 63 63">
          <circle
            cx="31.5"
            cy="31.5"
            r="27"
            fill="none"
            stroke="#1F2228"
            strokeWidth="6"
          />

          <motion.circle
            cx="31.5"
            cy="31.5"
            r="27"
            fill="none"
            stroke="#3B82F6"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={useTransform(
              progress,
              [0, 100],
              [circumference, 0]
            )}
            style={{
              filter: 'drop-shadow(0 0 6px rgba(59, 130, 246, 0.4))',
            }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-xl font-bold text-white">
            <motion.span>{progressPercent}</motion.span>
            <span className="text-sm text-[#9CA3AF]">%</span>
          </div>
        </div>
      </div>

      <motion.div
        className="mt-3 px-3 py-1 bg-[#3B82F6]/10 rounded-full"
        animate={{
          opacity: [1, 0.6, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <span className="text-xs font-medium text-[#3B82F6]">ACTIVE</span>
      </motion.div>

      <p className="mt-2 text-xs text-[#9CA3AF] text-center max-w-[200px]">
        Processing tasks
      </p>
    </motion.div>
  );
};

export default TaskStatus;
