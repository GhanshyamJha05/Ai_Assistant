import { motion } from 'framer-motion';
import { DashboardProvider, useDashboard } from './contexts/DashboardContext';
import QuickOptions from './components/LeftColumn/QuickOptions';
import CameraFeed from './components/LeftColumn/CameraFeed';
import AILearningDashboard from './components/LeftColumn/AILearningDashboard';
import StatusBar from './components/CenterColumn/StatusBar';
import VoiceButton from './components/CenterColumn/VoiceButton';
import CommandInput from './components/CenterColumn/CommandInput';
import TaskStatus from './components/CenterColumn/TaskStatus';
import ChatVoiceHistory from './components/RightColumn/ChatVoiceHistory';
import SystemStats from './components/RightColumn/SystemStats';
import SystemLogs from './components/RightColumn/SystemLogs';
import DetailView from './components/DetailView';
import DashboardDetail from './components/DetailViews/DashboardDetail';
import AppsDetail from './components/DetailViews/AppsDetail';
import ChatDetail from './components/DetailViews/ChatDetail';
import VoiceDetail from './components/DetailViews/VoiceDetail';
import SettingsDetail from './components/DetailViews/SettingsDetail';
import AILearningDetail from './components/DetailViews/AILearningDetail';
import { PWAInstallPrompt } from './components/PWAInstallPrompt';
import { OfflineIndicator } from './components/OfflineIndicator';

function AppContent() {
  const { selectedView, closeDetailView } = useDashboard();

  const getDetailContent = () => {
    switch (selectedView) {
      case 'dashboard':
        return { title: 'System Dashboard', content: <DashboardDetail /> };
      case 'apps':
        return { title: 'Integrated Applications', content: <AppsDetail /> };
      case 'chat':
        return { title: 'Chat History', content: <ChatDetail /> };
      case 'voice':
        return { title: 'Voice Control', content: <VoiceDetail /> };
      case 'settings':
        return { title: 'Settings', content: <SettingsDetail /> };
      case 'ai-learning':
      case 'database':
      case 'systems':
      case 'conversations':
        return { title: 'AI Learning Dashboard', content: <AILearningDetail /> };
      default:
        return null;
    }
  };

  const detailContent = getDetailContent();
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const columnVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: 'easeOut' }
    }
  };

  return (
      <div className="h-screen bg-[#0A0E12] text-white overflow-hidden flex flex-col">
        {/* Offline Indicator */}
        <OfflineIndicator />
        
        <motion.div
          className="flex-1 px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 max-w-[2000px] mx-auto w-full overflow-hidden flex flex-col"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-2 sm:gap-3 md:gap-4 flex-1 overflow-hidden min-h-0">
            <motion.div
              className="lg:col-span-3 flex flex-col gap-2 sm:gap-3 overflow-y-auto min-h-0"
              variants={columnVariants}
            >
              <QuickOptions />
              <CameraFeed />
              <AILearningDashboard />
            </motion.div>

            <motion.div
              className="lg:col-span-6 flex flex-col gap-1 sm:gap-1.5 overflow-hidden min-h-0"
              variants={columnVariants}
            >
              <StatusBar />
              <div className="flex-1 flex items-center justify-center min-h-0 overflow-visible py-2">
                <VoiceButton />
              </div>
              <CommandInput />
              <TaskStatus />
            </motion.div>

            <motion.div
              className="lg:col-span-3 flex flex-col gap-2 sm:gap-3 overflow-hidden min-h-0"
              variants={columnVariants}
            >
              <ChatVoiceHistory />
              <SystemStats />
              <SystemLogs />
            </motion.div>
          </div>
        </motion.div>

        {/* Detail View Modal */}
        {detailContent && (
          <DetailView
            isOpen={!!selectedView}
            onClose={closeDetailView}
            title={detailContent.title}
          >
            {detailContent.content}
          </DetailView>
        )}
        
        {/* PWA Install Prompt */}
        <PWAInstallPrompt />
      </div>
  );
}

function App() {
  return (
    <DashboardProvider>
      <AppContent />
    </DashboardProvider>
  );
}

export default App;
