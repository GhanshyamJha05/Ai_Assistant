import { motion } from 'framer-motion';
import { Shield, Lock, HardDrive, ChevronDown } from 'lucide-react';
import { useState } from 'react';

const securityFeatures = [
  {
    icon: Shield,
    title: 'PIN Authentication',
    description: 'Secure access with PIN-based authentication to prevent unauthorized use'
  },
  {
    icon: Lock,
    title: 'Encrypted API Keys',
    description: 'All API keys and sensitive data are encrypted using industry-standard encryption'
  },
  {
    icon: HardDrive,
    title: 'Local Data Processing',
    description: 'Your personal data stays on your device with offline processing capabilities'
  }
];

const faqs = [
  {
    question: 'What makes this different from Alexa/Siri?',
    answer: 'YourDaddy AI Assistant combines 27 specialized AI systems for superior understanding and learning. Unlike Alexa or Siri, it works 100% offline, gives you complete control over 500+ applications, and continuously learns from your interactions without sending data to the cloud.'
  },
  {
    question: 'Can it work offline?',
    answer: 'Yes! YourDaddy is designed with offline-first architecture. While some features like web searches require internet, core functionality including voice recognition, local file management, and application control work completely offline.'
  },
  {
    question: 'What languages are supported?',
    answer: 'We support 10+ languages including English, Hindi, Spanish, French, German, Italian, Portuguese, Russian, Japanese, and Chinese. The assistant can understand and respond in your preferred language with natural conversation flow.'
  },
  {
    question: 'Is my data safe?',
    answer: 'Absolutely. Your data is encrypted and stored locally on your device. We use industry-standard encryption for API keys, PIN authentication for access control, and never send your personal information to external servers unless explicitly required for a specific command.'
  },
  {
    question: 'What can I control with voice?',
    answer: 'You can control over 500+ Windows applications, manage your calendar and emails, play media on Spotify and YouTube, search the web, get weather and news updates, automate file management, take screenshots, and much more. The system learns new commands based on your usage patterns.'
  }
];

export default function SecurityFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

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
            Security & Privacy
          </h2>
          <p className="text-xl text-slate-400">
            Your data security is our top priority
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-24">
          {securityFeatures.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute -inset-0.5 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl opacity-0 group-hover:opacity-100 blur transition-opacity" />
              <div className="relative h-full bg-slate-800/90 backdrop-blur-sm rounded-2xl border border-slate-700 p-6 hover:border-green-500/50 transition-all text-center">
                <div className="inline-flex p-4 bg-green-500/10 rounded-xl border border-green-500/30 mb-4">
                  <feature.icon className="w-8 h-8 text-green-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-400">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 text-center">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-slate-400 text-center mb-12">
            Everything you need to know
          </p>
        </motion.div>

        <div className="max-w-3xl mx-auto space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden hover:border-cyan-500/50 transition-all"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-center justify-between p-6 text-left"
              >
                <span className="text-lg font-semibold text-white pr-4">
                  {faq.question}
                </span>
                <ChevronDown
                  className={`w-5 h-5 text-cyan-400 flex-shrink-0 transition-transform ${
                    openIndex === index ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {openIndex === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="px-6 pb-6"
                >
                  <p className="text-slate-400 leading-relaxed">
                    {faq.answer}
                  </p>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
