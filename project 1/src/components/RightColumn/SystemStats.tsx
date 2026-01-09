import { motion } from 'framer-motion';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from 'react';

interface StatCard {
  label: string;
  value: number;
  unit: string;
  data: number[];
}

const SystemStats = () => {
  const [stats, setStats] = useState<StatCard[]>([
    {
      label: 'CPU',
      value: 45,
      unit: '%',
      data: [30, 35, 40, 38, 42, 45, 43, 47, 45],
    },
    {
      label: 'Memory',
      value: 62,
      unit: '%',
      data: [55, 58, 60, 59, 61, 63, 62, 64, 62],
    },
    {
      label: 'Network',
      value: 28,
      unit: 'MB/s',
      data: [20, 25, 30, 28, 32, 29, 27, 26, 28],
    },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setStats((prevStats) =>
        prevStats.map((stat) => {
          const newValue = stat.value + (Math.random() - 0.5) * 10;
          const clampedValue = Math.max(0, Math.min(100, newValue));
          const newData = [...stat.data.slice(1), clampedValue];
          return { ...stat, value: Math.round(clampedValue), data: newData };
        })
      );
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      className="grid grid-cols-3 gap-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      {stats.map((stat, index) => {
        const chartData = stat.data.map((value, i) => ({ value, index: i }));

        return (
          <motion.div
            key={stat.label}
            className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4 hover:border-[#3B82F6]/30 transition-all duration-200"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <h4 className="text-xs font-medium text-white mb-2">{stat.label}</h4>
            <motion.div
              className="text-2xl font-bold text-white mb-3"
              key={stat.value}
              initial={{ scale: 1.2, opacity: 0.5 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {stat.value}
              <span className="text-sm text-[#9CA3AF] ml-1">{stat.unit}</span>
            </motion.div>

            <div className="h-12">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={false}
                    animationDuration={300}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

export default SystemStats;
