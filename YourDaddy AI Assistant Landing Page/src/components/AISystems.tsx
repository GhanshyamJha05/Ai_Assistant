import { motion } from 'framer-motion';
import { Database, Brain, Network, Target, TrendingUp, GitBranch } from 'lucide-react';

const systems = [
  {
    icon: Database,
    title: 'Historical RAG',
    description: 'Context-aware memory that remembers past conversations and preferences',
    stat: '10K+ interactions'
  },
  {
    icon: Brain,
    title: 'Semantic Memory',
    description: 'Deep understanding of meaning and context beyond keywords',
    stat: '99.7% accuracy'
  },
  {
    icon: Network,
    title: 'Knowledge Graph',
    description: 'Complex relationship mapping between concepts and entities',
    stat: '5M+ connections'
  },
  {
    icon: Target,
    title: 'Intent Classifier',
    description: 'Precise command recognition and action routing',
    stat: '500+ commands'
  },
  {
    icon: TrendingUp,
    title: 'Feedback Learning',
    description: 'Continuous improvement from user corrections and interactions',
    stat: '24/7 learning'
  },
  {
    icon: GitBranch,
    title: 'Graph Neural Networks',
    description: 'Advanced pattern recognition for complex decision making',
    stat: 'Deep learning'
  }
];

export default function AISystems() {
  return (
    <section className="relative py-24 bg-gradient-to-b from-slate-900 to-slate-800">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Powered by{' '}
            <span className="bg-gradient-to-r from-cyan-400 to-blue-500 text-transparent bg-clip-text">
              27 Advanced AI Systems
            </span>
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-4">
            Multiple specialized AI models working together for unmatched intelligence
          </p>
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500/10 border border-cyan-500/20 rounded-full backdrop-blur-sm">
            <span className="text-cyan-400 font-semibold">📚 Learns from 7,300+ articles yearly</span>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {systems.map((system, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ scale: 1.03 }}
              className="group relative"
            >
              <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl opacity-0 group-hover:opacity-100 blur transition-opacity" />
              <div className="relative h-full bg-slate-800/90 backdrop-blur-sm rounded-2xl border border-slate-700 p-6 hover:border-cyan-500/50 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-xl border border-cyan-500/30">
                    <system.icon className="w-6 h-6 text-cyan-400" />
                  </div>
                  <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-xs text-cyan-400 font-semibold">
                    {system.stat}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {system.title}
                </h3>
                <p className="text-slate-400">
                  {system.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-12 text-center"
        >
          <div className="inline-block bg-slate-800/80 backdrop-blur-sm rounded-2xl border border-slate-700 p-8">
            <p className="text-slate-300 text-lg">
              <span className="text-cyan-400 font-bold text-3xl">27</span> specialized AI systems
              <span className="mx-2">•</span>
              <span className="text-blue-400 font-bold text-3xl">Parallel</span> processing
              <span className="mx-2">•</span>
              <span className="text-green-400 font-bold text-3xl">Real-time</span> learning
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
