import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Globe, Zap } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';
import { useState } from 'react';

const VoiceButton = () => {
  const {
    isVoiceActive,
    interimTranscript,
    toggleVoice,
    setVoiceLanguage,
    alwaysActive,
    toggleAlwaysActive,
    wakeWordDetected
  } = useDashboard();

  const [showLangSelector, setShowLangSelector] = useState(false);
  const [selectedLang, setSelectedLang] = useState('hi-IN');

  const languages = [
    { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
    { code: 'en-IN', name: 'English (India)', flag: '🇮🇳' },
    { code: 'hi-IN', name: 'हिंदी (Hindi)', flag: '🇮🇳' },
    { code: 'auto', name: 'Auto Detect', flag: '🌐' },
  ];

  const handleLanguageChange = (langCode: string) => {
    setSelectedLang(langCode);
    setVoiceLanguage?.(langCode);
    setShowLangSelector(false);
  };

  return (
    <motion.div
      className="flex flex-col items-center gap-4"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2, duration: 0.5 }}
    >
      {/* Always-Active Mode Toggle */}
      <motion.button
        onClick={toggleAlwaysActive}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${alwaysActive
            ? 'bg-[#3B82F6]/20 border-[#3B82F6] text-[#3B82F6]'
            : 'bg-[#16181D] border-[#3B82F6]/30 text-[#9CA3AF] hover:border-[#3B82F6] hover:text-[#3B82F6]'
          }`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Zap className={`w-4 h-4 ${alwaysActive ? 'text-[#3B82F6]' : ''}`} strokeWidth={2} />
        <span className="text-sm font-medium">
          {alwaysActive ? '⚡ Always Active' : 'Always Active'}
        </span>
        {alwaysActive && (
          <motion.div
            className="w-2 h-2 rounded-full bg-[#3B82F6]"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </motion.button>

      {/* Main Voice Button */}
      <motion.button
        onClick={toggleVoice}
        className={`relative w-[180px] h-[180px] rounded-full bg-[#16181D] border-4 flex items-center justify-center cursor-pointer group overflow-hidden ${wakeWordDetected
            ? 'border-[#10B981]'
            : alwaysActive && isVoiceActive
              ? 'border-[#8B5CF6]'
              : 'border-[#3B82F6]'
          }`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        disabled={alwaysActive}
      >
        {/* Outer pulsing rings */}
        {(isVoiceActive || alwaysActive) && (
          <>
            <motion.div
              className={`absolute inset-0 rounded-full border-4 ${wakeWordDetected ? 'border-[#10B981]' : alwaysActive ? 'border-[#8B5CF6]' : 'border-[#3B82F6]'
                }`}
              animate={{
                scale: [1, 1.3, 1.3],
                opacity: [0.6, 0, 0],
              }}
              transition={{
                duration: alwaysActive && !wakeWordDetected ? 3 : 2,
                repeat: Infinity,
                ease: 'easeOut',
              }}
            />
            <motion.div
              className={`absolute inset-0 rounded-full border-4 ${wakeWordDetected ? 'border-[#10B981]' : alwaysActive ? 'border-[#8B5CF6]' : 'border-[#3B82F6]'
                }`}
              animate={{
                scale: [1, 1.5, 1.5],
                opacity: [0.4, 0, 0],
              }}
              transition={{
                duration: alwaysActive && !wakeWordDetected ? 3 : 2,
                repeat: Infinity,
                ease: 'easeOut',
                delay: 0.4,
              }}
            />
          </>
        )}

        {/* Background glow */}
        <motion.div
          className={`absolute inset-0 rounded-full ${wakeWordDetected ? 'bg-[#10B981]' : alwaysActive ? 'bg-[#8B5CF6]' : 'bg-[#3B82F6]'
            }`}
          animate={{
            opacity: isVoiceActive || alwaysActive ? [0.2, 0.4, 0.2] : 0,
          }}
          transition={isVoiceActive || alwaysActive ? {
            duration: wakeWordDetected ? 0.8 : 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          } : {}}
        />

        {/* Animated sound wave bars when listening */}
        {(isVoiceActive || alwaysActive) && (
          <div className="absolute inset-0 flex items-center justify-center gap-1.5 z-0">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className={`w-1.5 rounded-full ${wakeWordDetected ? 'bg-[#10B981]' : alwaysActive ? 'bg-[#8B5CF6]' : 'bg-[#3B82F6]'
                  }`}
                animate={{
                  height: ['20%', '60%', '20%'],
                }}
                transition={{
                  duration: wakeWordDetected ? 0.5 : 0.8,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: i * 0.15,
                }}
              />
            ))}
          </div>
        )}

        {/* Microphone icon */}
        <div className="relative z-10">
          {isVoiceActive || alwaysActive ? (
            <motion.div
              animate={{
                scale: wakeWordDetected ? [1, 1.2, 1] : [1, 1.1, 1],
              }}
              transition={{
                duration: wakeWordDetected ? 0.5 : 1,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <Mic
                className={`w-16 h-16 text-white drop-shadow-lg ${wakeWordDetected ? 'animate-pulse' : ''}`}
                strokeWidth={1.5}
              />
            </motion.div>
          ) : (
            <MicOff className="w-16 h-16 text-[#3B82F6] group-hover:text-white transition-colors group-hover:scale-110" strokeWidth={1.5} />
          )}
        </div>

        {/* Hover glow effect when not active */}
        {!isVoiceActive && !alwaysActive && (
          <motion.div
            className="absolute inset-0 rounded-full bg-[#3B82F6] opacity-0 group-hover:opacity-30 blur-xl transition-opacity"
          />
        )}
      </motion.button>

      {/* Language selector button */}
      <button
        onClick={() => setShowLangSelector(!showLangSelector)}
        className="flex items-center gap-2 px-4 py-2 bg-[#16181D] border border-[#3B82F6]/30 rounded-lg hover:border-[#3B82F6] transition-colors"
      >
        <Globe className="w-4 h-4 text-[#3B82F6]" />
        <span className="text-sm text-[#9CA3AF]">
          {languages.find(l => l.code === selectedLang)?.name || 'Select Language'}
        </span>
      </button>

      {/* Language dropdown */}
      <AnimatePresence>
        {showLangSelector && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-[300px] bg-[#16181D] border border-[#3B82F6]/30 rounded-lg overflow-hidden shadow-xl z-50"
          >
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`w-full px-6 py-3 flex items-center gap-3 hover:bg-[#3B82F6]/20 transition-colors ${selectedLang === lang.code ? 'bg-[#3B82F6]/10' : ''
                  }`}
              >
                <span className="text-2xl">{lang.flag}</span>
                <span className="text-sm text-white">{lang.name}</span>
                {selectedLang === lang.code && (
                  <span className="ml-auto text-[#3B82F6]">✓</span>
                )}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status text below button */}
      <motion.div
        className="text-sm font-medium text-center"
        animate={{
          color: wakeWordDetected
            ? '#10B981'
            : alwaysActive && isVoiceActive
              ? '#8B5CF6'
              : isVoiceActive
                ? '#3B82F6'
                : '#9CA3AF',
          scale: (isVoiceActive || alwaysActive) ? [1, 1.05, 1] : 1,
        }}
        transition={(isVoiceActive || alwaysActive) ? {
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        } : {}}
      >
        {wakeWordDetected && '🎯 WAKE WORD DETECTED'}
        {!wakeWordDetected && alwaysActive && isVoiceActive && '👂 Waiting for wake word...'}
        {!wakeWordDetected && !alwaysActive && isVoiceActive && '🎤 LISTENING...'}
        {!wakeWordDetected && !alwaysActive && !isVoiceActive && 'Click to speak'}
      </motion.div>

      {/* Real-time transcription */}
      {(isVoiceActive || alwaysActive) && (
        <motion.div
          className={`mt-2 px-6 py-3 border rounded-lg min-w-[300px] max-w-[500px] ${wakeWordDetected
              ? 'bg-[#10B981]/10 border-[#10B981]/30'
              : alwaysActive
                ? 'bg-[#8B5CF6]/10 border-[#8B5CF6]/30'
                : 'bg-[#3B82F6]/10 border-[#3B82F6]/30'
            }`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <div className="text-xs text-[#9CA3AF] mb-1">
            {wakeWordDetected ? 'Listening for command...' : alwaysActive ? 'Say "Hey Assistant"' : 'Transcribing...'}
          </div>
          <motion.div
            className="text-sm text-white font-medium min-h-[20px]"
            animate={{
              opacity: [1, 0.7, 1],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            {interimTranscript || '...'}
          </motion.div>
        </motion.div>
      )}

      {/* Wake Word Instructions */}
      {alwaysActive && !wakeWordDetected && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-[#8B5CF6]/70 text-center max-w-[280px]"
        >
          Say: "Hey Assistant", "Ok Assistant", or "Hey Daddy"
        </motion.div>
      )}
    </motion.div>
  );
};

export default VoiceButton;
