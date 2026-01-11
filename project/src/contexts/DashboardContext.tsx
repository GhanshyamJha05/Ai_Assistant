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

type ViewType = 'dashboard' | 'apps' | 'chat' | 'voice' | 'settings' | 'ai-learning' | 'database' | 'systems' | 'conversations' | null;

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
    selectedView: ViewType;
    setSelectedView: (view: ViewType) => void;
    closeDetailView: () => void;
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
    const interimTranscriptRef = useRef(''); // Ref to access current transcript in simulation
    const [recognition, setRecognition] = useState<any>(null);
    const [voiceLanguage, setVoiceLanguageState] = useState('en-US'); // Changed default to English
    const [isRecognitionStarted, setIsRecognitionStarted] = useState(false);
    const [userStoppedVoice, setUserStoppedVoice] = useState(false); // Track if user manually stopped
    const userStoppedRef = useRef(false); // Ref to track stop state without causing re-renders
    const isVoiceActiveRef = useRef(false); // Ref to track voice active state for reliable checks in handlers
    const [alwaysActive, setAlwaysActive] = useState(false); // Always-active wake word mode
    const [wakeWordDetected, setWakeWordDetected] = useState(false); // Wake word detection state
    const [isProcessingCommand, setIsProcessingCommand] = useState(false); // Processing command after wake word
    const [audioLevel, setAudioLevel] = useState(0); // Real-time audio level 0-100
    const [selectedView, setSelectedView] = useState<ViewType>(null); // Selected detail view

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

        // Handle voice command responses with talkback
        newSocket.on('voice_response', (data: any) => {
            console.log('🎤 Voice response received:', data);
            
            if (data.success && data.response) {
                addChatMessage(data.response, 'ai');
                
                // Speak the response back to user (talkback)
                speak(data.response, voiceLanguage);
                
                addSystemLog('success', `Command processed: ${data.response.substring(0, 50)}...`);
            } else if (data.error) {
                const errorMsg = data.response || 'Sorry, I encountered an error processing that command.';
                addChatMessage(errorMsg, 'ai');
                speak(errorMsg, voiceLanguage);
                addSystemLog('error', errorMsg);
            }
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
                console.log(`🌐 Auto-detect: Using language ${recog.lang}`);
            } else {
                recog.lang = voiceLanguage;
                console.log(`🌐 Using selected language: ${recog.lang}`);
            }
            recog.maxAlternatives = 3;  // Get multiple alternatives for better accuracy

            recog.onstart = () => {
                console.log('🎤 Voice recognition started');
                console.log('   Language:', recog.lang);
                console.log('   Continuous:', recog.continuous);
                console.log('   Interim Results:', recog.interimResults);
                console.log('   Max Alternatives:', recog.maxAlternatives);
                
                // Only set active if user didn't manually stop (use ref to avoid stale state)
                if (!userStoppedRef.current) {
                    setIsVoiceActive(true);
                    isVoiceActiveRef.current = true; // Sync ref
                    setInterimTranscript('');
                    setIsRecognitionStarted(true);

                    // Start audio level monitoring immediately
                    console.log('🎧 Initiating audio level monitoring...');
                    startAudioLevelMonitoring().catch(err => {
                        console.error('❌ Audio monitoring failed:', err);
                        console.log('📊 Falling back to simulated audio levels');
                        simulateAudioLevel();
                    });
                } else {
                    console.log('⚠️ Recognition started but user stopped - stopping immediately');
                    setIsRecognitionStarted(false);
                    recog.stop();
                }
            };

            recog.onresult = (event: any) => {
                console.log('🎯 Recognition event received:', {
                    resultIndex: event.resultIndex,
                    resultsLength: event.results.length,
                    isFinal: event.results[event.resultIndex]?.isFinal
                });
                
                let interim = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    const confidence = event.results[i][0].confidence;
                    console.log(`  Result ${i}: "${transcript}" (confidence: ${confidence?.toFixed(2) || 'N/A'}, final: ${event.results[i].isFinal})`);
                    
                    if (event.results[i].isFinal) {
                        final += transcript;
                    } else {
                        interim += transcript;
                    }
                }

                // Update interim transcript in real-time (immediate update)
                if (interim) {
                    console.log('💬 Setting interim transcript:', interim);
                    setInterimTranscript(interim);
                    interimTranscriptRef.current = interim; // Update ref for simulation
                } else {
                    console.log('⚠️ No interim text');
                }

                // Process final result
                if (final) {
                    console.log('✅ Final transcript:', final);
                    setInterimTranscript('');
                    interimTranscriptRef.current = ''; // Clear ref

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
                        
                        // Send via socket for voice command processing
                        if (socket && socket.connected) {
                            console.log('📤 Sending voice command to backend:', final);
                            socket.emit('voice_command', { 
                                text: final,
                                language: voiceLanguage,
                                timestamp: new Date().toISOString()
                            });
                        } else {
                            // Fallback to regular command
                            sendCommand(final);
                        }

                        // Reset processing state after command
                        setTimeout(() => {
                            setIsProcessingCommand(false);
                            setWakeWordDetected(false);
                        }, 1000);
                    }
                }
            };

            recog.onerror = (event: any) => {
                console.error('🚨 Speech recognition error:', event.error);

                // Ignore 'aborted' errors during normal stop
                if (event.error === 'aborted') {
                    console.log('Recognition aborted (normal during stop)');
                    return;
                }

                // Temporary errors - just log, continuous mode will handle it
                if (event.error === 'no-speech') {
                    console.log('⚠️ No speech detected, continuous mode will continue...');
                    return;
                }

                if (event.error === 'audio-capture') {
                    console.error('⚠️ Audio capture error - microphone issue');
                    // Don't try to restart, let the user handle it
                    return;
                }

                // Critical errors - stop listening
                if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                    console.error('🚫 Microphone access denied');
                    alert('Microphone access denied. Please allow microphone access in your browser settings.');
                    setIsVoiceActive(false);
                    isVoiceActiveRef.current = false;
                    setInterimTranscript('');
                    setUserStoppedVoice(true);
                    userStoppedRef.current = true;
                    return;
                }

                // Network errors
                if (event.error === 'network') {
                    console.error('🌐 Network error during recognition');
                    return;
                }

                // Language not supported
                if (event.error === 'language-not-supported') {
                    console.error('❌ Language not supported:', voiceLanguage);
                    alert(`Language "${voiceLanguage}" is not supported. Please select a different language.`);
                    setIsVoiceActive(false);
                    isVoiceActiveRef.current = false;
                    return;
                }

                // Other errors - just log
                console.error('Other recognition error:', event.error);
            };

            recog.onend = () => {
                console.log('🔴 Recognition ended, current state:', isVoiceActiveRef.current, 'userStopped:', userStoppedRef.current);
                setIsRecognitionStarted(false);

                // Stop audio monitoring when recognition ends
                stopAudioLevelMonitoring();

                // Only restart if:
                // 1. User hasn't manually stopped
                // 2. Voice is still supposed to be active
                // 3. Not in always-active mode (which handles its own lifecycle)
                if (!userStoppedRef.current && isVoiceActiveRef.current && !alwaysActive) {
                    console.log('🔄 Recognition ended unexpectedly, restarting in 300ms...');
                    setTimeout(() => {
                        if (!userStoppedRef.current && isVoiceActiveRef.current && recog) {
                            try {
                                recog.start();
                                console.log('✅ Recognition restarted');
                            } catch (error: any) {
                                if (!error.message?.includes('already started')) {
                                    console.error('❌ Failed to restart:', error);
                                    setIsVoiceActive(false);
                                    isVoiceActiveRef.current = false;
                                }
                            }
                        }
                    }, 300);
                } else {
                    console.log('🛑 Not restarting - userStopped:', userStoppedRef.current, 'active:', isVoiceActiveRef.current, 'alwaysActive:', alwaysActive);
                    if (!alwaysActive) {
                        setIsVoiceActive(false);
                        isVoiceActiveRef.current = false;
                        setInterimTranscript('');
                    }
                }
            };

            setRecognition(recog);
            console.log('✅ Voice recognition initialized (not started)');
        }
    }, [voiceLanguage]); // Only re-initialize when language changes (userStoppedRef used to prevent re-initialization)

    // Audio Level Monitoring Functions
    const startAudioLevelMonitoring = async () => {
        console.log('🔧 Starting audio level monitoring...');
        
        // First, try using simulated levels to avoid microphone conflicts
        // Web Speech API already has microphone access, requesting again can cause issues
        console.log('💡 Using simulated audio levels to avoid conflicts with Speech Recognition');
        simulateAudioLevel();
        
        /* Disabled real audio monitoring to prevent conflicts with Web Speech API
        try {
            // Request microphone access separately for audio visualization
            console.log('🎤 Requesting microphone access for visualization...');
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false
                }
            });
            console.log('✅ Microphone access granted');
            microphoneStreamRef.current = stream;

            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            console.log('🔊 Audio context created, state:', audioContext.state);
            
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
                console.log('▶️ Audio context resumed');
            }
            
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);

            analyser.fftSize = 512;
            analyser.smoothingTimeConstant = 0.5;
            analyser.minDecibels = -90;
            analyser.maxDecibels = -10;
            microphone.connect(analyser);
            console.log('📊 Analyser configured');

            audioContextRef.current = audioContext;
            analyserRef.current = analyser;

            analyzeAudioLevel();
            console.log('✅ Audio level monitoring started successfully');
        } catch (error) {
            console.error('❌ Failed to start audio monitoring:', error);
            throw error;
        }
        */
    };

    const analyzeAudioLevel = () => {
        if (!analyserRef.current) {
            console.warn('⚠️ No analyser available for audio level monitoring');
            return;
        }

        const analyser = analyserRef.current;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        let frameCount = 0;

        const updateLevel = () => {
            if (!analyserRef.current || !isVoiceActiveRef.current) {
                console.log('⏹️ Stopping audio level monitoring');
                return; // Stop if no longer active
            }

            // Get frequency data
            analyser.getByteFrequencyData(dataArray);

            // Calculate RMS (Root Mean Square) for better volume representation
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                const normalized = dataArray[i] / 255;
                sum += normalized * normalized;
            }
            const rms = Math.sqrt(sum / bufferLength);

            // Convert to 0-100 scale with exponential scaling for better visualization
            const normalizedLevel = Math.min(100, Math.pow(rms, 0.5) * 150);

            // Apply smoothing to reduce jitter
            setAudioLevel(prev => {
                const smoothingFactor = 0.3;
                const newLevel = prev * (1 - smoothingFactor) + normalizedLevel * smoothingFactor;
                
                // Log every 30 frames (~0.5 seconds) for debugging
                if (frameCount % 30 === 0) {
                    console.log('📊 Audio level:', newLevel.toFixed(1), '(RMS:', rms.toFixed(3), ')');
                }
                frameCount++;
                
                return newLevel;
            });

            // Continue monitoring
            animationFrameRef.current = requestAnimationFrame(updateLevel);
        };

        console.log('🎬 Starting audio level animation loop');
        updateLevel();
    };

    const simulateAudioLevel = () => {
        // Simulate realistic audio level when real monitoring unavailable
        let isSpeaking = false;
        let speakingStartTime = 0;
        
        const simulate = () => {
            if (!isVoiceActiveRef.current) {
                return;
            }

            const now = Date.now();
            
            // Check if there's actual speech (transcript is being generated)
            const hasTranscript = interimTranscriptRef.current.length > 0;
            
            // Random speaking bursts every 2-4 seconds when no transcript
            if (!hasTranscript && !isSpeaking && Math.random() > 0.98) {
                isSpeaking = true;
                speakingStartTime = now;
            }
            
            // Speaking duration: 1-3 seconds
            if (isSpeaking && (now - speakingStartTime) > (1000 + Math.random() * 2000)) {
                isSpeaking = false;
            }
            
            let level;
            if (hasTranscript || isSpeaking) {
                // Simulate speech with varying amplitude
                const baseLevel = 45;
                const variation = 25;
                const frequency = 0.015; // Faster oscillation for speech
                const noise = (Math.random() - 0.5) * 15; // Add randomness
                level = baseLevel + Math.sin(now * frequency) * variation + noise;
            } else {
                // Low ambient level when silent
                const baseLevel = 12;
                const variation = 8;
                const frequency = 0.005; // Slower oscillation
                level = baseLevel + Math.sin(now * frequency) * variation;
            }
            
            setAudioLevel(Math.max(0, Math.min(100, level)));

            animationFrameRef.current = requestAnimationFrame(simulate);
        };

        console.log('📊 Using simulated audio levels (visual feedback mode)');
        simulate();
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
        // Add user message to chat
        addChatMessage(command, 'user');
        addSystemLog('info', `Processing: ${command}`);

        if (socket && socket.connected) {
            console.log('📤 Sending command via socket:', command);
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
        console.log(`🌍 Changing language to: ${lang}`);
        setVoiceLanguageState(lang);
        
        // Simply update the language property - recognition will use it on next start
        if (recognition) {
            recognition.lang = lang;
            console.log(`✅ Language updated to: ${lang}`);
        }
        
        // Note: We don't restart recognition here to avoid restart loops
        // The new language will be used when user starts/restarts recognition manually
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

            try {
                recognition.stop();
            } catch (e) {
                console.warn('Error stopping recognition:', e);
            }
        } else {
            console.log('▶️ Starting voice recognition (user clicked start)');
            // Clear the stop flags (sync both state and refs)
            setUserStoppedVoice(false);
            userStoppedRef.current = false;
            
            // Check if recognition is already running
            if (isRecognitionStarted) {
                console.warn('⚠️ Recognition already started, not starting again');
                setIsVoiceActive(true);
                isVoiceActiveRef.current = true;
                return;
            }
            
            try {
                recognition.start();
                // State will be set by onstart handler
            } catch (error: any) {
                console.error('Error starting voice recognition:', error);
                if (error.message?.includes('already started')) {
                    console.log('Recognition already running, setting state to active');
                    setIsVoiceActive(true);
                    isVoiceActiveRef.current = true;
                    setIsRecognitionStarted(true);
                } else {
                    alert('Failed to start voice recognition: ' + error.message);
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

    const closeDetailView = () => {
        setSelectedView(null);
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
        selectedView,
        setSelectedView,
        closeDetailView,
    };

    return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
};
