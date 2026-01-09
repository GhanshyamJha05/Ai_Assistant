import { motion } from 'framer-motion';
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
    <div className="min-h-screen bg-[#0A0E12] text-white overflow-x-hidden">
      <motion.div
        className="container mx-auto px-4 py-6 max-w-[1800px]"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <motion.div
            className="xl:col-span-2 space-y-6"
            variants={columnVariants}
          >
            <QuickOptions />
            <CameraFeed />
            <LearningStats />
          </motion.div>

          <motion.div
            className="xl:col-span-6 space-y-6"
            variants={columnVariants}
          >
            <StatusBar />
            <VoiceButton />
            <CommandInput />
            <TaskStatus />
          </motion.div>

          <motion.div
            className="xl:col-span-4 space-y-6"
            variants={columnVariants}
          >
            <ChatVoiceHistory />
            <SystemStats />
            <SystemLogs />
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

export default App;
