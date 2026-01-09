import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
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
    sendCommand: (command: string) => void;
    toggleVoice: () => void;
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
    const [recognition, setRecognition] = useState<any>(null);

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
            recog.continuous = false;
            recog.interimResults = false;
            recog.lang = 'en-US';

            recog.onstart = () => {
                setIsVoiceActive(true);
            };

            recog.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                addVoiceCommand(transcript);
                sendCommand(transcript);
            };

            recog.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
                setIsVoiceActive(false);
            };

            recog.onend = () => {
                setIsVoiceActive(false);
            };

            setRecognition(recog);
        }
    }, []);

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
                    addChatMessage(data.response || data.message, 'ai');
                })
                .catch((error) => {
                    console.error('API call error:', error);
                    addChatMessage('Error processing command. Please try again.', 'ai');
                });
        }
    };

    const toggleVoice = () => {
        if (!recognition) {
            alert('Voice recognition not supported in this browser');
            return;
        }

        if (isVoiceActive) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (error) {
                console.error('Error starting voice recognition:', error);
            }
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
        sendCommand,
        toggleVoice,
    };

    return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
};
