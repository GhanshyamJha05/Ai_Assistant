import { motion } from 'framer-motion';
import { Bell, Lock, Palette, Globe, Database, Brain, Zap, DollarSign, Clock, Mic, Volume2, Shield, Download, Upload, RotateCcw, Save, Check, X, Cpu, MessageSquare } from 'lucide-react';
import { useState, useEffect } from 'react';

interface Model {
  id: string;
  name: string;
  provider: string;
  tier: string;
  cost_per_1k_tokens: number;
  avg_latency_ms: number;
  max_tokens: number;
  capabilities: string[];
  description: string;
  priority: number;
}

interface Settings {
  appearance: {
    theme: string;
    accentColor: string;
    fontSize: string;
    language: string;
  };
  notifications: {
    pushNotifications: boolean;
    soundAlerts: boolean;
    emailNotifications: boolean;
    desktopNotifications: boolean;
  };
  privacy: {
    dataCollection: string;
    encryption: boolean;
    autoLock: string;
    twoFactorAuth: boolean;
  };
  voice: {
    engine: string;
    voice: string;
    speed: number;
    volume: number;
    wakeWord: string;
    continuousListening: boolean;
  };
  ai: {
    preferredModel: string;
    autoRoute: boolean;
    contextMemory: boolean;
    learningEnabled: boolean;
  };
  automation: {
    autoUpdate: boolean;
    backgroundTasks: boolean;
    autoBackup: string;
  };
}

const SettingsDetail = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [modelsByProvider, setModelsByProvider] = useState<Record<string, Model[]>>({});
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [showModelModal, setShowModelModal] = useState<boolean>(false);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showLocalAIModal, setShowLocalAIModal] = useState<boolean>(false);
  const [editCategory, setEditCategory] = useState<string>('');
  const [editData, setEditData] = useState<any>({});
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [localAIStatus, setLocalAIStatus] = useState<any>(null);
  const [localAILoading, setLocalAILoading] = useState<boolean>(false);

  useEffect(() => {
    console.log('Modal state changed:', showModelModal);
  }, [showModelModal]);

  useEffect(() => {
    loadAllSettings();
    loadLocalAIStatus();
  }, []);

  const loadLocalAIStatus = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/local_ai/status');
      const data = await res.json();
      setLocalAIStatus(data);
    } catch (error) {
      console.error('Failed to load local AI status:', error);
    }
  };

  const loadAllSettings = async () => {
    try {
      setLoading(true);
      const [modelsRes, settingsRes] = await Promise.all([
        fetch('http://localhost:5000/api/models/available'),
        fetch('http://localhost:5000/api/settings/all')
      ]);

      const modelsData = await modelsRes.json();
      const settingsData = await settingsRes.json();

      if (modelsData.success) {
        setModels(modelsData.models || []);
        setModelsByProvider(modelsData.by_provider || {});
      }

      if (settingsData.success) {
        setSettings(settingsData.settings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async (category: string, data: any) => {
    try {
      setSaving(true);
      const response = await fetch('http://localhost:5000/api/settings/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category,
          settings: data
        })
      });

      const result = await response.json();
      if (result.success) {
        setSettings(result.settings);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 2000);
        setShowEditModal(false);
        setShowModelModal(false);
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
        alert('✅ ' + result.message);
        loadAllSettings();
      }
    } catch (error) {
      alert('❌ Error resetting: ' + error);
    }
  };

  const exportSettings = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/settings/export');
      const result = await response.json();
      
      if (result.success) {
        const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `settings_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      alert('❌ Error exporting: ' + error);
    }
  };

  const importSettings = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      try {
        const text = await file.text();
        const importedSettings = JSON.parse(text);

        const response = await fetch('http://localhost:5000/api/settings/import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ settings: importedSettings })
        });

        const result = await response.json();
        if (result.success) {
          alert('✅ Settings imported successfully!');
          loadAllSettings();
        }
      } catch (error) {
        alert('❌ Error importing: ' + error);
      }
    };
    input.click();
  };

  const openEditModal = (category: string, data: any) => {
    setEditCategory(category);
    setEditData({ ...data });
    setShowEditModal(true);
  };

  const getProviderIcon = (provider: string) => {
    const icons: Record<string, string> = {
      'Google': '🔵',
      'OpenAI': '🟢',
      'Anthropic': '🟣'
    };
    return icons[provider] || '⚪';
  };

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      'fast': '#10B981',
      'standard': '#3B82F6',
      'advanced': '#8B5CF6'
    };
    return colors[tier] || '#6B7280';
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

  const settingsGroups = [
    {
      title: 'AI Model Selection',
      icon: Brain,
      color: '#3B82F6',
      category: 'ai',
      settings: [
        { label: 'Current Model', value: models.find(m => m.id === settings?.ai?.preferredModel)?.name || 'Gemini 2.0 Flash' },
        { label: 'Provider', value: models.find(m => m.id === settings?.ai?.preferredModel)?.provider || 'Google' },
        { label: 'Auto Routing', value: settings?.ai?.autoRoute ? 'Enabled' : 'Disabled' },
      ],
      action: () => setShowModelModal(true)
    },
    {
      title: 'Local AI (Private & Fast)',
      icon: Cpu,
      color: '#10B981',
      category: 'local_ai',
      settings: [
        { 
          label: 'Status', 
          value: localAIStatus?.initialized ? '🟢 Ready' : localAIStatus?.available ? '🟡 Not Loaded' : '🔴 Not Installed' 
        },
        { 
          label: 'Model', 
          value: localAIStatus?.model_info?.name || 'No model loaded' 
        },
        { 
          label: 'Speed', 
          value: localAIStatus?.stats?.avg_tokens_per_sec 
            ? `${Math.round(localAIStatus.stats.avg_tokens_per_sec)} tok/s` 
            : 'N/A' 
        },
      ],
      action: () => setShowLocalAIModal(true)
    },
    {
      title: 'Appearance',
      icon: Palette,
      color: '#3B82F6',
      category: 'appearance',
      settings: [
        { label: 'Theme', value: settings?.appearance?.theme || 'Dark' },
        { label: 'Accent Color', value: settings?.appearance?.accentColor || 'Blue' },
        { label: 'Font Size', value: settings?.appearance?.fontSize || 'Medium' },
      ],
      action: () => openEditModal('appearance', settings?.appearance)
    },
    {
      title: 'Notifications',
      icon: Bell,
      color: '#F59E0B',
      category: 'notifications',
      settings: [
        { label: 'Push Notifications', value: settings?.notifications?.pushNotifications ? 'Enabled' : 'Disabled' },
        { label: 'Sound Alerts', value: settings?.notifications?.soundAlerts ? 'Enabled' : 'Disabled' },
        { label: 'Email Notifications', value: settings?.notifications?.emailNotifications ? 'Enabled' : 'Disabled' },
      ],
      action: () => openEditModal('notifications', settings?.notifications)
    },
    {
      title: 'Privacy & Security',
      icon: Lock,
      color: '#EF4444',
      category: 'privacy',
      settings: [
        { label: 'Data Collection', value: settings?.privacy?.dataCollection || 'Minimal' },
        { label: 'Encryption', value: settings?.privacy?.encryption ? 'Enabled' : 'Disabled' },
        { label: 'Auto-Lock', value: settings?.privacy?.autoLock || '5 minutes' },
      ],
      action: () => openEditModal('privacy', settings?.privacy)
    },
    {
      title: 'Voice Settings',
      icon: Mic,
      color: '#10B981',
      category: 'voice',
      settings: [
        { label: 'Voice Engine', value: settings?.voice?.engine || 'edge_tts' },
        { label: 'Speed', value: `${(settings?.voice?.speed || 1.0)}x` },
        { label: 'Volume', value: `${Math.round((settings?.voice?.volume || 0.9) * 100)}%` },
      ],
      action: () => openEditModal('voice', settings?.voice)
    },
    {
      title: 'Automation',
      icon: Database,
      color: '#8B5CF6',
      category: 'automation',
      settings: [
        { label: 'Auto Update', value: settings?.automation?.autoUpdate ? 'Enabled' : 'Disabled' },
        { label: 'Background Tasks', value: settings?.automation?.backgroundTasks ? 'Enabled' : 'Disabled' },
        { label: 'Auto Backup', value: settings?.automation?.autoBackup || 'Daily' },
      ],
      action: () => openEditModal('automation', settings?.automation)
    },
  ];

  return (
    <div className="space-y-6">
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {settingsGroups.map((group, index) => (
          <motion.div
            key={group.title}
            className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6 hover:border-[#3B82F6]/50 transition-all"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${group.color}15` }}>
                <group.icon className="w-5 h-5" style={{ color: group.color }} strokeWidth={1.5} />
              </div>
              <h4 className="text-lg font-semibold text-white">{group.title}</h4>
            </div>

            <div className="space-y-3">
              {group.settings.map((setting, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-[#2A2D35] rounded-lg hover:bg-[#3A3D45] transition-colors">
                  <span className="text-[#9CA3AF] text-sm">{setting.label}</span>
                  <span className="text-white font-medium text-sm">{setting.value}</span>
                </div>
              ))}
            </div>

            <button 
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Button clicked for:', group.title);
                console.log('Action exists:', !!group.action);
                if (group.action) {
                  console.log('Calling action...');
                  group.action();
                }
              }}
              type="button"
              className="mt-4 w-full px-4 py-2 bg-[#3B82F6]/20 text-[#3B82F6] rounded-lg hover:bg-[#3B82F6]/30 transition-colors font-medium cursor-pointer"
            >
              Configure
            </button>
          </motion.div>
        ))}
      </div>

      <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Advanced Options</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button 
            onClick={exportSettings}
            className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export Data
          </button>
          <button 
            onClick={importSettings}
            className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium flex items-center justify-center gap-2"
          >
            <Upload className="w-4 h-4" />
            Import Settings
          </button>
          <button 
            onClick={() => resetSettings()}
            className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reset to Default
          </button>
          <button 
            onClick={() => resetSettings()}
            className="px-4 py-3 bg-[#EF4444]/20 text-[#EF4444] rounded-lg hover:bg-[#EF4444]/30 transition-colors font-medium"
          >
            Clear All Data
          </button>
        </div>
      </div>

      {/* Model Selection Modal */}
      {showModelModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-4" onClick={() => setShowModelModal(false)}>
          <motion.div 
            className="bg-[#1F2228] rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto border border-[#3B82F6]/30"
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="sticky top-0 bg-[#1F2228] border-b border-[#2A2D35] p-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-[#3B82F6]/20">
                  <Brain className="w-6 h-6 text-[#3B82F6]" strokeWidth={1.5} />
                </div>
                <div>
                  <h4 className="text-xl font-semibold text-white">🤖 AI Model Selection</h4>
                  <p className="text-sm text-[#9CA3AF]">Choose your preferred language model and provider</p>
                </div>
              </div>
              <button 
                onClick={() => setShowModelModal(false)}
                className="p-2 hover:bg-[#2A2D35] rounded-lg transition-colors"
              >
                <span className="text-2xl text-[#9CA3AF] hover:text-white">×</span>
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Auto-Route Toggle */}
              <div className="p-4 bg-[#2A2D35] rounded-lg border border-[#3A3D45]">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoRoute}
                    onChange={(e) => setAutoRoute(e.target.checked)}
                    className="w-5 h-5 rounded bg-[#1F2228] border-[#3A3D45] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
                  />
                  <div>
                    <span className="text-white font-medium">Enable Intelligent Model Routing</span>
                    <p className="text-sm text-[#9CA3AF]">Automatically select the best model based on your query</p>
                  </div>
                </label>
              </div>

              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#3B82F6] border-t-transparent"></div>
                  <p className="text-[#9CA3AF] mt-4">Loading models...</p>
                </div>
              ) : (
                <>
                  {/* Models by Provider */}
                  <div className="space-y-6">
                    {Object.entries(modelsByProvider).map(([provider, providerModels]) => (
                      <div key={provider} className="space-y-3">
                        <h5 className="text-lg font-semibold text-white flex items-center gap-2">
                          <span>{getProviderIcon(provider)}</span>
                          <span>{provider}</span>
                        </h5>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                          {providerModels.map((model) => (
                            <motion.div
                              key={model.id}
                              onClick={() => setSelectedModel(model.id)}
                              className={`
                                p-4 rounded-lg border-2 cursor-pointer transition-all
                                ${selectedModel === model.id 
                                  ? 'border-[#10B981] bg-[#10B981]/10 shadow-lg shadow-[#10B981]/20' 
                                  : 'border-[#3A3D45] bg-[#2A2D35] hover:border-[#3B82F6]/50'
                                }
                              `}
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <h6 className="text-white font-semibold">{model.name}</h6>
                                  <p className="text-xs text-[#9CA3AF] mt-1">{model.description}</p>
                                </div>
                                <span
                                  className="px-2 py-1 rounded text-xs font-bold uppercase"
                                  style={{
                                    backgroundColor: `${getTierColor(model.tier)}20`,
                                    color: getTierColor(model.tier)
                                  }}
                                >
                                  {model.tier}
                                </span>
                              </div>

                              <div className="grid grid-cols-3 gap-2 mt-3 text-xs">
                                <div className="flex items-center gap-1 text-[#9CA3AF]">
                                  <DollarSign className="w-3 h-3" />
                                  <span>${model.cost_per_1k_tokens}/1K</span>
                                </div>
                                <div className="flex items-center gap-1 text-[#9CA3AF]">
                                  <Zap className="w-3 h-3" />
                                  <span>{model.avg_latency_ms}ms</span>
                                </div>
                                <div className="flex items-center gap-1 text-[#9CA3AF]">
                                  <Clock className="w-3 h-3" />
                                  <span>{model.max_tokens}</span>
                                </div>
                              </div>

                              <div className="flex flex-wrap gap-1 mt-3">
                                {model.capabilities.map((cap) => (
                                  <span
                                    key={cap}
                                    className="px-2 py-0.5 bg-[#3B82F6]/20 text-[#3B82F6] text-xs rounded-full"
                                  >
                                    {cap}
                                  </span>
                                ))}
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Save Button */}
                  <div className="sticky bottom-0 bg-[#1F2228] border-t border-[#2A2D35] pt-4 flex gap-3">
                    <button
                      onClick={() => settings && saveSettings('ai', settings.ai)}
                      disabled={saving}
                      className="flex-1 px-6 py-3 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {saving ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                          <span>Saving...</span>
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4" />
                          <span>Save Model Preference</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => setShowModelModal(false)}
                      className="px-6 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-semibold"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Edit Settings Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-4" onClick={() => setShowEditModal(false)}>
          <motion.div 
            className="bg-[#1F2228] rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-[#3B82F6]/30"
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="sticky top-0 bg-[#1F2228] border-b border-[#2A2D35] p-6 flex items-center justify-between">
              <h4 className="text-xl font-semibold text-white capitalize">{editCategory} Settings</h4>
              <button 
                onClick={() => setShowEditModal(false)}
                className="p-2 hover:bg-[#2A2D35] rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-[#9CA3AF] hover:text-white" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {Object.entries(editData).map(([key, value]) => (
                <div key={key} className="space-y-2">
                  <label className="text-white font-medium capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</label>
                  {typeof value === 'boolean' ? (
                    <label className="flex items-center gap-3 p-3 bg-[#2A2D35] rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => setEditData({ ...editData, [key]: e.target.checked })}
                        className="w-5 h-5 rounded bg-[#1F2228] border-[#3A3D45] text-[#3B82F6]"
                      />
                      <span className="text-[#9CA3AF]">{value ? 'Enabled' : 'Disabled'}</span>
                    </label>
                  ) : typeof value === 'number' ? (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => setEditData({ ...editData, [key]: parseFloat(e.target.value) })}
                      className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] focus:outline-none"
                      step="0.1"
                    />
                  ) : (
                    <input
                      type="text"
                      value={value as string}
                      onChange={(e) => setEditData({ ...editData, [key]: e.target.value })}
                      className="w-full p-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white focus:border-[#3B82F6] focus:outline-none"
                    />
                  )}
                </div>
              ))}
            </div>

            <div className="sticky bottom-0 bg-[#1F2228] border-t border-[#2A2D35] p-6 flex gap-3">
              <button
                onClick={() => saveSettings(editCategory, editData)}
                disabled={saving}
                className="flex-1 px-6 py-3 bg-[#3B82F6] text-white rounded-lg hover:bg-[#2563EB] transition-colors font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setShowEditModal(false)}
                className="px-6 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-semibold"
              >
                Cancel
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Local AI Chat Modal */}
      {showLocalAIModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
          <motion.div
            className="bg-[#1F2228] border border-[#2A2D35] rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="bg-gradient-to-r from-[#10B981]/20 to-[#3B82F6]/20 border-b border-[#2A2D35] p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-[#10B981]/20 rounded-xl">
                    <Cpu className="w-6 h-6 text-[#10B981]" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Local AI Chat</h3>
                    <p className="text-[#9CA3AF] text-sm">100% Private • Fast • Offline</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowLocalAIModal(false)}
                  className="p-2 hover:bg-[#2A2D35] rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-[#9CA3AF]" />
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* Status Section */}
              <div className="mb-6 p-4 bg-[#2A2D35] rounded-lg">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-[#9CA3AF] text-sm mb-1">Status</p>
                    <p className="text-white font-semibold">
                      {localAIStatus?.initialized ? '🟢 Ready' : localAIStatus?.available ? '🟡 Not Loaded' : '🔴 Not Installed'}
                    </p>
                  </div>
                  <div>
                    <p className="text-[#9CA3AF] text-sm mb-1">Model</p>
                    <p className="text-white font-semibold text-sm">
                      {localAIStatus?.model_info?.name?.substring(0, 20) || 'None'}
                    </p>
                  </div>
                  <div>
                    <p className="text-[#9CA3AF] text-sm mb-1">Speed</p>
                    <p className="text-white font-semibold">
                      {localAIStatus?.stats?.avg_tokens_per_sec 
                        ? `${Math.round(localAIStatus.stats.avg_tokens_per_sec)} tok/s` 
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-[#9CA3AF] text-sm mb-1">Queries</p>
                    <p className="text-white font-semibold">
                      {localAIStatus?.stats?.total_queries || 0}
                    </p>
                  </div>
                </div>
              </div>

              {/* Chat Interface */}
              {localAIStatus?.initialized ? (
                <LocalAIChatInterface onClose={() => setShowLocalAIModal(false)} />
              ) : (
                <div className="text-center py-12">
                  <div className="mb-6">
                    <Cpu className="w-16 h-16 text-[#9CA3AF] mx-auto mb-4" />
                    <h4 className="text-xl font-semibold text-white mb-2">Local AI Not Ready</h4>
                    <p className="text-[#9CA3AF] mb-6">
                      {!localAIStatus?.available 
                        ? 'Local AI is not installed. Install llama-cpp-python to continue.' 
                        : 'No model loaded. Download TinyLlama or Qwen2 model.'}
                    </p>
                  </div>
                  
                  <div className="bg-[#2A2D35] rounded-lg p-6 text-left max-w-2xl mx-auto">
                    <h5 className="text-white font-semibold mb-3">📥 Quick Setup Instructions:</h5>
                    <ol className="space-y-2 text-[#9CA3AF] text-sm">
                      <li>1. Install dependencies: <code className="bg-[#1F2228] px-2 py-1 rounded text-[#10B981]">pip install llama-cpp-python</code></li>
                      <li>2. Download model: <code className="bg-[#1F2228] px-2 py-1 rounded text-[#10B981]">huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --local-dir model/local_models</code></li>
                      <li>3. Restart backend and refresh this page</li>
                    </ol>
                    <p className="mt-4 text-xs text-[#6B7280]">
                      📚 Full guide: <span className="text-[#3B82F6]">docs/LOCAL_AI_QUICKSTART.md</span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Local AI Chat Component
const LocalAIChatInterface = ({ onClose }: { onClose: () => void }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<{role: string, content: string, timestamp: string}[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message;
    setMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/local_ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, max_tokens: 512 })
      });

      const data = await res.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response, 
          timestamp: data.timestamp 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'error', 
          content: `Error: ${data.error}`, 
          timestamp: new Date().toISOString() 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: `Failed to send message: ${error}`, 
        timestamp: new Date().toISOString() 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await fetch('http://localhost:5000/api/local_ai/reset', { method: 'POST' });
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear chat:', error);
    }
  };

  return (
    <div className="flex flex-col h-[500px]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-12 h-12 text-[#9CA3AF] mx-auto mb-3" />
            <p className="text-[#9CA3AF]">Start a conversation with your local AI</p>
            <p className="text-[#6B7280] text-sm mt-2">100% private • runs on your machine</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-[#3B82F6] text-white' 
                  : msg.role === 'error'
                  ? 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30'
                  : 'bg-[#2A2D35] text-white'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs mt-2 opacity-60">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#2A2D35] p-4 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-[#3B82F6] border-t-transparent"></div>
                <span className="text-[#9CA3AF]">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          className="flex-1 px-4 py-3 bg-[#2A2D35] border border-[#3A3D45] rounded-lg text-white placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6]"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={!message.trim() || loading}
          className="px-6 py-3 bg-[#10B981] text-white rounded-lg hover:bg-[#059669] transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
        <button
          onClick={clearChat}
          className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors"
          title="Clear chat"
        >
          <RotateCcw className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default SettingsDetail;
