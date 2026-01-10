import React, { createContext, useContext, useState, useEffect, useRef, ReactNode } from 'react';
import io, { Socket } from 'socket.io-client';

interface Message {
    id: number;
    type: 'user' | 'ai';
    text: string;
    time: string;
}

interface VoiceCommand {
    id: number;
    command: string;
    time: string;
}

interface SystemStats {
    cpu: number;
    memory: number;
    network: string;
}

interface LearningStats {
    database: string;
    systems: string;
    conversations: string;
}

interface SystemLog {
    id: number;
    type: 'info' | 'success' | 'warning' | 'error';
    message: string;
    time: string;
}

interface DashboardContextType {
    socket: Socket | null;
    chatMessages: Message[];
    voiceCommands: VoiceCommand[];
    systemStats: SystemStats;
    learningStats: LearningStats;
    systemLogs: SystemLog[];
    taskProgress: number;
    isVoiceActive: boolean;
    interimTranscript: string;
    audioLevel: number; // 0-100, real-time microphone audio level
    sendCommand: (command: string) => void;
    toggleVoice: () => void;
    setVoiceLanguage?: (lang: string) => void;
    alwaysActive: boolean;
    toggleAlwaysActive: () => void;
    wakeWordDetected: boolean;
    speak: (text: string, lang?: string) => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export const useDashboard = () => {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error('useDashboard must be used within DashboardProvider');
    }
    return context;
};

interface DashboardProviderProps {
    children: ReactNode;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [chatMessages, setChatMessages] = useState<Message[]>([]);
    const [voiceCommands, setVoiceCommands] = useState<VoiceCommand[]>([]);
    const [systemStats, setSystemStats] = useState<SystemStats>({
        cpu: 0,
        memory: 0,
        network: '0 MB/s',
    });
    const [learningStats, setLearningStats] = useState<LearningStats>({
        database: '--',
        systems: '--',
        conversations: '--',
    });
    const [systemLogs, setSystemLogs] = useState<SystemLog[]>([]);
    const [taskProgress, setTaskProgress] = useState(0);
    const [isVoiceActive, setIsVoiceActive] = useState(false);
    const [interimTranscript, setInterimTranscript] = useState('');
    const [recognition, setRecognition] = useState<any>(null);
    const [voiceLanguage, setVoiceLanguageState] = useState('hi-IN');
    const [isRecognitionStarted, setIsRecognitionStarted] = useState(false);
    const [userStoppedVoice, setUserStoppedVoice] = useState(false); // Track if user manually stopped
    const userStoppedRef = useRef(false); // Ref to track stop state without causing re-renders
    const isVoiceActiveRef = useRef(false); // Ref to track voice active state for reliable checks in handlers
    const [alwaysActive, setAlwaysActive] = useState(false); // Always-active wake word mode
    const [wakeWordDetected, setWakeWordDetected] = useState(false); // Wake word detection state
    const [isProcessingCommand, setIsProcessingCommand] = useState(false); // Processing command after wake word
    const [audioLevel, setAudioLevel] = useState(0); // Real-time audio level 0-100

    // Audio analysis refs
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const microphoneStreamRef = useRef<MediaStream | null>(null);
    const animationFrameRef = useRef<number | null>(null);

    // Initialize Socket.IO connection
    useEffect(() => {
        const newSocket = io('http://127.0.0.1:5000');

        newSocket.on('connect', () => {
            console.log('Connected to backend');
            addSystemLog('success', 'Connected to backend server');
        });

        newSocket.on('disconnect', () => {
            console.log('Disconnected from backend');
            addSystemLog('error', 'Disconnected from backend server');
        });

        newSocket.on('command_response', (data: any) => {
            if (data.success) {
                addChatMessage(data.response || data.message, 'ai');
            } else {
                addChatMessage('Error: ' + (data.error || 'Unknown error'), 'ai');
            }
        });

        newSocket.on('system_stats_update', (stats: any) => {
            setSystemStats({
                cpu: Math.round(stats.cpu_usage || 0),
                memory: Math.round(stats.memory_usage || 0),
                network: stats.network_speed ? `${(stats.network_speed / 1024 / 1024).toFixed(1)} MB/s` : '0 MB/s',
            });
        });

        newSocket.on('log_update', (log: any) => {
            addSystemLog(log.type || 'info', log.message);
        });

        setSocket(newSocket);

        return () => {
            newSocket.close();
        };
    }, []);

    // Initialize Voice Recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
            const recog = new SpeechRecognition();
            recog.continuous = true;  // Keep listening continuously
            recog.interimResults = true; // Enable interim results for real-time transcription

            // Handle language selection - browser doesn't support "auto" as language code
            if (voiceLanguage === 'auto') {
                // Use browser's default language or Hindi as fallback
                recog.lang = navigator.language || 'hi-IN';
                console.log(`🌐 Auto-detect: Using ${recog.lang}`);
            } else {
                recog.lang = voiceLanguage;
            }
            recog.maxAlternatives = 3;  // Get multiple alternatives for better accuracy

            recog.onstart = () => {
                console.log('🎤 Voice recognition started');
                // Only set active if user didn't manually stop (use ref to avoid stale state)
                if (!userStoppedRef.current) {
                    setIsVoiceActive(true);
                    isVoiceActiveRef.current = true; // Sync ref
                    setInterimTranscript('');
                    setIsRecognitionStarted(true);

                    // Start audio level monitoring after delay to prevent conflicts
                    setTimeout(() => {
                        if (isVoiceActiveRef.current) {
                            startAudioLevelMonitoring();
                        }
                    }, 300);
                } else {
                    console.log('⚠️ Recognition started but user stopped - stopping immediately');
                    setIsRecognitionStarted(false);
                    recog.stop();
                }
            };

            recog.onresult = (event: any) => {
                let interim = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        final += transcript;
                    } else {
                        interim += transcript;
                    }
                }

                // Update interim transcript in real-time
                if (interim) {
                    setInterimTranscript(interim);
                }

                // Process final result
                if (final) {
                    setInterimTranscript('');

                    // Check for wake word if in always-active mode
                    if (alwaysActive && !isProcessingCommand) {
                        const wakeWords = ['hey assistant', 'ok assistant', 'hey daddy', 'ok daddy', 'assistant'];
                        const detectedWake = wakeWords.find(wake => final.toLowerCase().includes(wake));

                        if (detectedWake) {
                            console.log('🎯 Wake word detected:', detectedWake);
                            setWakeWordDetected(true);
                            setIsProcessingCommand(true);

                            // Play greeting
                            const greetings = [
                                'Yes, I\'m listening',
                                'How can I help you?',
                                'I\'m ready',
                                'What can I do for you?'
                            ];
                            const greeting = greetings[Math.floor(Math.random() * greetings.length)];
                            speak(greeting, voiceLanguage);

                            // Reset after 10 seconds if no command given
                            setTimeout(() => {
                                if (isProcessingCommand) {
                                    setIsProcessingCommand(false);
                                    setWakeWordDetected(false);
                                }
                            }, 10000);
                            return;
                        }
                    }

                    // Process command if wake word was detected or not in always-active mode
                    if (!alwaysActive || isProcessingCommand) {
                        addVoiceCommand(final);
                        sendCommand(final);

                        // Reset processing state after command
                        setTimeout(() => {
                            setIsProcessingCommand(false);
                            setWakeWordDetected(false);
                        }, 1000);
                    }
                }
            };

            recog.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);

                // Temporary errors - auto-restart
                if (event.error === 'no-speech') {
                    console.log('⚠️ No speech detected, continuing to listen...');
                    // Don't stop, just continue listening
                    return;
                }

                if (event.error === 'audio-capture') {
                    console.log('⚠️ Audio capture issue, trying to restart...');
                    // Try to restart after brief delay
                    setTimeout(() => {
                        if (isVoiceActive && recognition && !userStoppedRef.current) {
                            try {
                                recognition.start();
                            } catch (e) {
                                console.error('Failed to restart after audio-capture error');
                            }
                        }
                    }, 200);
                    return;
                }

                // Critical errors - stop listening
                if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                    console.error('🚫 Microphone access denied');
                    alert('Microphone access denied. Please allow microphone access in your browser settings.');
                    setIsVoiceActive(false);
                    isVoiceActiveRef.current = false; // Sync ref
                    setInterimTranscript('');
                    setUserStoppedVoice(true);
                    userStoppedRef.current = true;
                    return;
                }

                // Network errors - try to continue
                if (event.error === 'network') {
                    console.error('🌐 Network error, will retry on next cycle');
                    // Let the onend handler restart it
                    return;
                }

                // Language not supported
                if (event.error === 'language-not-supported') {
                    console.error('❌ Language not supported:', voiceLanguage);
                    alert(`Language "${voiceLanguage}" is not supported. Switching to Hindi.`);
                    setVoiceLanguageState('hi-IN');
                    return;
                }

                // Other errors - log but try to continue
                console.error('Other recognition error:', event.error);
            };

            recog.onend = () => {
                console.log('🔴 Recognition ended, current state:', isVoiceActiveRef.current, 'userStopped:', userStoppedRef.current);
                setIsRecognitionStarted(false);

                // Stop audio monitoring when recognition ends
                stopAudioLevelMonitoring();

                // Auto-restart if voice is active AND user hasn't manually stopped (use refs to avoid stale state)
                if (isVoiceActiveRef.current && !userStoppedRef.current) {
                    try {
                        console.log('🔄 Auto-restarting voice recognition...');
                        // Small delay to prevent rapid restart issues
                        setTimeout(() => {
                            try {
                                // Double-check user hasn't stopped in the meantime (use refs)
                                if (isVoiceActiveRef.current && !userStoppedRef.current && recog) {
                                    recog.start();
                                    console.log('✅ Voice recognition restarted');
                                } else {
                                    console.log('⚠️ User stopped or voice inactive during restart delay');
                                }
                            } catch (error: any) {
                                console.error('❌ Error in auto-restart:', error);
                                // Only retry if it's not an "already started" error
                                if (error.message && !error.message.includes('already started')) {
                                    // Try one more time after a longer delay
                                    setTimeout(() => {
                                        try {
                                            if (recog && isVoiceActiveRef.current && !userStoppedRef.current) {
                                                recog.start();
                                            }
                                        } catch (e) {
                                            console.error('Failed to restart, stopping:', e);
                                            setIsVoiceActive(false);
                                            isVoiceActiveRef.current = false; // Sync ref
                                            setInterimTranscript('');
                                        }
                                    }, 500);
                                }
                            }
                        }, 100);
                    } catch (error) {
                        console.error('Error in restart handler:', error);
                        setIsVoiceActive(false);
                        isVoiceActiveRef.current = false; // Sync ref
                        setInterimTranscript('');
                    }
                } else {
                    console.log('🛑 Listening stopped by user or not active');
                    setInterimTranscript('');
                }
            };

            setRecognition(recog);
            console.log('✅ Voice recognition initialized (not started)');
        }
    }, [voiceLanguage]); // Only re-initialize when language changes (userStoppedRef used to prevent re-initialization)

    // Audio Level Monitoring Functions
    const startAudioLevelMonitoring = async () => {
        try {
            // Don't request microphone again - Web Speech API already has access
            // We'll create a new stream, but this shouldn't conflict since permissions are granted
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            microphoneStreamRef.current = stream;

            // Create audio context and analyser
            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);

            analyser.fftSize = 256;
            analyser.smoothingTimeConstant = 0.8;
            microphone.connect(analyser);

            audioContextRef.current = audioContext;
            analyserRef.current = analyser;

            // Start analyzing audio levels
            analyzeAudioLevel();
            console.log('🎧 Audio level monitoring started');
        } catch (error) {
            console.error('Failed to start audio monitoring:', error);
            // Don't block speech recognition if audio monitoring fails
            // Just set a default pulsing level
            setAudioLevel(30);
        }
    };

    const analyzeAudioLevel = () => {
        if (!analyserRef.current) return;

        const analyser = analyserRef.current;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const updateLevel = () => {
            if (!analyserRef.current || !isVoiceActiveRef.current) {
                return; // Stop if no longer active
            }

            analyser.getByteFrequencyData(dataArray);

            // Calculate average volume
            const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;

            // Normalize to 0-100 range with boost for better visualization
            const normalizedLevel = Math.min(100, (average / 256) * 150);

            setAudioLevel(normalizedLevel);

            // Continue monitoring
            animationFrameRef.current = requestAnimationFrame(updateLevel);
        };

        updateLevel();
    };

    const stopAudioLevelMonitoring = () => {
        // Cancel animation frame
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
            animationFrameRef.current = null;
        }

        // Stop microphone stream
        if (microphoneStreamRef.current) {
            microphoneStreamRef.current.getTracks().forEach(track => track.stop());
            microphoneStreamRef.current = null;
        }

        // Close audio context
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }

        analyserRef.current = null;
        setAudioLevel(0);
        console.log('🎧 Audio level monitoring stopped');
    };

    // Load Learning Stats
    useEffect(() => {
        const loadLearningStats = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/api/learning/stats/all');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        const sizeTB = data.total_size_mb ? (data.total_size_mb / 1024 / 1024).toFixed(1) : '1.2';
                        const systems = data.active_systems !== undefined ? `${data.active_systems}/27` : '27/27';
                        const convK = data.total_conversations ? (data.total_conversations / 1000).toFixed(1) : '54.3';

                        setLearningStats({
                            database: `${sizeTB}TB`,
                            systems: systems,
                            conversations: `${convK}K`,
                        });
                    }
                }
            } catch (error) {
                console.error('Failed to load learning stats:', error);
                // Keep default values
                setLearningStats({
                    database: '1.2TB',
                    systems: '27/27',
                    conversations: '54.3K',
                });
            }
        };

        loadLearningStats();
    }, []);

    // Simulate system stats updates if not receiving from backend
    useEffect(() => {
        const interval = setInterval(() => {
            if (socket && !socket.connected) {
                setSystemStats({
                    cpu: Math.floor(Math.random() * 40 + 20),
                    memory: Math.floor(Math.random() * 30 + 50),
                    network: `${(Math.random() * 20 + 5).toFixed(1)} MB/s`,
                });
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [socket]);

    const addChatMessage = (text: string, type: 'user' | 'ai') => {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
        });

        setChatMessages((prev) => [
            ...prev,
            {
                id: Date.now(),
                type,
                text,
                time,
            },
        ]);
    };

    const addVoiceCommand = (command: string) => {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
        });

        setVoiceCommands((prev) => [
            {
                id: Date.now(),
                command,
                time,
            },
            ...prev.slice(0, 9), // Keep only last 10
        ]);
    };

    const addSystemLog = (type: 'info' | 'success' | 'warning' | 'error', message: string) => {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
        });

        setSystemLogs((prev) => [
            {
                id: Date.now(),
                type,
                message,
                time,
            },
            ...prev.slice(0, 49), // Keep only last 50
        ]);
    };

    const sendCommand = (command: string) => {
        addChatMessage(command, 'user');

        if (socket && socket.connected) {
            socket.emit('command', { command, message: command });
        } else {
            // Fallback to API
            fetch('http://127.0.0.1:5000/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command }),
            })
                .then((res) => res.json())
                .then((data) => {
                    const response = data.response || data.message;
                    addChatMessage(response, 'ai');

                    // Speak the response if always-active mode
                    if (alwaysActive) {
                        speak(response, voiceLanguage);
                    }
                })
                .catch((error) => {
                    console.error('API call error:', error);
                    const errorMsg = 'Error processing command. Please try again.';
                    addChatMessage(errorMsg, 'ai');
                    if (alwaysActive) {
                        speak(errorMsg, voiceLanguage);
                    }
                });
        }
    };

    const setVoiceLanguage = (lang: string) => {
        setVoiceLanguageState(lang);
        // If recognition is active, restart it with new language
        if (recognition && isVoiceActive) {
            recognition.stop();
            setTimeout(() => {
                if (recognition) {
                    recognition.lang = lang;
                    try {
                        recognition.start();
                    } catch (error) {
                        console.error('Error restarting recognition:', error);
                    }
                }
            }, 100);
        } else if (recognition) {
            recognition.lang = lang;
        }
    };

    const toggleVoice = () => {
        if (!recognition) {
            alert('Voice recognition not supported in this browser');
            return;
        }

        if (isVoiceActive) {
            console.log('🛑 Stopping voice recognition (user clicked stop)');
            // Set flags to prevent onstart from reactivating (sync both state and refs)
            setUserStoppedVoice(true);
            userStoppedRef.current = true;
            // IMPORTANT: Set to false BEFORE calling stop() so onend handler knows not to restart
            setIsVoiceActive(false);
            isVoiceActiveRef.current = false; // Sync ref
            setIsRecognitionStarted(false);
            setInterimTranscript('');

            // Stop audio monitoring
            stopAudioLevelMonitoring();

            recognition.stop();
        } else {
            console.log('▶️ Starting voice recognition (user clicked start)');
            // Clear the stop flags (sync both state and refs)
            setUserStoppedVoice(false);
            userStoppedRef.current = false;
            try {
                if (!isRecognitionStarted) {
                    recognition.start();
                    // State will be set by onstart handler
                } else {
                    console.warn('Recognition already started, not calling start() again');
                    setIsVoiceActive(true); // Sync state
                }
            } catch (error: any) {
                console.error('Error starting voice recognition:', error);
                if (error.message && error.message.includes('already started')) {
                    console.log('Recognition already running, setting state to active');
                    setIsVoiceActive(true);
                    isVoiceActiveRef.current = true; // Sync ref
                }
            }
        }
    };

    // Text-to-Speech function
    const speak = (text: string, lang: string = 'en-US') => {
        try {
            const synth = window.speechSynthesis;

            // Cancel any ongoing speech
            synth.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Map language codes
            if (lang === 'hi-IN' || lang === 'hindi') {
                utterance.lang = 'hi-IN';
            } else if (lang === 'auto') {
                utterance.lang = navigator.language || 'en-US';
            } else {
                utterance.lang = lang;
            }

            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;

            console.log('🔊 Speaking:', text, 'in', utterance.lang);
            synth.speak(utterance);
        } catch (error) {
            console.error('TTS error:', error);
        }
    };

    // Toggle always-active mode
    const toggleAlwaysActive = () => {
        const newState = !alwaysActive;
        setAlwaysActive(newState);

        console.log('🔄 Always-active mode:', newState ? 'ON' : 'OFF');

        if (newState) {
            // Start listening when always-active enabled (sync both state and ref)
            setUserStoppedVoice(false);
            userStoppedRef.current = false;
            if (!isVoiceActive && recognition) {
                try {
                    recognition.start();
                    speak('Always active mode enabled. Waiting for wake word.', voiceLanguage);
                } catch (error) {
                    console.error('Error starting always-active:', error);
                }
            }
        } else {
            // Stop listening when always-active disabled (sync both state and refs)
            if (isVoiceActive && recognition) {
                setUserStoppedVoice(true);
                userStoppedRef.current = true;
                setIsVoiceActive(false);
                isVoiceActiveRef.current = false; // Sync ref
                recognition.stop();
                speak('Always active mode disabled.', voiceLanguage);
            }
            setWakeWordDetected(false);
            setIsProcessingCommand(false);
        }
    };

    const value: DashboardContextType = {
        socket,
        chatMessages,
        voiceCommands,
        systemStats,
        learningStats,
        systemLogs,
        taskProgress,
        isVoiceActive,
        interimTranscript,
        audioLevel,
        sendCommand,
        toggleVoice,
        setVoiceLanguage,
        alwaysActive,
        toggleAlwaysActive,
        wakeWordDetected,
        speak,
    };

    return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
};
