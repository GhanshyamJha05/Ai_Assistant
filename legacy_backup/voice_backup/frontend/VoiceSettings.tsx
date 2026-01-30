import { useState } from 'react';
import { Play, Settings as SettingsIcon, ChevronDown, ChevronUp } from 'lucide-react';

interface VoiceOption {
    id: string;
    name: string;
    gender: 'male' | 'female';
    accent: string;
    language: string;
    description: string;
    personality: string;
}

interface VoiceSettingsProps {
    availableVoices: VoiceOption[];
    selectedVoice: string;
    onVoiceChange: (voiceId: string) => void;
    onPreviewVoice: (voiceId: string) => void;
    previewingVoice: string | null;
}

export default function VoiceSettings({
    availableVoices,
    selectedVoice,
    onVoiceChange,
    onPreviewVoice,
    previewingVoice
}: VoiceSettingsProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    const selectedVoiceInfo = availableVoices.find(v => v.id === selectedVoice);

    return (
        <div className="voice-settings bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Header */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <SettingsIcon className="w-5 h-5 text-gray-600" />
                    <div className="text-left">
                        <h3 className="font-semibold text-gray-900">Assistant Voice</h3>
                        <p className="text-sm text-gray-600">
                            {selectedVoiceInfo?.name || 'No voice selected'} - {selectedVoiceInfo?.description}
                        </p>
                    </div>
                </div>
                {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
            </button>

            {/* Voice Selection Grid */}
            {isExpanded && (
                <div className="p-4 border-t border-gray-200 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                        {availableVoices.map((voice) => (
                            <div
                                key={voice.id}
                                className={`
                  p-4 rounded-lg border-2 transition-all cursor-pointer
                  ${selectedVoice === voice.id
                                        ? 'border-blue-500 bg-blue-50'
                                        : 'border-gray-200 bg-white hover:border-blue-300'
                                    }
                `}
                                onClick={() => onVoiceChange(voice.id)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h4 className="font-semibold text-gray-900">{voice.name}</h4>
                                            <span className={`
                        px-2 py-0.5 text-xs rounded-full
                        ${voice.gender === 'female' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'}
                      `}>
                                                {voice.gender}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600 mb-1">{voice.description}</p>
                                        <p className="text-xs text-gray-500">
                                            {voice.accent} • {voice.personality}
                                        </p>
                                    </div>

                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onPreviewVoice(voice.id);
                                        }}
                                        disabled={previewingVoice === voice.id}
                                        className="ml-3 p-2 rounded-full hover:bg-blue-100 text-blue-600 transition-colors disabled:opacity-50"
                                        title="Preview voice"
                                    >
                                        {previewingVoice === voice.id ? (
                                            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                                        ) : (
                                            <Play className="w-5 h-5" />
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
