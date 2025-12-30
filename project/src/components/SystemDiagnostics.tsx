import { CheckCircle, AlertCircle, XCircle, Loader } from 'lucide-react';

interface DiagnosticsProps {
    diagnostics: {
        overall_status: string;
        systems: Array<{
            name: string;
            icon: string;
            status: string;
            message: string;
            details?: Record<string, any>;
        }>;
    };
}

const SystemDiagnostics = ({ diagnostics }: DiagnosticsProps) => {
    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'operational':
                return <CheckCircle className="text-[#39FF14]" size={24} />;
            case 'warning':
            case 'partial':
                return <AlertCircle className="text-[#FF9500]" size={24} />;
            case 'error':
                return <XCircle className="text-[#FF3B30]" size={24} />;
            default:
                return <Loader className="text-[#00D9FF] animate-spin" size={24} />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'operational':
                return 'border-[#39FF14]/50 bg-[#39FF14]/5';
            case 'warning':
            case 'partial':
                return 'border-[#FF9500]/50 bg-[#FF9500]/5';
            case 'error':
                return 'border-[#FF3B30]/50 bg-[#FF3B30]/5';
            default:
                return 'border-[#00D9FF]/50 bg-[#00D9FF]/5';
        }
    };

    const getProgressWidth = (status: string) => {
        switch (status) {
            case 'operational':
                return '100%';
            case 'warning':
            case 'partial':
                return '66%';
            case 'error':
                return '33%';
            default:
                return '50%';
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {diagnostics.systems.map((system, index) => (
                <div
                    key={system.name}
                    className={`diagnostic-card p-6 rounded-2xl border backdrop-blur-lg transition-all duration-300 hover:scale-105 ${getStatusColor(system.status)}`}
                    style={{
                        animation: `diagnostic-scan 0.8s ease-out ${index * 0.15}s forwards`,
                        opacity: 0
                    }}
                >
                    <div className="flex items-start gap-4">
                        <div className="text-4xl">{system.icon}</div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-lg font-bold text-white">{system.name}</h3>
                                {getStatusIcon(system.status)}
                            </div>

                            <p className="text-sm text-[#DDDDDD] mb-3">{system.message}</p>

                            {/* Progress bar */}
                            <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-[#00D9FF] to-[#00FFF5] transition-all duration-1000"
                                    style={{
                                        width: getProgressWidth(system.status),
                                        animation: 'progress-fill 1s ease-out forwards'
                                    }}
                                />
                            </div>

                            {/* Details */}
                            {system.details && Object.keys(system.details).length > 0 && (
                                <div className="mt-3 text-xs text-[#DDDDDD]/70 space-y-1">
                                    {Object.entries(system.details).map(([key, value]) => (
                                        <div key={key} className="flex justify-between">
                                            <span>{key}:</span>
                                            <span className="font-mono text-[#00D9FF]">{String(value)}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            ))}

            <style>{`
        @keyframes diagnostic-scan {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes progress-fill {
          from {
            transform: scaleX(0);
            transform-origin: left;
          }
          to {
            transform: scaleX(1);
            transform-origin: left;
          }
        }

        .diagnostic-card {
          position: relative;
          overflow: hidden;
        }

        .diagnostic-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(0, 217, 255, 0.1), transparent);
          animation: scan-line 2s ease-in-out infinite;
        }

        @keyframes scan-line {
          0% {
            left: -100%;
          }
          100% {
            left: 100%;
          }
        }
      `}</style>
        </div>
    );
};

export default SystemDiagnostics;
