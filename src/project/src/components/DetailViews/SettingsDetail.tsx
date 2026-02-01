import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell, Lock, Palette, Globe, Database, Brain, Zap, DollarSign, Clock,
  Mic, Volume2, Shield, Download, Upload, RotateCcw, Save, Check, X,
  Cpu, MessageSquare, Key, Terminal, Server, Layers, Speaker, HardDrive, Activity, Wifi
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDashboard } from '../../contexts/DashboardContext';

// --- Interfaces matching app_settings.json ---

interface GeneralSettings {
  language: string;
  secondaryLanguage: string;
  enableHinglish: boolean;
  theme: string;
  animations: boolean;
  startOnBoot: boolean;
}

interface SecuritySettings {
  apiKeys: {
    googleGemini: string;
    openAI: string;
    anthropic: string;
    elevenLabs: string;
  };
  permissions: {
    allowFileDeletion: boolean;
    allowAppExecution: boolean;
    allowWebBrowsing: boolean;
    allowSystemControl: boolean;
  };
  encryption: {
    encryptDatabase: boolean;
    enablePinParams: boolean;
  };
}

interface AISettings {
  defaultProvider: string;
  defaultModel: string;
  temperature: number;
  maxTokens: number;
  contextWindow: number;
  safetySettings: {
    harassment: string;
    hateSpeech: string;
    sexuallyExplicit: string;
    dangerousContent: string;
  };
  localLlm: {
    enabled: boolean;
    modelPath: string;
    useGpu: boolean;
  };
}

interface VoiceSettings {
  tts: {
    engine: string;
    voice: string;
    rate: number;
    volume: number;
    useCache: boolean;
  };
  stt: {
    engine: string;
    model: string;
    sensitivity: number;
    language: string;
    continuous: boolean;
  };
  wakeWord: {
    enabled: boolean;
    phrases: string[];
    sensitivity: number;
  };
}

interface AutomationSettings {
  autoUpdate: boolean;
  autoBackup: string;
  maxHistorySize: number;
  smartHome: {
    enabled: boolean;
    provider: string;
  };
}

interface SystemSettings {
  logLevel: string;
  maxLogSizeMb: number;
  minimizeToTray: boolean;
  notifications: {
    desktop: boolean;
    sound: boolean;
  };
}

interface AppSettings {
  general: GeneralSettings;
  security: SecuritySettings;
  ai: AISettings;
  voice: VoiceSettings;
  automation: AutomationSettings;
  system: SystemSettings;
}

const AI_PROVIDERS = [
  { value: 'google', label: 'Google Gemini' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'local', label: 'Local LLM' }
];

const AI_MODELS: Record<string, string[]> = {
  google: ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
  openai: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
  local: ['llama-3-8b', 'mistral-7b', 'gemma-2b', 'tinyllama-1.1b']
};

// --- Component ---

const SettingsDetail = () => {
  const { systemStats } = useDashboard();
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<keyof AppSettings | 'all'>('general');

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:5000/api/settings/all');
      const data = await res.json();
      if (data.success) {
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (category: string) => {
    if (!settings) return;

    try {
      setSaving(true);
      const response = await fetch('http://localhost:5000/api/settings/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category,
          settings: settings[category as keyof AppSettings]
        })
      });

      const result = await response.json();
      if (result.success) {
        setSettings(result.settings); // Update local state with returned settings
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 2000);
      } else {
        alert('❌ Failed to save: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      alert('❌ Error saving: ' + error);
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = async (category?: string) => {
    if (!confirm(`Are you sure you want to reset ${category || 'all'} settings?`)) return;
    try {
      const response = await fetch('http://localhost:5000/api/settings/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category })
      });
      const result = await response.json();
      if (result.success) {
        setSettings(result.settings);
        alert('✅ Settings reset successfully');
      }
    } catch (error) {
      alert('❌ Error resetting: ' + error);
    }
  };

  // Helper to update state deeply
  const handleSettingChange = (category: string, path: string[], value: any) => {
    setSettings((prev: any) => {
      if (!prev) return null;
      // Copy root state
      const newState = { ...prev };

      // Navigate to the category
      // Now navigate down the path within the category
      let current = newState[category];

      // If path is empty, we are replacing the whole category (unlikely here)
      if (path.length === 0) {
        newState[category] = value;
        return newState;
      }

      for (let i = 0; i < path.length - 1; i++) {
        // If current level is array or object, copy it to modify
        if (Array.isArray(current[path[i]])) {
          current[path[i]] = [...current[path[i]]];
        } else {
          current[path[i]] = { ...current[path[i]] };
        }
        current = current[path[i]];
      }

      current[path[path.length - 1]] = value;
      return newState;
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#3B82F6] border-t-transparent mb-4"></div>
          <p className="text-[#9CA3AF]">Loading settings...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'general', label: 'General', icon: Globe },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'ai', label: 'AI & Models', icon: Brain },
    { id: 'voice', label: 'Voice', icon: Mic },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'system', label: 'System', icon: Server },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-20">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-white mb-2">Settings</h3>
          <p className="text-[#9CA3AF]">Configure your AI assistant preferences</p>
        </div>

        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 bg-[#10B981]/20 text-[#10B981] px-4 py-2 rounded-lg border border-[#10B981]/30"
          >
            <Check className="w-5 h-5" />
            <span>Saved successfully!</span>
          </motion.div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`
              flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-all whitespace-nowrap
              ${activeTab === tab.id
                ? 'bg-[#3B82F6] text-white shadow-lg shadow-[#3B82F6]/20'
                : 'bg-[#2A2D35] text-[#9CA3AF] hover:bg-[#3A3D45] hover:text-white'
              }
            `}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <motion.div
        key={activeTab as string}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="space-y-6"
      >
        {activeTab === 'voice' && (
          <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-20 text-center">
            <h1 className="text-6xl font-bold text-[#3B82F6] mb-4">✅ VISIBLE</h1>
            <p className="text-2xl text-[#10B981]">Changes are loading! HMR working!</p>
            <p className="text-lg text-white mt-4">Voice Settings will appear here</p>
          </div>
        )}

        {activeTab === 'system' && (
          <LiveMetrics stats={systemStats} />
        )}

        {settings && settings[activeTab as keyof AppSettings] && activeTab !== 'voice' && (
          <EditableSection
            key={activeTab} // Force re-render on tab change to reset path context
            title={tabs.find(t => t.id === activeTab)?.label || ''}
            data={settings[activeTab as keyof AppSettings]}
            category={activeTab as string}
            onChange={(path, val) => handleSettingChange(activeTab as string, path, val)}
            onSave={() => saveSettings(activeTab as string)}
            saving={saving}
          />
        )}
      </motion.div>
    </div>
  );
};

// --- Sub-components ---

const EditableSection = ({ title, data, category, onChange, onSave, saving }: {
  title: string,
  data: any,
  category: string,
  onChange: (path: string[], val: any) => void,
  onSave: () => void,
  saving: boolean
}) => {
  return (
    <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg flex flex-col h-full">
      <div className="p-6 border-b border-[#2A2D35] flex justify-between items-center sticky top-0 bg-[#1F2228] z-10 rounded-t-lg">
        <h4 className="text-xl font-semibold text-white">{title} Configuration</h4>

        <button
          onClick={onSave}
          disabled={saving}
          className="px-6 py-2 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-semibold disabled:opacity-50 flex items-center gap-2"
        >
          {saving ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" /> : <Save className="w-4 h-4" />}
          <span>Save Changes</span>
        </button>
      </div>

      <div className="p-6">
        <RecursiveFormRenderer data={data} onChange={onChange} path={[]} rootData={data} />
      </div>
    </div>
  );
};

const RecursiveFormRenderer = ({ data, onChange, path, rootData }: { data: any, onChange: (path: string[], val: any) => void, path: string[], rootData?: any }) => {
  // Use rootData to look up siblings if needed (like defaultProvider)
  // If rootData is not passed, use data (only works at top level)
  const contextData = rootData || data;

  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.entries(data).map(([key, value]) => {
        const currentPath = [...path, key];
        const label = key.replace(/([A-Z])/g, ' $1').trim();

        // Sub-section (nested object)
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          return (
            <div key={key} className="col-span-3 border border-[#3A3D45] p-4 rounded-lg bg-[#252830]/50">
              <h5 className="text-[#3B82F6] font-medium mb-3 capitalize flex items-center gap-2 text-sm">
                <Layers className="w-4 h-4" />
                {label}
              </h5>
              {/* Pass rootData down so children can access top-level context if needed (though tricky with recursion) */}
              {/* Actually simpler: just recursively render. Sibling lookups need to be done carefully. */}
              <RecursiveFormRenderer data={value} onChange={onChange} path={currentPath} rootData={contextData} />
            </div>
          );
        }

        // Special Handling: AI Provider Dropdown (Top Level)
        if (key === 'defaultProvider') {
          return (
            <div key={key} className="space-y-1.5">
              <label className="text-white text-xs font-medium capitalize block">{label}</label>
              <div className="relative">
                <select
                  value={String(value)}
                  onChange={(e) => onChange(currentPath, e.target.value)}
                  className="w-full p-2.5 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white text-sm focus:border-[#3B82F6] outline-none appearance-none cursor-pointer hover:border-[#3B82F6]/50 transition-colors"
                >
                  {AI_PROVIDERS.map((provider) => (
                    <option key={provider.value} value={provider.value}>{provider.label}</option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#9CA3AF] text-xs">▼</div>
              </div>
            </div>
          );
        }

        // Special Handling: TTS Voice Dropdown
        if (key === 'voice_id' && contextData.available_voices) {
          const availableVoices = contextData.available_voices;
          return (
            <div key={key} className="space-y-1.5">
              <label className="text-white text-xs font-medium capitalize block">TTS Voice</label>
              <div className="relative">
                <select
                  value={String(value)}
                  onChange={(e) => {
                    onChange(currentPath, e.target.value);
                    // Also update voice_name
                    const selectedVoice = availableVoices.find((v: any) => v.id === e.target.value);
                    if (selectedVoice) {
                      onChange([...path, 'voice_name'], selectedVoice.name);
                    }
                  }}
                  className="w-full p-2.5 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white text-sm focus:border-[#3B82F6] outline-none appearance-none cursor-pointer hover:border-[#3B82F6]/50 transition-colors"
                >
                  {availableVoices.map((voice: any) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} ({voice.gender}, {voice.accent})
                    </option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#9CA3AF] text-xs">▼</div>
              </div>
            </div>
          );
        }

        // Skip voice_name and available_voices from rendering (handled by voice_id)
        if (key === 'voice_name' || key === 'available_voices') {
          return null;
        }

        // Special Handling: STT Engine Dropdown
        if (key === 'engine' && path.includes('stt')) {
          const engines = [
            { value: 'vosk', label: 'Vosk (Offline, Fast)' },
            { value: 'whisper', label: 'Whisper (High Accuracy)' },
            { value: 'google', label: 'Google Cloud STT' }
          ];
          return (
            <div key={key} className="space-y-2">
              <label className="text-white text-sm font-medium capitalize block">STT Engine</label>
              <div className="relative">
                <select
                  value={String(value)}
                  onChange={(e) => onChange(currentPath, e.target.value)}
                  className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none appearance-none cursor-pointer hover:border-[#3B82F6]/50 transition-colors"
                >
                  {engines.map((engine) => (
                    <option key={engine.value} value={engine.value}>{engine.label}</option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#9CA3AF]">▼</div>
              </div>
            </div>
          );
        }


        // Special Handling: STT Model - only show for Vosk/Whisper
        if (key === 'model' && path.includes('stt')) {
          // Check if engine is Google (if so, don't show model field)
          const currentEngine = data['engine'] || 'vosk';
          if (currentEngine === 'google') {
            return null; // Hide model field for Google
          }

          return (
            <div key={key} className="space-y-1.5">
              <label className="text-white text-xs font-medium capitalize block">Model</label>
              <input
                type="text"
                value={String(value)}
                onChange={(e) => onChange(currentPath, e.target.value)}
                className="w-full p-2.5 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white text-sm focus:border-[#3B82F6] outline-none"
                placeholder={currentEngine === 'vosk' ? 'vosk-model-small-en-us-0.15' : 'whisper-medium'}
              />
              <p className="text-xs text-[#6B7280]">Required for {currentEngine === 'vosk' ? 'Vosk' : 'Whisper'}</p>
            </div>
          );
        }

        // Special Handling: AI Model Dropdown (Top Level)
        if (key === 'defaultModel') {
          // Look up 'defaultProvider' in the CURRENT data object (siblings)
          const currentProvider = data['defaultProvider'] || 'google';
          const availableModels = AI_MODELS[currentProvider] || [];

          return (
            <div key={key} className="space-y-2">
              <label className="text-white text-sm font-medium capitalize block">{label}</label>
              {availableModels.length > 0 ? (
                <div className="relative">
                  <select
                    value={String(value)}
                    onChange={(e) => onChange(currentPath, e.target.value)}
                    className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none appearance-none cursor-pointer hover:border-[#3B82F6]/50 transition-colors"
                  >
                    {availableModels.map((model) => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#9CA3AF]">▼</div>
                </div>
              ) : (
                <input
                  type="text"
                  value={String(value)}
                  onChange={(e) => onChange(currentPath, e.target.value)}
                  className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none"
                  placeholder="Enter model name"
                />
              )}
            </div>
          );
        }

        // Array (Simple comma separated for now)
        if (Array.isArray(value)) {
          // Safely convert array to string
          const arrayValue = value.filter(v => v != null).join(', ');

          return (
            <div key={key} className="space-y-2 col-span-1 md:col-span-2">
              <label className="text-white text-sm font-medium capitalize block">{label}</label>
              <input
                type="text"
                value={arrayValue}
                onChange={(e) => {
                  const newValue = e.target.value
                    .split(',')
                    .map(s => s.trim())
                    .filter(s => s.length > 0);
                  onChange(currentPath, newValue);
                }}
                className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none"
                placeholder="Comma separated values (e.g., hey daddy, hey assistant)"
              />
              <p className="text-xs text-[#6B7280]">Separate multiple values with commas</p>
            </div>
          );
        }

        // Boolean
        if (typeof value === 'boolean') {
          return (
            <label key={key} className="flex items-center gap-2.5 p-3 bg-[#2A2D35] rounded-lg cursor-pointer border border-[#3A3D45] hover:border-[#3B82F6]/50 transition-all group h-full">
              <div className="relative flex items-center">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => onChange(currentPath, e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-9 h-5 bg-[#1F2228] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#3B82F6]"></div>
              </div>
              <div>
                <span className="text-white text-sm font-medium capitalize block group-hover:text-[#3B82F6] transition-colors">{label}</span>
                <span className="text-[#9CA3AF] text-xs">{value ? 'Enabled' : 'Disabled'}</span>
              </div>
            </label>
          );
        }

        // Number
        if (typeof value === 'number') {
          return (
            <div key={key} className="space-y-2">
              <label className="text-white text-sm font-medium capitalize block">{label}</label>
              <input
                type="number"
                value={value}
                onChange={(e) => onChange(currentPath, parseFloat(e.target.value))}
                className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none"
              />
            </div>
          );
        }

        // String (Default)
        return (
          <div key={key} className="space-y-2">
            <label className="text-white text-sm font-medium capitalize block">{label}</label>
            <input
              type="text"
              value={String(value)}
              onChange={(e) => onChange(currentPath, e.target.value)}
              className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] outline-none"
            />
          </div>
        );
      })}
    </div>
  );
};

const LiveMetrics = ({ stats }: { stats: any }) => {
  if (!stats) return null;

  const metrics = [
    { label: 'CPU Load', value: `${stats.cpu}%`, icon: Cpu, color: '#3B82F6' },
    { label: 'Memory', value: `${stats.memory}%`, icon: HardDrive, color: '#10B981' },
    { label: 'Disk', value: `${stats.disk || 0}%`, icon: Database, color: '#8B5CF6' },
    { label: 'Network', value: stats.network, icon: Activity, color: '#F59E0B' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {metrics.map((m) => (
        <div key={m.label} className="bg-[#1F2228] border border-[#2A2D35] p-4 rounded-lg flex items-center gap-4">
          <div className="p-3 rounded-lg bg-[#2A2D35]" style={{ color: m.color }}>
            <m.icon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[#9CA3AF] text-xs uppercase font-medium">{m.label}</p>
            <p className="text-white text-xl font-bold">{m.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SettingsDetail;
