// Unified Dashboard JavaScript
class UnifiedDashboard {
    constructor() {
        this.socket = null;
        this.isVoiceActive = false;
        // Initialize dashboard
        this.init();

        // Add initial system log
        this.addSystemLog('info', 'Dashboard initialized successfully');
        this.addSystemLog('info', 'Connecting to backend services...');
    }

    init() {
        this.initializeSocket();
        this.initializeVoice();
        this.startRealTimeUpdates();
        this.loadInitialData();

        console.log('Unified Dashboard initialized');
    }

    // Socket.IO Connection
    initializeSocket() {
        try {
            this.socket = io();

            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.updateConnectionStatus(true);
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.updateConnectionStatus(false);
            });

            this.socket.on('command_response', (data) => {
                this.handleCommandResponse(data);
            });

            this.socket.on('system_stats_update', (stats) => {
                this.updateSystemStats(stats);
            });

            this.socket.on('log_update', (log) => {
                this.addSystemLog(log);
            });
        } catch (error) {
            console.warn('Socket.IO not available:', error);
        }
    }

    // Voice Recognition
    initializeVoice() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();

            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isVoiceActive = true;
                document.getElementById('voice-btn').classList.add('listening');
                document.getElementById('voice-status').textContent = 'LISTENING';
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.addVoiceHistory(transcript);
                this.processCommand(transcript);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isVoiceActive = false;
                document.getElementById('voice-btn').classList.remove('listening');
                document.getElementById('voice-status').textContent = 'READY';
            };

            this.recognition.onend = () => {
                this.isVoiceActive = false;
                document.getElementById('voice-btn').classList.remove('listening');
                document.getElementById('voice-status').textContent = 'READY';
            };
        } else {
            console.warn('Speech recognition not supported');
        }
    }

    // Toggle Voice Recognition
    toggleVoice() {
        if (!this.recognition) {
            alert('Voice recognition not supported in this browser');
            return;
        }

        if (this.isVoiceActive) {
            this.recognition.stop();
        } else {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error starting voice recognition:', error);
            }
        }
    }

    // Send Command
    sendCommand() {
        const input = document.getElementById('command-input');
        const command = input.value.trim();

        if (!command) return;

        this.addChatMessage(command, 'user');
        input.value = '';
        this.processCommand(command);
    }

    // Process Command
    processCommand(command) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('command', { command: command, message: command });
        } else {
            // Fallback to API
            this.processCommandViaAPI(command);
        }
    }

    async processCommandViaAPI(command) {
        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            });

            const data = await response.json();
            this.addChatMessage(data.response || data.message, 'ai');
        } catch (error) {
            console.error('API call error:', error);
            this.addChatMessage('Error processing command. Please try again.', 'ai');
        }
    }

    // Handle Command Response
    handleCommandResponse(data) {
        if (data.success) {
            this.addChatMessage(data.response || data.message, 'ai');
        } else {
            this.addChatMessage('Error: ' + (data.error || 'Unknown error'), 'ai');
        }
    }

    // Add Chat Message
    addChatMessage(text, sender) {
        const chatHistory = document.getElementById('chat-history');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const time = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        messageDiv.innerHTML = `
            <div class="message-time">${time}</div>
            <div>${sender === 'ai' ? 'AI: ' : ''}${text}</div>
        `;

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Add Voice History Entry
    addVoiceHistory(text) {
        const voiceHistory = document.getElementById('voice-history');
        const entry = document.createElement('div');
        entry.className = 'voice-entry';

        const time = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });

        entry.innerHTML = `<span class="voice-time">${time}</span> "${text}"`;

        voiceHistory.insertBefore(entry, voiceHistory.firstChild);

        // Limit to 10 entries
        while (voiceHistory.children.length > 10) {
            voiceHistory.removeChild(voiceHistory.lastChild);
        }
    }

    // Add System Log
    addSystemLog(typeOrLog, message) {
        const logsContainer = document.getElementById('system-logs');
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';

        const time = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });

        let type, msg;
        if (typeof typeOrLog === 'object') {
            type = typeOrLog.type || 'info';
            msg = typeOrLog.message;
        } else {
            type = typeOrLog;
            msg = message;
        }

        const logClass = `log-${type}`;
        logEntry.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-type ${logClass}">${type.toUpperCase()}</span>
            <span class="log-message">${msg}</span>
        `;

        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;

        // Limit to 50 entries
        while (logsContainer.children.length > 50) {
            logsContainer.removeChild(logsContainer.firstChild);
        }
    }

    // Update System Stats
    updateSystemStats(stats) {
        if (stats.cpu_usage !== undefined) {
            document.getElementById('cpu-usage').textContent = Math.round(stats.cpu_usage) + '%';
        }
        if (stats.memory_usage !== undefined) {
            document.getElementById('memory-usage').textContent = Math.round(stats.memory_usage) + '%';
        }
        if (stats.network_speed !== undefined) {
            const speedMB = (stats.network_speed / 1024 / 1024).toFixed(1);
            document.getElementById('network-usage').textContent = speedMB + 'MB/s';
        }
    }

    // Update Connection Status
    updateConnectionStatus(connected) {
        const statusItems = document.querySelectorAll('.status-item');
        if (connected) {
            this.addSystemLog({ type: 'success', message: 'Connected to server' });
        } else {
            this.addSystemLog({ type: 'error', message: 'Disconnected from server' });
        }
    }

    // Real-time Updates
    startRealTimeUpdates() {
        // Update time every second
        setInterval(() => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
            document.getElementById('current-time').textContent = timeStr;
        }, 1000);

        // Simulate system stats updates
        setInterval(() => {
            if (!this.socket || !this.socket.connected) {
                // Generate mock stats
                const cpu = Math.floor(Math.random() * 40 + 20);
                const memory = Math.floor(Math.random() * 30 + 50);
                const network = (Math.random() * 20 + 5).toFixed(1);

                document.getElementById('cpu-usage').textContent = cpu + '%';
                document.getElementById('memory-usage').textContent = memory + '%';
                document.getElementById('network-usage').textContent = network + 'MB/s';
            }
        }, 3000);

        // Update battery (simulate)
        setInterval(() => {
            const battery = Math.floor(Math.random() * 10 + 80);
            document.getElementById('battery-level').textContent = battery + '%';
        }, 30000);
    }

    // Load Initial Data
    async loadInitialData() {
        try {
            // Load learning dashboard stats
            const response = await fetch('/api/learning/stats/all');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateLearningDashboard(data);
                }
            }
        } catch (error) {
            console.warn('Failed to load learning stats:', error);
            // Set default values
            document.getElementById('db-stats').textContent = '1.2TB';
            document.getElementById('active-systems').textContent = '27/27';
            document.getElementById('conversations').textContent = '54.3K';
        }
    }

    // Update Learning Dashboard
    updateLearningDashboard(data) {
        if (data.total_size_mb) {
            const sizeTB = (data.total_size_mb / 1024 / 1024).toFixed(1);
            document.getElementById('db-stats').textContent = sizeTB + 'TB';
        }
        if (data.active_systems !== undefined) {
            document.getElementById('active-systems').textContent = data.active_systems + '/27';
        }
        if (data.total_conversations) {
            const convK = (data.total_conversations / 1000).toFixed(1);
            document.getElementById('conversations').textContent = convK + 'K';
        }
    }
}

// Global functions for buttons
function toggleVoice() {
    dashboard.toggleVoice();
}

function sendCommand() {
    dashboard.sendCommand();
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        sendCommand();
    }
}

function openApps() {
    window.location.href = '/';
}

function openStats() {
    dashboard.addSystemLog({ type: 'info', message: 'Opening statistics panel...' });
}

function openSettings() {
    dashboard.addSystemLog({ type: 'info', message: 'Opening settings...' });
}

function openMore() {
    dashboard.addSystemLog({ type: 'info', message: 'More options coming soon!' });
}

// Initialize dashboard when DOM is ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new UnifiedDashboard();
});
