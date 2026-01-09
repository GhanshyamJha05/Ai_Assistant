import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

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

const ChatVoiceHistory = () => {
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const voiceScrollRef = useRef<HTMLDivElement>(null);

  const [chatMessages] = useState<Message[]>([
    { id: 1, type: 'user', text: 'Analyze system performance', time: '14:23' },
    { id: 2, type: 'ai', text: 'System running optimally. All metrics within normal parameters.', time: '14:23' },
    { id: 3, type: 'user', text: 'Show recent logs', time: '14:25' },
    { id: 4, type: 'ai', text: 'Displaying last 50 system logs from the past hour.', time: '14:25' },
  ]);

  const [voiceCommands] = useState<VoiceCommand[]>([
    { id: 1, command: 'Start monitoring', time: '14:20' },
    { id: 2, command: 'Check system status', time: '14:22' },
    { id: 3, command: 'Run diagnostics', time: '14:24' },
    { id: 4, command: 'Generate report', time: '14:26' },
  ]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="grid grid-cols-2 divide-x divide-[#1F2228]">
        <div className="p-4">
          <h3 className="text-sm font-medium text-white mb-3">Chat History</h3>
          <div
            ref={chatScrollRef}
            className="space-y-3 max-h-[280px] overflow-y-auto scrollbar-thin scrollbar-thumb-[#3B82F6] scrollbar-track-[#1F2228]"
          >
            {chatMessages.map((message, index) => (
              <motion.div
                key={message.id}
                className={`${
                  message.type === 'user'
                    ? 'bg-[#3B82F6]/15 ml-auto'
                    : 'bg-[#1F2228]'
                } p-3 rounded-lg max-w-[90%]`}
                initial={{ opacity: 0, x: message.type === 'user' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <p className="text-xs text-white mb-1">{message.text}</p>
                <span className="text-[10px] text-[#6B7280]">{message.time}</span>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="p-4">
          <h3 className="text-sm font-medium text-white mb-3">Voice History</h3>
          <div
            ref={voiceScrollRef}
            className="space-y-2.5 max-h-[280px] overflow-y-auto scrollbar-thin scrollbar-thumb-[#3B82F6] scrollbar-track-[#1F2228]"
          >
            {voiceCommands.map((command, index) => (
              <motion.div
                key={command.id}
                className="p-3 bg-[#1F2228] rounded-lg hover:bg-[#1F2228]/80 transition-colors cursor-pointer group"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02 }}
              >
                <p className="text-xs text-[#9CA3AF] group-hover:text-white transition-colors">
                  {command.command}
                </p>
                <span className="text-[10px] text-[#6B7280] mt-1 block">{command.time}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatVoiceHistory;
