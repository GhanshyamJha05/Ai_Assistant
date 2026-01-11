import { motion } from 'framer-motion';
import { Mic, Volume2, Languages, Clock } from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';

const VoiceDetail = () => {
  const { voiceCommands, isVoiceActive, toggleVoice, alwaysActive, toggleAlwaysActive } = useDashboard();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-white mb-2">Voice Control</h3>
          <p className="text-[#9CA3AF]">Manage voice commands and settings</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={toggleVoice}
            className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
              isVoiceActive 
                ? 'bg-[#EF4444]/20 text-[#EF4444] hover:bg-[#EF4444]/30' 
                : 'bg-[#10B981]/20 text-[#10B981] hover:bg-[#10B981]/30'
            }`}
          >
            <Mic className="w-4 h-4" />
            {isVoiceActive ? 'Stop Listening' : 'Start Listening'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Voice Settings</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#3B82F6]/20 rounded">
                  <Mic className="w-5 h-5 text-[#3B82F6]" />
                </div>
                <div>
                  <p className="text-white font-medium">Always Active Mode</p>
                  <p className="text-xs text-[#9CA3AF]">Listen for wake word continuously</p>
                </div>
              </div>
              <button 
                onClick={toggleAlwaysActive}
                className={`px-4 py-2 rounded-lg transition-all ${
                  alwaysActive 
                    ? 'bg-[#10B981]/20 text-[#10B981]' 
                    : 'bg-[#6B7280]/20 text-[#9CA3AF]'
                }`}
              >
                {alwaysActive ? 'ON' : 'OFF'}
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#F59E0B]/20 rounded">
                  <Languages className="w-5 h-5 text-[#F59E0B]" />
                </div>
                <div>
                  <p className="text-white font-medium">Language</p>
                  <p className="text-xs text-[#9CA3AF]">English (US)</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors">
                Change
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#8B5CF6]/20 rounded">
                  <Volume2 className="w-5 h-5 text-[#8B5CF6]" />
                </div>
                <div>
                  <p className="text-white font-medium">Voice Feedback</p>
                  <p className="text-xs text-[#9CA3AF]">Audio responses enabled</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-[#10B981]/20 text-[#10B981] rounded-lg">
                ON
              </button>
            </div>
          </div>
        </div>

        <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Voice Statistics</h4>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-[#9CA3AF]">Commands Today</span>
                <span className="text-white font-semibold">{voiceCommands.length}</span>
              </div>
              <div className="h-2 bg-[#2A2D35] rounded-full overflow-hidden">
                <div className="h-full bg-[#3B82F6]" style={{ width: '70%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-[#9CA3AF]">Recognition Accuracy</span>
                <span className="text-white font-semibold">94%</span>
              </div>
              <div className="h-2 bg-[#2A2D35] rounded-full overflow-hidden">
                <div className="h-full bg-[#10B981]" style={{ width: '94%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-[#9CA3AF]">Response Time</span>
                <span className="text-white font-semibold">0.8s avg</span>
              </div>
              <div className="h-2 bg-[#2A2D35] rounded-full overflow-hidden">
                <div className="h-full bg-[#F59E0B]" style={{ width: '85%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Recent Voice Commands</h4>
        <div className="space-y-2 max-h-[300px] overflow-y-auto">
          {voiceCommands.length === 0 ? (
            <div className="text-center py-8">
              <Mic className="w-12 h-12 text-[#3B82F6] mx-auto mb-3 opacity-50" />
              <p className="text-[#9CA3AF]">No voice commands yet</p>
            </div>
          ) : (
            voiceCommands.map((command, index) => (
              <motion.div
                key={command.id}
                className="flex items-center gap-3 p-3 bg-[#2A2D35] rounded-lg hover:bg-[#3A3D45] transition-colors"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Mic className="w-4 h-4 text-[#3B82F6]" />
                <p className="flex-1 text-white">{command.command}</p>
                <span className="text-xs text-[#6B7280] flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {command.time}
                </span>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default VoiceDetail;
