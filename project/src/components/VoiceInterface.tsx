import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { io, Socket } from 'socket.io-client';

const VoiceInterface = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const recognitionRef = useRef<any>(null);

  // Connect to WebSocket
  useEffect(() => {
    const socketInstance = io('http://localhost:5000', {
      withCredentials: true,
      transports: ['polling', 'websocket'],
      reconnection: true
    });

    socketInstance.on('connect', () => {
      setIsConnected(true);
      console.log('✅ Connected to backend');
    });

    socketInstance.on('disconnect', () => {
      setIsConnected(false);
      console.log('❌ Disconnected from backend');
    });

    socketInstance.on('voice_response', (data) => {
      console.log('📥 Response received:', data);
      setResponse(data.response);

      // Speak the response
      if (data.response && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.response);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
        console.log('🔊 Speaking:', data.response);
      }
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const toggleListening = () => {
    if (!isConnected) {
      alert('Not connected to backend!');
      return;
    }

    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser!');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }

      if (finalTranscript) {
        const text = finalTranscript.trim();
        setTranscript(text);
        console.log('📤 Sending command:', text);

        // Send to backend
        if (socket) {
          socket.emit('voice_command', {
            text: text,
            confidence: event.results[event.resultIndex][0].confidence || 0.9
          });
        }
      }
    };

    recognition.onerror = (event: any) => {
      console.error('🔴 Speech recognition error:', event.error);
    };

    recognition.onend = () => {
      console.log('Speech recognition ended');
    };

    recognition.start();
    setIsListening(true);
    console.log('🎤 Listening started');
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      console.log('🛑 Listening stopped');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">Voice Interface</h1>
        <p className="text-gray-400">
          {isConnected ? '✅ Connected' : '❌ Disconnected'}
        </p>
      </div>

      {/* Mic Button */}
      <button
        onClick={toggleListening}
        disabled={!isConnected}
        className={`w-32 h-32 rounded-full flex items-center justify-center transition-all ${isListening
            ? 'bg-red-500 hover:bg-red-600 scale-110'
            : 'bg-blue-500 hover:bg-blue-600'
          } ${!isConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {isListening ? (
          <MicOff size={48} className="text-white" />
        ) : (
          <Mic size={48} className="text-white" />
        )}
      </button>

      <p className="mt-4 text-lg">
        {isListening ? '🎤 Listening...' : 'Click to start'}
      </p>

      {/* Transcript */}
      {transcript && (
        <div className="mt-8 p-4 bg-gray-800 rounded-lg max-w-2xl">
          <h3 className="text-sm text-gray-400 mb-2">You said:</h3>
          <p className="text-white">{transcript}</p>
        </div>
      )}

      {/* Response */}
      {response && (
        <div className="mt-4 p-4 bg-blue-900 rounded-lg max-w-2xl">
          <h3 className="text-sm text-blue-300 mb-2">Assistant:</h3>
          <p className="text-white">{response}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceInterface;
