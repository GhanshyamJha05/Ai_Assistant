import { useState, useEffect } from 'react';
import { Sparkles, CheckCircle, AlertCircle, XCircle, Loader } from 'lucide-react';
import SystemDiagnostics from './SystemDiagnostics';

interface StartupSequenceProps {
  onComplete: () => void;
}

interface StartupData {
  greeting: string;
  timestamp: string;
  diagnostics: {
    overall_status: string;
    systems: Array<{
      name: string;
      icon: string;
      status: string;
      message: string;
    }>;
  };
  briefing: {
    items: Array<{
      type: string;
      icon: string;
      message: string;
    }>;
  };
  status: string;
}

const StartupSequence = ({ onComplete }: StartupSequenceProps) => {
  const [phase, setPhase] = useState<'boot' | 'diagnostics' | 'briefing' | 'complete'>('boot');
  const [startupData, setStartupData] = useState<StartupData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sound effects helper
  const playSound = (type: 'boot' | 'scan' | 'complete') => {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      if (type === 'boot') {
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(100, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.5);
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1.5);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 1.5);
      } else if (type === 'scan') {
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.05, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
      } else if (type === 'complete') {
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime + 0.2);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.5);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.5);
      }
    } catch (e) {
      console.error("Audio playback error:", e);
    }
  };

  // Text-to-Speech helper
  const speakText = (text: string) => {
    try {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Cancel current speaking
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;

        // Try to find a good English voice
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice =>
          voice.name.includes('Google US English') ||
          voice.name.includes('Microsoft David') ||
          (voice.lang === 'en-US' && !voice.name.includes('Zira'))
        );

        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }

        window.speechSynthesis.speak(utterance);
      }
    } catch (e) {
      console.error("TTS error:", e);
    }
  };

  useEffect(() => {
    const runStartupSequence = async () => {
      try {
        // Phase 1: Boot animation (2 seconds)
        playSound('boot');
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Phase 2: Fetch startup data
        setPhase('diagnostics');
        const response = await fetch('/api/startup/sequence');

        if (!response.ok) {
          throw new Error('Failed to fetch startup data');
        }

        const result = await response.json();

        if (result.success) {
          setStartupData(result.data);
          setLoading(false);

          // Phase 3: Show diagnostics (3 seconds)
          // Play subtle scan sounds
          const scanInterval = setInterval(() => playSound('scan'), 400);
          speakText("Initializing system diagnostics. Checking core protocols.");

          await new Promise(resolve => setTimeout(resolve, 3000));
          clearInterval(scanInterval);

          // Phase 4: Show briefing (3 seconds)
          setPhase('briefing');
          if (result.data) {
            // Construct intelligent briefing speech
            let speech = `${result.data.greeting}, Sir. `;

            // Add weather info if available
            const weatherItem = result.data.briefing.items.find(i => i.type === 'weather');
            if (weatherItem) {
              speech += `It is currently ${weatherItem.message.split(',')[0]}. `;
            }

            // Add calendar info
            const calendarItem = result.data.briefing.items.find(i => i.type === 'calendar');
            if (calendarItem) {
              speech += `Your schedule shows: ${calendarItem.message.replace('Next:', '')}. `;
            }

            // Add tasks info
            const taskItem = result.data.briefing.items.find(i => i.type === 'tasks');
            if (taskItem) {
              speech += `You have ${taskItem.message}. `;
            }

            speech += `All systems are ${result.data.status === 'operational' ? 'fully operational' : 'online'}.`;

            speakText(speech);
          }
          await new Promise(resolve => setTimeout(resolve, 8000)); // Increased time for longer speech

          // Phase 5: Complete
          setPhase('complete');
          playSound('complete');
          speakText("System ready.");
          await new Promise(resolve => setTimeout(resolve, 1500));

          // Mark as seen and complete
          localStorage.setItem('yourdaddy-startup-seen', 'true');
          onComplete();
        } else {
          // ... existing error handling ...
          throw new Error(result.error || 'Unknown error');
        }
      } catch (err) {
        console.error('Startup sequence error:', err);
        setError(err instanceof Error ? err.message : 'Startup failed');
        setLoading(false);

        // Auto-skip on error after 2 seconds
        setTimeout(() => {
          localStorage.setItem('yourdaddy-startup-seen', 'true');
          onComplete();
        }, 2000);
      }
    };

    runStartupSequence();
  }, [onComplete]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="text-[#39FF14]" size={20} />;
      case 'warning':
      case 'partial':
        return <AlertCircle className="text-[#FF9500]" size={20} />;
      case 'error':
        return <XCircle className="text-[#FF3B30]" size={20} />;
      default:
        return <Loader className="text-[#00D9FF] animate-spin" size={20} />;
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f0f1e]">
        <div className="text-center">
          <XCircle className="text-red-500 mx-auto mb-4" size={64} />
          <h2 className="text-2xl font-bold text-white mb-2">Startup Error</h2>
          <p className="text-[#DDDDDD] mb-4">{error}</p>
          <p className="text-sm text-[#DDDDDD]/70">Redirecting to main interface...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f0f1e] overflow-hidden">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(#00D9FF 1px, transparent 1px), linear-gradient(90deg, #00D9FF 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'grid-move 20s linear infinite'
        }} />
      </div>

      <div className="relative z-10 max-w-4xl w-full px-8">
        {/* Boot Phase */}
        {phase === 'boot' && (
          <div className="text-center animate-fade-in">
            <div className="relative w-48 h-48 mx-auto mb-8">
              {/* Pulse rings */}
              <div className="absolute inset-0 rounded-full border-2 border-[#00D9FF] animate-ping opacity-75" />
              <div className="absolute inset-4 rounded-full border-2 border-[#00FFF5] animate-ping opacity-50" style={{ animationDelay: '0.5s' }} />

              {/* Center logo */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-40 h-40 rounded-full bg-gradient-to-br from-[#00D9FF] via-[#6C5CE7] to-[#E17055] flex items-center justify-center animate-breathe shadow-2xl shadow-[#00D9FF]/50">
                  <div className="w-36 h-36 rounded-full bg-[#0A0E27] flex items-center justify-center">
                    <Sparkles size={64} className="text-[#00D9FF] animate-pulse" />
                  </div>
                </div>
              </div>
            </div>

            <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#00D9FF] to-[#00FFF5] mb-4 animate-pulse">
              YOURDADDY ASSISTANT
            </h1>
            <p className="text-xl text-[#DDDDDD] animate-pulse">
              Initializing systems...
            </p>
          </div>
        )}

        {/* Diagnostics Phase */}
        {phase === 'diagnostics' && startupData && (
          <div className="animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#00D9FF] to-[#00FFF5] mb-2">
                SYSTEM DIAGNOSTICS
              </h2>
              <p className="text-[#DDDDDD]">Running comprehensive system checks...</p>
            </div>

            <SystemDiagnostics diagnostics={startupData.diagnostics} />
          </div>
        )}

        {/* Briefing Phase */}
        {phase === 'briefing' && startupData && (
          <div className="animate-fade-in">
            <div className="text-center mb-8">
              <div className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-[#00D9FF]/20 to-[#6C5CE7]/20 border border-[#00D9FF]/50 mb-6">
                <span className="text-2xl font-bold text-[#00D9FF]">
                  {startupData.greeting}, Sir.
                </span>
              </div>

              <p className="text-xl text-[#DDDDDD] mb-2">
                {formatTime(startupData.timestamp)}
              </p>
            </div>

            {/* Briefing Items */}
            <div className="glass-strong p-8 rounded-3xl max-w-2xl mx-auto">
              <div className="space-y-4">
                {startupData.briefing.items.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <span className="text-3xl">{item.icon}</span>
                    <div className="flex-1">
                      <p className="text-white">{item.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Overall Status */}
              <div className="mt-6 pt-6 border-t border-white/10">
                <div className="flex items-center justify-center gap-3">
                  {getStatusIcon(startupData.status)}
                  <span className="text-lg font-semibold text-white">
                    {startupData.status === 'operational' && 'All systems operational'}
                    {startupData.status === 'partial' && 'Systems partially operational'}
                    {startupData.status === 'degraded' && 'Some systems degraded'}
                  </span>
                </div>
              </div>

              <div className="mt-6 text-center">
                <p className="text-[#00D9FF] text-lg font-semibold animate-pulse">
                  Initializing Command Center...
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Complete Phase */}
        {phase === 'complete' && (
          <div className="text-center animate-fade-in">
            <CheckCircle className="text-[#39FF14] mx-auto mb-4 animate-pulse" size={80} />
            <h2 className="text-3xl font-bold text-white mb-2">Ready</h2>
            <p className="text-[#DDDDDD]">Transitioning to Command Center...</p>
          </div>
        )}
      </div>

      {/* Skip button */}
      <button
        onClick={() => {
          localStorage.setItem('yourdaddy-startup-seen', 'true');
          onComplete();
        }}
        className="absolute bottom-8 right-8 px-4 py-2 text-sm text-[#DDDDDD] hover:text-white transition-colors opacity-50 hover:opacity-100"
      >
        Skip →
      </button>

      <style>{`
        @keyframes grid-move {
          0% { transform: translateY(0); }
          100% { transform: translateY(50px); }
        }
        
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default StartupSequence;
