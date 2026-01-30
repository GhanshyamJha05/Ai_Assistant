import { motion } from 'framer-motion';
import { Database, Activity, MessageSquare, TrendingUp, Brain, Zap } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const AILearningDetail = () => {
  const { learningStats } = useDashboard();

  const learningMetrics = [
    { 
      icon: Database, 
      label: 'Knowledge Base', 
      value: learningStats.database,
      description: 'Total data stored in learning database',
      color: '#3B82F6',
      trend: '+12%'
    },
    { 
      icon: Activity, 
      label: 'Active Learning Systems', 
      value: learningStats.systems,
      description: 'Currently operational AI modules',
      color: '#10B981',
      trend: '+5%'
    },
    { 
      icon: MessageSquare, 
      label: 'Training Conversations', 
      value: learningStats.conversations,
      description: 'Conversations used for training',
      color: '#F59E0B',
      trend: '+18%'
    },
    { 
      icon: Brain, 
      label: 'Neural Network Layers', 
      value: '342',
      description: 'Active neural network layers',
      color: '#8B5CF6',
      trend: '+3%'
    },
    { 
      icon: TrendingUp, 
      label: 'Learning Rate', 
      value: '96.8%',
      description: 'Current model accuracy',
      color: '#06B6D4',
      trend: '+2.1%'
    },
    { 
      icon: Zap, 
      label: 'Processing Speed', 
      value: '2.3ms',
      description: 'Average inference time',
      color: '#EF4444',
      trend: '-15%'
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-white mb-2">AI Learning Dashboard</h3>
        <p className="text-[#9CA3AF]">Monitor and analyze AI learning performance and metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {learningMetrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6 hover:border-[#3B82F6]/50 transition-all"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.03 }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="p-3 rounded-lg" style={{ backgroundColor: `${metric.color}15` }}>
                <metric.icon className="w-6 h-6" style={{ color: metric.color }} strokeWidth={1.5} />
              </div>
              <span className={`text-sm font-semibold px-2 py-1 rounded ${
                metric.trend.startsWith('+') ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-[#EF4444]/20 text-[#EF4444]'
              }`}>
                {metric.trend}
              </span>
            </div>

            <h4 className="text-sm text-[#9CA3AF] mb-2">{metric.label}</h4>
            <p className="text-3xl font-bold text-white mb-3">{metric.value}</p>
            <p className="text-xs text-[#6B7280]">{metric.description}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Learning Progress</h4>
          <div className="space-y-4">
            {[
              { label: 'Natural Language Understanding', value: 94 },
              { label: 'Context Awareness', value: 89 },
              { label: 'Intent Recognition', value: 97 },
              { label: 'Response Generation', value: 92 },
            ].map((skill, idx) => (
              <div key={idx}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-[#9CA3AF]">{skill.label}</span>
                  <span className="text-sm font-semibold text-white">{skill.value}%</span>
                </div>
                <div className="h-2 bg-[#2A2D35] rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-[#3B82F6] to-[#10B981]"
                    initial={{ width: 0 }}
                    animate={{ width: `${skill.value}%` }}
                    transition={{ duration: 1, delay: idx * 0.2 }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Recent Training Sessions</h4>
          <div className="space-y-3">
            {[
              { session: 'Voice Recognition Training', time: '2 hours ago', status: 'completed' },
              { session: 'Context Learning Update', time: '5 hours ago', status: 'completed' },
              { session: 'Intent Classification', time: '1 day ago', status: 'completed' },
              { session: 'Response Optimization', time: 'In Progress', status: 'active' },
            ].map((session, idx) => (
              <div 
                key={idx} 
                className="flex items-center gap-3 p-3 bg-[#2A2D35] rounded-lg"
              >
                <div className={`w-2 h-2 rounded-full ${
                  session.status === 'active' ? 'bg-[#10B981] animate-pulse' : 'bg-[#6B7280]'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{session.session}</p>
                  <p className="text-xs text-[#6B7280]">{session.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-[#3B82F6]/10 to-[#10B981]/10 border border-[#3B82F6]/30 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-semibold text-white mb-2">Continuous Learning Mode</h4>
            <p className="text-sm text-[#9CA3AF]">AI is actively learning from interactions to improve responses</p>
          </div>
          <button className="px-6 py-3 bg-[#10B981]/20 text-[#10B981] rounded-lg hover:bg-[#10B981]/30 transition-colors font-semibold">
            ACTIVE
          </button>
        </div>
      </div>
    </div>
  );
};

export default AILearningDetail;
