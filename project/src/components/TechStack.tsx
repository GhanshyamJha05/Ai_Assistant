import { motion } from 'framer-motion';

const technologies = [
  { name: 'Google Gemini 2.0', gradient: 'from-blue-500 to-cyan-500' },
  { name: 'OpenAI GPT-4', gradient: 'from-green-500 to-emerald-500' },
  { name: 'Whisper AI', gradient: 'from-purple-500 to-pink-500' },
  { name: 'Python', gradient: 'from-yellow-500 to-orange-500' },
  { name: 'React + TypeScript', gradient: 'from-cyan-500 to-blue-500' },
  { name: 'WebSocket', gradient: 'from-pink-500 to-rose-500' }
];

export default function TechStack() {
  return (
    <section className="relative py-16 bg-slate-800">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Powered by Cutting-Edge Technology
          </h2>
        </motion.div>

        <div className="flex flex-wrap justify-center gap-4">
          {technologies.map((tech, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              className="group relative"
            >
              <div className={`absolute -inset-0.5 bg-gradient-to-r ${tech.gradient} rounded-full opacity-75 group-hover:opacity-100 blur transition-opacity`} />
              <div className="relative px-6 py-3 bg-slate-900 rounded-full border border-slate-700 group-hover:border-transparent transition-all">
                <span className={`font-semibold bg-gradient-to-r ${tech.gradient} text-transparent bg-clip-text`}>
                  {tech.name}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
