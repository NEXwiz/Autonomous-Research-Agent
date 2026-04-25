import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Search, BrainCircuit, FileSearch, PenTool, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [activeNode, setActiveNode] = useState(null);
  const [stateData, setStateData] = useState({ loop_count: 1, sub_questions: [], critic_score: null, critic_feedback: '', report: '' });
  const [error, setError] = useState('');

  const handleResearch = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsResearching(true);
    setActiveNode('planner_node');
    setStateData({ loop_count: 1, sub_questions: [], critic_score: null, critic_feedback: '', report: '' });
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });

      if (!response.ok) throw new Error('Backend server is not running or encountered an error.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const dataStr = line.replace('data: ', '').trim();
              if (dataStr) {
                const parsed = JSON.parse(dataStr);
                setActiveNode(parsed.node);
                setStateData(prev => ({ ...prev, ...parsed }));
                if (parsed.node === 'report_node') {
                  setIsResearching(false);
                }
              }
            } catch (err) {
              console.error("Parse error:", err);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred during research.');
      setIsResearching(false);
    }
  };

  const getNodeStatus = (nodeName) => {
    if (activeNode === nodeName) return 'active';
    const order = ['planner_node', 'search_node', 'summarizer_node', 'critic_node', 'report_node'];
    const currentIndex = order.indexOf(activeNode);
    const thisIndex = order.indexOf(nodeName);
    if (thisIndex < currentIndex && activeNode !== null) return 'done';
    return 'pending';
  };

  return (
    <div className="container">
      <header className="app-header">
        <h1 className="app-title">Autonomous Research Agent</h1>
        <p className="app-subtitle">Powered by LangGraph & Gemini 2.5 Flash</p>
      </header>

      <form onSubmit={handleResearch} className="search-box">
        <input 
          type="text" 
          className="search-input glass-panel" 
          placeholder="What do you want to research today?" 
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          disabled={isResearching}
        />
        <button type="submit" className="search-button" disabled={isResearching || !topic.trim()}>
          {isResearching ? <Loader2 className="icon-spin" /> : <Search />}
          Research
        </button>
      </form>

      {error && <div className="critic-feedback" style={{marginBottom: '2rem'}}>{error}</div>}

      {(isResearching || stateData.report) && (
        <div className="status-grid">
          
          <div className={`status-card glass-panel ${getNodeStatus('planner_node')}`}>
            <div className="status-header">
              <BrainCircuit className={getNodeStatus('planner_node') === 'active' ? 'icon-spin' : ''} />
              Planner
            </div>
            {stateData.sub_questions.length > 0 && (
              <>
                <div style={{fontSize: '0.8rem', color: 'var(--primary)'}}>Loop {stateData.loop_count}/4</div>
                <ul className="sub-questions-list">
                  {stateData.sub_questions.map((sq, i) => <li key={i}>{sq.question}</li>)}
                </ul>
              </>
            )}
          </div>

          <div className={`status-card glass-panel ${getNodeStatus('search_node')}`}>
            <div className="status-header">
              <FileSearch className={getNodeStatus('search_node') === 'active' ? 'icon-spin' : ''} />
              Parallel Search
            </div>
            {getNodeStatus('search_node') === 'active' && <p className="sub-questions-list" style={{paddingLeft:0}}>Fetching live sources...</p>}
          </div>

          <div className={`status-card glass-panel ${getNodeStatus('summarizer_node')}`}>
            <div className="status-header">
              <PenTool className={getNodeStatus('summarizer_node') === 'active' ? 'icon-spin' : ''} />
              Summarizer
            </div>
             {getNodeStatus('summarizer_node') === 'active' && <p className="sub-questions-list" style={{paddingLeft:0}}>Synthesizing findings...</p>}
          </div>

          <div className={`status-card glass-panel ${getNodeStatus('critic_node')}`}>
            <div className="status-header">
              <AlertTriangle className={getNodeStatus('critic_node') === 'active' ? 'icon-spin' : ''} />
              Critic
            </div>
            {stateData.critic_score && (
              <div style={{marginTop: '0.5rem'}}>
                <div style={{fontSize: '1.5rem', fontWeight: '700', color: stateData.critic_score >= 7 ? 'var(--secondary)' : '#f87171'}}>
                  Score: {stateData.critic_score}/10
                </div>
                {stateData.critic_feedback && stateData.critic_score < 7 && (
                  <div className="critic-feedback" style={{marginTop: '0.5rem'}}>{stateData.critic_feedback}</div>
                )}
              </div>
            )}
          </div>

        </div>
      )}

      {stateData.report && (
        <div className="report-container glass-panel">
          <div className="status-header" style={{marginBottom: '1rem', color: 'var(--primary)'}}>
            <CheckCircle /> Final Report
          </div>
          <div className="markdown-body">
            <ReactMarkdown>{stateData.report}</ReactMarkdown>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
