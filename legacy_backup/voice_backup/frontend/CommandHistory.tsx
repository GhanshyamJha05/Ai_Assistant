import { MessageSquare, RefreshCw } from 'lucide-react';

interface CommandHistoryItem {
    id: string;
    timestamp: number;
    userText: string;
    assistantResponse: string;
    confidence?: number;
}

interface CommandHistoryProps {
    history: CommandHistoryItem[];
    onClear?: () => void;
}

export default function CommandHistory({ history, onClear }: CommandHistoryProps) {
    if (history.length === 0) {
        return (
            <div className="text-center py-8 text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No command history yet</p>
                <p className="text-sm mt-1">Start talking to see your conversation here</p>
            </div>
        );
    }

    return (
        <div className="command-history">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                    Command History ({history.length})
                </h3>
                {onClear && history.length > 0 && (
                    <button
                        onClick={onClear}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Clear
                    </button>
                )}
            </div>

            {/* History List */}
            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {[...history].reverse().map((item) => (
                    <div
                        key={item.id}
                        className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                    >
                        {/* Timestamp */}
                        <div className="text-xs text-gray-500 mb-2">
                            {new Date(item.timestamp).toLocaleTimeString()}
                            {item.confidence && (
                                <span className="ml-2">
                                    • Confidence: {(item.confidence * 100).toFixed(0)}%
                                </span>
                            )}
                        </div>

                        {/* User Command */}
                        <div className="mb-3">
                            <div className="flex items-start gap-2">
                                <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-700">You said:</p>
                                    <p className="text-gray-900 mt-1">{item.userText}</p>
                                </div>
                            </div>
                        </div>

                        {/* Assistant Response */}
                        <div className="pl-4 border-l-2 border-green-200">
                            <div className="flex items-start gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 flex-shrink-0" />
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-700">Assistant:</p>
                                    <p className="text-gray-900 mt-1">{item.assistantResponse}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
