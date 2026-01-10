import { motion } from 'framer-motion';
import { DashboardProvider } from './contexts/DashboardContext';
import QuickOptions from './components/LeftColumn/QuickOptions';
import CameraFeed from './components/LeftColumn/CameraFeed';
import LearningStats from './components/LeftColumn/LearningStats';
import StatusBar from './components/CenterColumn/StatusBar';
import VoiceButton from './components/CenterColumn/VoiceButton';
import CommandInput from './components/CenterColumn/CommandInput';
import TaskStatus from './components/CenterColumn/TaskStatus';
import ChatVoiceHistory from './components/RightColumn/ChatVoiceHistory';
import SystemStats from './components/RightColumn/SystemStats';
import SystemLogs from './components/RightColumn/SystemLogs';

function App() {
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
    <DashboardProvider>
      <div className="h-screen bg-[#0A0E12] text-white overflow-hidden flex flex-col">
        <motion.div
          className="flex-1 px-4 py-4 max-w-[1920px] mx-auto w-full overflow-hidden"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 h-full">
            <motion.div
              className="xl:col-span-2 space-y-4 overflow-y-auto"
              variants={columnVariants}
            >
              <QuickOptions />
              <CameraFeed />
              <LearningStats />
            </motion.div>

            <motion.div
              className="xl:col-span-6 flex flex-col gap-4"
              variants={columnVariants}
            >
              <StatusBar />
              <div className="flex-1 flex items-center justify-center">
                <VoiceButton />
              </div>
              <CommandInput />
              <TaskStatus />
            </motion.div>

            <motion.div
              className="xl:col-span-4 space-y-4 overflow-y-auto"
              variants={columnVariants}
            >
              <ChatVoiceHistory />
              <SystemStats />
              <SystemLogs />
            </motion.div>
          </div>
        </motion.div>
      </div>
    </DashboardProvider>
  );
}

export default App;
