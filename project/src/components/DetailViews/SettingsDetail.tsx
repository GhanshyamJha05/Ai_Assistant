import { motion } from 'framer-motion';
import { Bell, Lock, Palette, Globe, Database } from 'lucide-react';

const SettingsDetail = () => {
  const settingsGroups = [
    {
      title: 'Appearance',
      icon: Palette,
      color: '#3B82F6',
      settings: [
        { label: 'Theme', value: 'Dark' },
        { label: 'Accent Color', value: 'Blue' },
        { label: 'Font Size', value: 'Medium' },
      ]
    },
    {
      title: 'Notifications',
      icon: Bell,
      color: '#F59E0B',
      settings: [
        { label: 'Push Notifications', value: 'Enabled' },
        { label: 'Sound Alerts', value: 'Enabled' },
        { label: 'Email Notifications', value: 'Disabled' },
      ]
    },
    {
      title: 'Privacy & Security',
      icon: Lock,
      color: '#EF4444',
      settings: [
        { label: 'Data Collection', value: 'Minimal' },
        { label: 'Encryption', value: 'Enabled' },
        { label: 'Auto-Lock', value: '5 minutes' },
      ]
    },
    {
      title: 'Language & Region',
      icon: Globe,
      color: '#10B981',
      settings: [
        { label: 'Language', value: 'English (US)' },
        { label: 'Time Zone', value: 'UTC+0' },
        { label: 'Date Format', value: 'MM/DD/YYYY' },
      ]
    },
    {
      title: 'Data Management',
      icon: Database,
      color: '#8B5CF6',
      settings: [
        { label: 'Cache Size', value: '1.2 GB' },
        { label: 'Auto-Backup', value: 'Daily' },
        { label: 'Data Retention', value: '90 days' },
      ]
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-white mb-2">Settings</h3>
        <p className="text-[#9CA3AF]">Configure your AI assistant preferences</p>
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
                <div key={idx} className="flex items-center justify-between p-3 bg-[#2A2D35] rounded-lg hover:bg-[#3A3D45] transition-colors cursor-pointer">
                  <span className="text-[#9CA3AF]">{setting.label}</span>
                  <span className="text-white font-medium">{setting.value}</span>
                </div>
              ))}
            </div>

            <button className="mt-4 w-full px-4 py-2 bg-[#3B82F6]/20 text-[#3B82F6] rounded-lg hover:bg-[#3B82F6]/30 transition-colors font-medium">
              Edit Settings
            </button>
          </motion.div>
        ))}
      </div>

      <div className="bg-[#1F2228] border border-[#2A2D35] rounded-lg p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Advanced Options</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium">
            Export Data
          </button>
          <button className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium">
            Import Settings
          </button>
          <button className="px-4 py-3 bg-[#2A2D35] text-[#9CA3AF] rounded-lg hover:bg-[#3A3D45] transition-colors font-medium">
            Reset to Default
          </button>
          <button className="px-4 py-3 bg-[#EF4444]/20 text-[#EF4444] rounded-lg hover:bg-[#EF4444]/30 transition-colors font-medium">
            Clear All Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsDetail;
