import { motion } from 'framer-motion';
import { Briefcase, Headphones, Info, Cog } from 'lucide-react';

const useCases = [
  {
    icon: Briefcase,
    title: 'Productivity',
    description: 'Schedule meetings, manage your calendar, send emails, and organize tasks effortlessly',
    examples: ['Schedule meeting', 'Send email to team', 'Add reminder', 'Create document'],
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: Headphones,
    title: 'Entertainment',
    description: 'Control Spotify playlists, play YouTube videos, and manage all your media',
    examples: ['Play my workout playlist', 'Next song', 'Play on YouTube', 'Volume up'],
    color: 'from-pink-500 to-rose-500'
  },
  {
    icon: Info,
    title: 'Information',
    description: 'Get weather updates, latest news, web searches, and instant answers',
    examples: ['Weather forecast', 'Latest tech news', 'Search for recipes', 'Define quantum'],
    color: 'from-green-500 to-emerald-500'
  },
  {
    icon: Cog,
    title: 'Automation',
    description: 'Launch applications, organize files, control system settings, and automate workflows',
    examples: ['Open Chrome', 'Organize downloads', 'Take screenshot', 'Lock screen'],
    color: 'from-orange-500 to-yellow-500'
  }
];

export default function UseCases() {
  return (
    <section className="relative py-24 bg-slate-900">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            What Can You Do?
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            From productivity to entertainment, YourDaddy does it all
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {useCases.map((useCase, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              className="group relative"
            >
              <div className={`absolute -inset-0.5 bg-gradient-to-r ${useCase.color} rounded-2xl opacity-0 group-hover:opacity-100 blur transition-opacity`} />
              <div className="relative h-full bg-slate-800/90 backdrop-blur-sm rounded-2xl border border-slate-700 p-8 hover:border-cyan-500/50 transition-all">
                <div className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${useCase.color} mb-4`}>
                  <useCase.icon className="w-8 h-8 text-white" />
                </div>

                <h3 className="text-2xl font-semibold text-white mb-3">
                  {useCase.title}
                </h3>

                <p className="text-slate-400 mb-6">
                  {useCase.description}
                </p>

                <div className="space-y-2">
                  <p className="text-sm text-slate-500 font-semibold uppercase tracking-wider mb-3">
                    Example Commands
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {useCase.examples.map((example, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors"
                      >
                        "{example}"
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
