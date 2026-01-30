import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

// Import sub-components
import VoiceControls from './VoiceControls';
import VoiceSettings from './VoiceSettings';
import CommandHistory from './CommandHistory';

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking' | 'error';

interface CommandHistoryItem {
  id: string;
  timestamp: number;
  userText: string;
  assistantResponse: string;
  confidence?: number;
}

interface VoiceOption {
  id: string;
  name: string;
  gender: 'male' | 'female';
  accent: string;
  language: string;
  description: string;
  personality: string;
}

const VoiceInterface = () => {
  // State
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [commandHistory, setCommandHistory] = useState<CommandHistoryItem[]>([]);
  const [confidence, setConfidence] = useState(0);
  const [availableVoices, setAvailableVoices] = useState<VoiceOption[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>('en-US-AriaNeural');
  const [previewingVoice, setPreviewingVoice] = useState<string | null>(null);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);

  // WebSocket connection
  useEffect(() => {
    const socketInstance = io();
    setSocket(socketInstance);

    socketInstance.on('connect', () => {
      setIsConnected(true);
      console.log('Voice interface connected');
      fetchCommandHistory();
    });

    socketInstance.on('disconnect', () => setIsConnected(false));

    socketInstance.on('voice_transcript', (data) => {
      setTranscript(data.text);
      setInterimTranscript('');
      setVoiceState('processing');
      setConfidence(data.confidence || 0.8);
    });

    socketInstance.on('voice_partial_transcript', (data) => {
      setInterimTranscript(data.text);
    });

    socketInstance.on('voice_response', (data) => {
      setResponse(data.response);
      setVoiceState('speaking');

      const newItem: CommandHistoryItem = {
        id: Date.now().toString(),
        timestamp: Date.now(),
        userText: transcript,
        assistantResponse: data.response,
        confidence
      };
      setCommandHistory(prev => [newItem, ...prev.slice(0, 9)]);

      setTimeout(() => setVoiceState('idle'), 2000);
    });

    return () => {
      socketInstance.disconnect();
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  // Fetch command history
  const fetchCommandHistory = async () => {
    try {
      const response = await fetch('/api/voice/history');
      if (response.ok) {
        const history = await response.json();
        setCommandHistory(history);
      }
    } catch (error) {
      console.error('Failed to fetch command history:', error);
    }
  };

  // Fetch available voices
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const response = await fetch('/api/voice/list');
        if (response.ok) {
          const data = await response.json();
          setAvailableVoices(data.voices || []);

          const savedVoice = localStorage.getItem('selectedVoice');
          setSelectedVoice(savedVoice || data.default || 'en-US-AriaNeural');
        }
      } catch (error) {
        console.error('Failed to fetch voices:', error);
      }
    };

    fetchVoices();
  }, []);

  // Preview voice
  const previewVoice = async (voiceId: string) => {
    if (previewingVoice) return;

    setPreviewingVoice(voiceId);
    try {
      const response = await fetch('/api/voice/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voiceId })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.audio_data) {
          const audio = new Audio(data.audio_data);
          audio.play();
          audio.onended = () => setPreviewingVoice(null);
        }
      } else {
        setPreviewingVoice(null);
      }
    } catch (error) {
      console.error('Failed to preview voice:', error);
      setPreviewingVoice(null);
    }
  };

  // Handle voice selection
  const handleVoiceChange = (voiceId: string) => {
    setSelectedVoice(voiceId);
    localStorage.setItem('selectedVoice', voiceId);
  };

  // Toggle listening
  const toggleListening = async () => {
    if (isListening) {
      // Stop listening
      setIsListening(false);
      setVoiceState('idle');

      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      if (socket) {
        socket.emit('voice_stop');
      }
    } else {
      // Start listening
      setIsListening(true);
      setVoiceState('listening');
      setTranscript('');
      setInterimTranscript('');

      // Try Web Speech API first
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
          let final = '';
          let interim = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              final += transcript;
            } else {
              interim += transcript;
            }
          }

          if (final) {
            setTranscript(final);
            if (socket) {
              socket.emit('voice_command', { text: final, confidence: event.results[0][0].confidence });
            }
          }
          setInterimTranscript(interim);
        };

        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setVoiceState('error');
          setIsListening(false);
        };

        recognition.onend = () => {
          if (isListening) {
            recognition.start(); // Restart if still should be listening
          }
        };

        recognition.start();
        recognitionRef.current = recognition;
      } else {
        // Fallback: Use MediaRecorder and send to backend
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          const mediaRecorder = new MediaRecorder(stream);

          mediaRecorder.ondataavailable = (event) => {
            audioChunksRef.current.push(event.data);
          };

          mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            audioChunksRef.current = [];

            const reader = new FileReader();
            reader.onloadend = () => {
              if (socket) {
                socket.emit('audio_data', reader.result);
              }
            };
            reader.readAsDataURL(audioBlob);
          };

          mediaRecorder.start();
          mediaRecorderRef.current = mediaRecorder;

          if (socket) {
            socket.emit('voice_start');
          }
        } catch (error) {
          console.error('Microphone access error:', error);
          setVoiceState('error');
          setIsListening(false);
        }
      }
    }
  };

  // Clear history
  const clearHistory = () => {
    setCommandHistory([]);
  };

  return (
    <div className="voice-interface p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-8 text-white">
          <h1 className="text-3xl font-bold mb-2">Voice Assistant</h1>
          <p className="text-blue-100">
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'} •
            {isListening ? ' Listening...' : ' Ready'}
          </p>
        </div>

        {/* Main Content */}
        <div className="p-6 space-y-6">
          {/* Voice Controls */}
          <div className="flex flex-col items-center">
            <VoiceControls
              isListening={isListening}
              voiceState={voiceState}
              onToggleListening={toggleListening}
              disabled={!isConnected}
            />
          </div>

          {/* Transcript Display */}
          {(transcript || interimTranscript) && (
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Transcript:</h3>
              <p className="text-gray-900">
                {transcript}
                {interimTranscript && (
                  <span className="text-gray-400 italic"> {interimTranscript}</span>
                )}
              </p>
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h3 className="text-sm font-semibold text-blue-700 mb-2">Assistant:</h3>
              <p className="text-gray-900">{response}</p>
            </div>
          )}

          {/* Voice Settings */}
          <VoiceSettings
            availableVoices={availableVoices}
            selectedVoice={selectedVoice}
            onVoiceChange={handleVoiceChange}
            onPreviewVoice={previewVoice}
            previewingVoice={previewingVoice}
          />

          {/* Command History */}
          <div className="border-t border-gray-200 pt-6">
            <CommandHistory
              history={commandHistory}
              onClear={clearHistory}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceInterface;
