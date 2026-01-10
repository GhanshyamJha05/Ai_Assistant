import { motion } from 'framer-motion';
import { Video, VideoOff } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const CameraFeed = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);
  const [error, setError] = useState<string>('');
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setHasPermission(true);
        setIsRecording(true);
        setError('');
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setError('Camera access denied');
      setHasPermission(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsRecording(false);
  };

  const toggleCamera = () => {
    if (isRecording) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  return (
    <motion.div
      className="bg-[#16181D] border border-[#1F2228] rounded-lg p-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-white">Camera Feed</h3>
        <motion.button
          onClick={toggleCamera}
          className="text-xs text-[#9CA3AF] hover:text-white transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isRecording ? 'Stop' : 'Start'}
        </motion.button>
      </div>

      <div className="relative bg-[#0A0E12] rounded-lg overflow-hidden aspect-video flex items-center justify-center group cursor-pointer">
        {hasPermission && isRecording ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />

            {isRecording && (
              <motion.div
                className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-full"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 }}
              >
                <motion.div
                  className="w-2 h-2 bg-red-500 rounded-full"
                  animate={{
                    opacity: [1, 0.3, 1],
                    scale: [1, 0.8, 1],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
                <span className="text-xs font-medium text-white">REC</span>
              </motion.div>
            )}
          </>
        ) : (
          <>
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-[#16181D] to-[#0A0E12]"
              animate={{
                opacity: [0.5, 0.7, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />

            <motion.div
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.2 }}
              className="relative z-10 flex flex-col items-center gap-2"
            >
              {error ? (
                <>
                  <VideoOff className="w-12 h-12 text-[#EF4444] opacity-60" strokeWidth={1.5} />
                  <span className="text-xs text-[#EF4444]">{error}</span>
                  <button
                    onClick={startCamera}
                    className="mt-2 px-3 py-1 bg-[#3B82F6] text-white text-xs rounded-md hover:bg-[#3B82F6]/80 transition-colors"
                  >
                    Retry
                  </button>
                </>
              ) : (
                <>
                  <Video className="w-12 h-12 text-[#3B82F6] opacity-60 group-hover:opacity-100 transition-opacity" strokeWidth={1.5} />
                  <span className="text-xs text-[#9CA3AF]">Click to enable</span>
                </>
              )}
            </motion.div>
          </>
        )}
      </div>
    </motion.div>
  );
};

export default CameraFeed;
