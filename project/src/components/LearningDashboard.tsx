import { useState, useEffect } from 'react';
import { Brain, Database, TrendingUp, BookOpen, Activity, Search, FileText } from 'lucide-react';
import axios from 'axios';

interface LearningStats {
  total_databases: number;
  total_size_mb: number;
  total_conversations: number;
  enhanced_records: number;
  learning_nodes: number;
  active_systems: number;
}

interface DatabaseInfo {
  database: string;
  size_kb: number;
  total_records: number;
  has_data: boolean;
  tables: Array<{name: string; records: number}>;
}

interface RecentActivity {
  timestamp: string;
  type: string;
  speaker: string;
  content: string;
  importance: number;
  category: string;
}

interface DashboardData {
  summary: LearningStats;
  databases: DatabaseInfo[];
  recent_activity: RecentActivity[];
  system_breakdown: Array<{name: string; database: string; records: number; status: string}>;
}

const LearningDashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'databases' | 'systems' | 'docs'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  useEffect(() => {
    fetchDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/learning/dashboard');
      setDashboardData(response.data.data);
      setLoading(false);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load dashboard data');
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.get(`/api/learning/memory/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data.results);
    } catch (err) {
      console.error('Search error:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Brain className="w-16 h-16 mx-auto mb-4 animate-pulse text-blue-500" />
          <p className="text-gray-600">Loading AI Learning Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center text-red-500">
          <p className="text-xl font-bold">Error Loading Dashboard</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.summary;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold flex items-center gap-3 mb-2">
          <Brain className="w-10 h-10" />
          AI Learning Dashboard
        </h1>
        <p className="text-gray-300">Monitor your AI's learning progress and knowledge growth</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('overview')}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'overview'
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Activity className="w-5 h-5 inline mr-2" />
          Overview
        </button>
        <button
          onClick={() => setActiveTab('databases')}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'databases'
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Database className="w-5 h-5 inline mr-2" />
          Databases
        </button>
        <button
          onClick={() => setActiveTab('systems')}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'systems'
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <TrendingUp className="w-5 h-5 inline mr-2" />
          Learning Systems
        </button>
        <button
          onClick={() => setActiveTab('docs')}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'docs'
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <BookOpen className="w-5 h-5 inline mr-2" />
          Documentation
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard
              icon={<Database className="w-8 h-8" />}
              title="Total Databases"
              value={stats.total_databases}
              subtitle={`${stats.total_size_mb.toFixed(2)} MB`}
              color="blue"
            />
            <StatCard
              icon={<Brain className="w-8 h-8" />}
              title="Active Systems"
              value={`${stats.active_systems}/27`}
              subtitle="Learning systems"
              color="green"
            />
            <StatCard
              icon={<FileText className="w-8 h-8" />}
              title="Conversations"
              value={stats.total_conversations}
              subtitle={`${stats.enhanced_records} enhanced`}
              color="purple"
            />
            <StatCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="Learning Nodes"
              value={stats.learning_nodes}
              subtitle="Knowledge concepts"
              color="orange"
            />
            <StatCard
              icon={<Activity className="w-8 h-8" />}
              title="Enhanced Records"
              value={stats.enhanced_records}
              subtitle="Deep analysis"
              color="pink"
            />
            <StatCard
              icon={<Search className="w-8 h-8" />}
              title="Memory Search"
              value="Active"
              subtitle="AI remembers"
              color="cyan"
            />
          </div>

          {/* Search Memory */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Search className="w-6 h-6" />
              Search AI Memory
            </h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search conversations..."
                className="flex-1 px-4 py-2 rounded-lg bg-white/20 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSearch}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
              >
                Search
              </button>
            </div>
            
            {searchResults.length > 0 && (
              <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
                {searchResults.map((result, idx) => (
                  <div key={idx} className="bg-white/5 p-3 rounded border border-white/10">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-400">{result.timestamp}</span>
                      <span className="text-xs bg-blue-600/30 px-2 py-1 rounded">{result.category}</span>
                    </div>
                    <p className="text-sm"><strong>{result.speaker}:</strong> {result.content}</p>
                    <div className="text-xs text-gray-400 mt-1">
                      Importance: {result.importance}/5
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Recent Learning Activity</h3>
            <div className="space-y-2">
              {dashboardData?.recent_activity.slice(0, 5).map((activity, idx) => (
                <div key={idx} className="bg-white/5 p-3 rounded border border-white/10">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold">{activity.speaker}</span>
                    <span className="text-xs text-gray-400">{activity.timestamp}</span>
                  </div>
                  <p className="text-sm mt-1">{activity.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Databases Tab */}
      {activeTab === 'databases' && (
        <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
          <h3 className="text-2xl font-bold mb-4">Learning Databases</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {dashboardData?.databases.filter(db => db.has_data).map((db, idx) => (
              <div key={idx} className="bg-white/5 p-4 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold">{db.database}</h4>
                  <span className="text-sm bg-green-600/30 px-2 py-1 rounded">
                    {db.total_records} records
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">Size: {db.size_kb.toFixed(2)} KB</p>
                <div className="space-y-1">
                  {db.tables.slice(0, 3).map((table, tidx) => (
                    <div key={tidx} className="text-xs text-gray-300">
                      • {table.name}: {table.records} entries
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Learning Systems Tab */}
      {activeTab === 'systems' && (
        <div className="bg-white/10 backdrop-blur-md rounded-lg p-6">
          <h3 className="text-2xl font-bold mb-4">27 Learning Systems Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboardData?.system_breakdown.map((system, idx) => (
              <div key={idx} className="bg-white/5 p-4 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-sm">{system.name}</h4>
                  <span className={`text-xs px-2 py-1 rounded ${
                    system.status === 'active' ? 'bg-green-600/30' :
                    system.status === 'empty' ? 'bg-yellow-600/30' :
                    'bg-gray-600/30'
                  }`}>
                    {system.status}
                  </span>
                </div>
                <p className="text-xs text-gray-400">{system.database}</p>
                <p className="text-lg font-bold mt-2">{system.records} records</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documentation Tab */}
      {activeTab === 'docs' && (
        <DocumentationViewer />
      )}
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle: string;
  color: string;
}> = ({ icon, title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'from-blue-600 to-blue-700',
    green: 'from-green-600 to-green-700',
    purple: 'from-purple-600 to-purple-700',
    orange: 'from-orange-600 to-orange-700',
    pink: 'from-pink-600 to-pink-700',
    cyan: 'from-cyan-600 to-cyan-700',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} p-6 rounded-lg shadow-lg`}>
      <div className="flex items-center justify-between mb-2">
        {icon}
        <span className="text-3xl font-bold">{value}</span>
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-white/80">{subtitle}</p>
    </div>
  );
};

// Documentation Viewer Component
const DocumentationViewer = () => {
  const [docContent, setDocContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocumentation();
  }, []);

  const fetchDocumentation = async () => {
    try {
      const response = await axios.get('/api/learning/documentation');
      setDocContent(response.data.content);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load documentation:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-10">Loading documentation...</div>;
  }

  // Simple markdown-like rendering
  const renderMarkdown = (content: string) => {
    return content.split('\n').map((line, idx) => {
      if (line.startsWith('# ')) {
        return <h1 key={idx} className="text-3xl font-bold mt-6 mb-3">{line.slice(2)}</h1>;
      } else if (line.startsWith('## ')) {
        return <h2 key={idx} className="text-2xl font-bold mt-5 mb-2">{line.slice(3)}</h2>;
      } else if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-xl font-bold mt-4 mb-2">{line.slice(4)}</h3>;
      } else if (line.startsWith('- ')) {
        return <li key={idx} className="ml-6 mb-1">{line.slice(2)}</li>;
      } else if (line.startsWith('**') && line.endsWith('**')) {
        return <p key={idx} className="font-bold my-2">{line.slice(2, -2)}</p>;
      } else if (line.trim() === '') {
        return <br key={idx} />;
      } else {
        return <p key={idx} className="my-1">{line}</p>;
      }
    });
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
        <BookOpen className="w-8 h-8" />
        How Your AI Learns
      </h2>
      <div className="prose prose-invert max-w-none">
        {renderMarkdown(docContent)}
      </div>
    </div>
  );
};

export default LearningDashboard;
