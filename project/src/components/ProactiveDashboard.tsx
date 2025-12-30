import { useState, useEffect } from 'react';
import { Calendar, CheckSquare, Sun, Target, Briefcase } from 'lucide-react';

interface InsightData {
    calendar: any[];
    tasks: any[];
    weather: any;
    news: string[];
    focus: string;
}

const ProactiveDashboard = () => {
    const [insights, setInsights] = useState<InsightData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                const response = await fetch('/api/startup/briefing'); // Re-using this endpoint for now
                if (response.ok) {
                    const result = await response.json();
                    // Extract raw insights if available, or parse from briefing items
                    // Ideally backend returns raw structure too. For now, let's assume we get similar data structure 
                    // or we might need to adjust the endpoint to return raw data.
                    // Let's assume the endpoint returns { data: { briefing: { raw_insights: ... } } }

                    // Actually, let's double check what startup/sequence returns. 
                    // It returns { data: { briefing: { ... } } }
                    // And we added "raw_insights" to briefing.

                    if (result.success && result.data && result.data.briefing && result.data.briefing.raw_insights) {
                        setInsights(result.data.briefing.raw_insights);
                    }
                }
            } catch (e) {
                console.error("Failed to fetch proactive insights", e);
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();

        // Refresh every 5 mins
        const interval = setInterval(fetchInsights, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !insights) {
        return (
            <div className="glass-strong p-6 rounded-2xl animate-pulse">
                <div className="h-6 w-1/3 bg-white/10 rounded mb-4"></div>
                <div className="space-y-3">
                    <div className="h-20 bg-white/5 rounded-xl"></div>
                    <div className="h-20 bg-white/5 rounded-xl"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-strong p-6 rounded-2xl animate-fade-in relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[#6C5CE7]/10 to-transparent rounded-bl-full -mr-16 -mt-16 pointer-events-none" />

            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 relative z-10">
                <Target size={24} className="text-[#00D9FF]" />
                Proactive Insights
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">

                {/* Daily Focus */}
                <div className="md:col-span-3 bg-gradient-to-r from-[#6C5CE7]/20 to-[#00D9FF]/20 border border-[#00D9FF]/30 p-4 rounded-xl flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-[#0A0E27] flex items-center justify-center border border-[#00D9FF]/50 shadow-[0_0_15px_rgba(0,217,255,0.3)]">
                            <Briefcase size={24} className="text-[#00D9FF]" />
                        </div>
                        <div>
                            <h3 className="text-sm text-[#DDDDDD] uppercase tracking-wider">Today's Focus</h3>
                            <p className="text-xl font-bold text-white">{insights.focus || "Productivity & Development"}</p>
                        </div>
                    </div>
                    <div className="hidden md:block text-right">
                        <p className="text-3xl font-bold text-[#00D9FF]">{insights.tasks.length}</p>
                        <p className="text-xs text-[#DDDDDD]">Pending Tasks</p>
                    </div>
                </div>

                {/* Schedule */}
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 hover:border-[#6C5CE7]/50 transition-colors group">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="flex items-center gap-2 text-[#DDDDDD] font-medium">
                            <Calendar size={18} className="text-[#6C5CE7]" />
                            Agenda
                        </h3>
                        <span className="text-xs bg-[#6C5CE7]/20 text-[#6C5CE7] px-2 py-0.5 rounded-full">{insights.calendar.length} events</span>
                    </div>
                    <div className="space-y-3">
                        {insights.calendar.slice(0, 2).map((event: any, idx: number) => (
                            <div key={idx} className="flex gap-3 text-sm border-l-2 border-[#6C5CE7] pl-3">
                                <div className="text-[#DDDDDD] w-12 flex-shrink-0">
                                    {new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                                <div className="text-white truncate" title={event.title}>{event.title}</div>
                            </div>
                        ))}
                        {insights.calendar.length === 0 && (
                            <p className="text-sm text-gray-500 italic">No upcoming events</p>
                        )}
                    </div>
                </div>

                {/* Tasks */}
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 hover:border-[#00D9FF]/50 transition-colors group">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="flex items-center gap-2 text-[#DDDDDD] font-medium">
                            <CheckSquare size={18} className="text-[#00D9FF]" />
                            Tasks
                        </h3>
                        <span className="text-xs bg-[#00D9FF]/20 text-[#00D9FF] px-2 py-0.5 rounded-full">{insights.tasks.filter((t: any) => t.priority === 'high').length} High Priority</span>
                    </div>
                    <div className="space-y-2">
                        {insights.tasks.slice(0, 3).map((task: any, idx: number) => (
                            <div key={idx} className="flex items-center gap-2 text-sm group-hover:translate-x-1 transition-transform">
                                <div className={`w-2 h-2 rounded-full ${task.priority === 'high' ? 'bg-red-500' : 'bg-green-500'}`} />
                                <span className="text-white line-clamp-1">{task.title}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Weather & News */}
                <div className="bg-white/5 p-4 rounded-xl border border-white/10 hover:border-[#00B894]/50 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="flex items-center gap-2 text-[#DDDDDD] font-medium">
                            <Sun size={18} className="text-[#00B894]" />
                            Intel
                        </h3>
                    </div>
                    <div className="flex items-center gap-4 mb-3">
                        <div className="text-2xl font-bold text-white">{insights.weather.temperature}</div>
                        <div className="text-sm text-[#DDDDDD]">{insights.weather.condition}<br />{insights.weather.location}</div>
                    </div>
                    {insights.news.length > 0 && (
                        <div className="pt-2 border-t border-white/10">
                            <p className="text-xs text-[#AAAAAA] line-clamp-2">Using Latest: {insights.news[0]}</p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default ProactiveDashboard;
