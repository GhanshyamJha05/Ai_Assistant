import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Loader } from 'lucide-react';

interface VoiceControlsProps {
    isListening: boolean;
    voiceState: 'idle' | 'listening' | 'processing' | 'speaking' | 'error';
    onToggleListening: () => void;
    disabled?: boolean;
}

export default function VoiceControls({
    isListening,
    voiceState,
    onToggleListening,
    disabled = false
}: VoiceControlsProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const animationRef = useRef<number>();

    // Waveform animation
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let amplitude = 0;
        const targetAmplitude = isListening ? 40 : 0;

        const animate = () => {
            // Smooth amplitude transition
            amplitude += (targetAmplitude - amplitude) * 0.1;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (amplitude > 0.5) {
                const centerY = canvas.height / 2;
                const barCount = 50;
                const barWidth = canvas.width / barCount;

                ctx.fillStyle = isListening ? '#3b82f6' : '#6b7280';

                for (let i = 0; i < barCount; i++) {
                    const height = Math.sin(Date.now() * 0.003 + i * 0.5) * amplitude + amplitude;
                    const x = i * barWidth;
                    const y = centerY - height / 2;

                    ctx.fillRect(x, y, barWidth - 2, height);
                }
            }

            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [isListening]);

    const getStateInfo = () => {
        switch (voiceState) {
            case 'listening':
                return { text: 'Listening...', color: 'text-blue-600', bg: 'bg-blue-50' };
            case 'processing':
                return { text: 'Processing...', color: 'text-yellow-600', bg: 'bg-yellow-50' };
            case 'speaking':
                return { text: 'Speaking...', color: 'text-green-600', bg: 'bg-green-50' };
            case 'error':
                return { text: 'Error', color: 'text-red-600', bg: 'bg-red-50' };
            default:
                return { text: 'Ready', color: 'text-gray-600', bg: 'bg-gray-50' };
        }
    };

    const stateInfo = getStateInfo();

    return (
        <div className="voice-controls">
            {/* Waveform Visualizer */}
            <div className="mb-6">
                <canvas
                    ref={canvasRef}
                    width={600}
                    height={100}
                    className="w-full h-24 rounded-lg bg-gray-900/5"
                />
            </div>

            {/* Status Badge */}
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${stateInfo.bg} ${stateInfo.color} mb-6`}>
                {voiceState === 'processing' && <Loader className="w-4 h-4 animate-spin" />}
                <span className="font-medium text-sm">{stateInfo.text}</span>
            </div>

            {/* Main Mic Button */}
            <button
                onClick={onToggleListening}
                disabled={disabled || voiceState === 'processing'}
                className={`
          relative w-20 h-20 rounded-full flex items-center justify-center
          transition-all duration-300 transform hover:scale-110
          ${isListening
                        ? 'bg-gradient-to-br from-red-500 to-red-600 shadow-lg shadow-red-500/50'
                        : 'bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/50'
                    }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-xl'}
        `}
            >
                {isListening ? (
                    <MicOff className="w-10 h-10 text-white" />
                ) : (
                    <Mic className="w-10 h-10 text-white" />
                )}

                {isListening && (
                    <span className="absolute -top-2 -right-2 flex h-4 w-4">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500"></span>
                    </span>
                )}
            </button>

            {/* Helper Text */}
            <p className="mt-4 text-sm text-gray-600">
                {isListening ? 'Click to stop listening' : 'Click to start listening'}
            </p>
        </div>
    );
}
