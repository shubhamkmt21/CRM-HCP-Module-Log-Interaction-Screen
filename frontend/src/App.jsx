import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInteractions, sendChatMessage, addUserMessage, addInteraction } from './store';
import { MessageSquare, LayoutDashboard, Send, Activity, PlusCircle, Mic, Search, Plus, Smile, Meh, Frown } from 'lucide-react';

function LogInteractionView() {
  const [input, setInput] = useState('');
  const [formData, setFormData] = useState({
    hcp_name: '',
    interaction_type: 'Meeting',
    interaction_date: '',
    interaction_time: '',
    attendees: '',
    notes: '',
    materials_shared: '',
    samples_distributed: '',
    sentiment: 'Neutral',
    outcomes: '',
    action_items: '',
  });

  const dispatch = useDispatch();
  const { messages, status } = useSelector((state) => state.chat);

  const handleSendChat = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = input;
    dispatch(addUserMessage(userMessage));
    setInput('');
    
    // Send to agent for chat response
    dispatch(sendChatMessage(userMessage));

    // Send to extraction endpoint to auto-populate the form
    try {
      const res = await fetch('http://localhost:8000/extract/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      if (res.ok) {
        const extractedData = await res.json();
        // Merge extracted data over current formData (only overwriting if extracted data is truthy)
        setFormData(prev => ({
          hcp_name: extractedData.hcp_name || prev.hcp_name,
          interaction_type: extractedData.interaction_type || prev.interaction_type,
          interaction_date: extractedData.interaction_date || prev.interaction_date,
          interaction_time: extractedData.interaction_time || prev.interaction_time,
          attendees: extractedData.attendees || prev.attendees,
          notes: extractedData.notes || prev.notes,
          materials_shared: extractedData.materials_shared || prev.materials_shared,
          samples_distributed: extractedData.samples_distributed || prev.samples_distributed,
          sentiment: extractedData.sentiment || prev.sentiment,
          outcomes: extractedData.outcomes || prev.outcomes,
          action_items: extractedData.action_items || prev.action_items,
        }));
      }
    } catch (err) {
      console.error("Failed to auto-extract form data:", err);
    }
  };

  const handleManualSubmit = (e) => {
    e.preventDefault();
    dispatch(addInteraction(formData)).then(() => {
      alert("Interaction logged manually!");
      setFormData({ 
        hcp_name: '', interaction_type: 'Meeting', interaction_date: '', interaction_time: '',
        attendees: '', notes: '', materials_shared: '', samples_distributed: '',
        sentiment: 'Neutral', outcomes: '', action_items: ''
      });
      dispatch(fetchInteractions());
    });
  };

  return (
    <div className="log-screen-container">
      <div className="manual-form-section">
        <h3 className="form-header">Interaction Details</h3>
        <form className="complex-form" onSubmit={handleManualSubmit}>
          
          <div className="form-row two-col">
            <div className="form-group">
              <label>HCP Name</label>
              <input 
                type="text" 
                required
                value={formData.hcp_name} 
                onChange={e => setFormData({...formData, hcp_name: e.target.value})} 
                placeholder="Search or select HCP..." 
              />
            </div>
            <div className="form-group">
              <label>Interaction Type</label>
              <select 
                value={formData.interaction_type} 
                onChange={e => setFormData({...formData, interaction_type: e.target.value})}
              >
                <option value="Meeting">Meeting</option>
                <option value="Virtual">Virtual</option>
                <option value="Email">Email</option>
                <option value="Call">Call</option>
              </select>
            </div>
          </div>

          <div className="form-row two-col">
            <div className="form-group">
              <label>Date</label>
              <input 
                type="date" 
                value={formData.interaction_date} 
                onChange={e => setFormData({...formData, interaction_date: e.target.value})} 
              />
            </div>
            <div className="form-group">
              <label>Time</label>
              <input 
                type="time" 
                value={formData.interaction_time} 
                onChange={e => setFormData({...formData, interaction_time: e.target.value})} 
              />
            </div>
          </div>

          <div className="form-group">
            <label>Attendees</label>
            <input 
              type="text" 
              value={formData.attendees} 
              onChange={e => setFormData({...formData, attendees: e.target.value})} 
              placeholder="Enter names or search..." 
            />
          </div>

          <div className="form-group">
            <label>Topics Discussed</label>
            <div className="textarea-wrapper">
              <textarea 
                required
                rows="4"
                value={formData.notes} 
                onChange={e => setFormData({...formData, notes: e.target.value})} 
                placeholder="Enter key discussion points..." 
              ></textarea>
              <Mic className="mic-icon" size={18} />
            </div>
            <button type="button" className="action-btn secondary voice-btn">
              <Mic size={16} /> Summarize from Voice Note (Requires Consent)
            </button>
          </div>

          <div className="form-section-title">Materials Shared / Samples Distributed</div>
          <div className="materials-box">
            <div className="materials-row">
              <div className="materials-content">
                <strong>Materials Shared</strong>
                <p className="no-items">No materials added.</p>
              </div>
              <button type="button" className="action-btn outline"><Search size={14}/> Search/Add</button>
            </div>
          </div>
          <div className="materials-box">
            <div className="materials-row">
              <div className="materials-content">
                <strong>Samples Distributed</strong>
                <p className="no-items">No samples added.</p>
              </div>
              <button type="button" className="action-btn outline"><Plus size={14}/> Add Sample</button>
            </div>
          </div>

          <div className="form-group">
            <label>Observed/Inferred HCP Sentiment</label>
            <div className="sentiment-options">
              <label className="sentiment-radio">
                <input type="radio" name="sentiment" value="Positive" checked={formData.sentiment === 'Positive'} onChange={e => setFormData({...formData, sentiment: e.target.value})} />
                <Smile size={18} /> Positive
              </label>
              <label className="sentiment-radio">
                <input type="radio" name="sentiment" value="Neutral" checked={formData.sentiment === 'Neutral'} onChange={e => setFormData({...formData, sentiment: e.target.value})} />
                <Meh size={18} /> Neutral
              </label>
              <label className="sentiment-radio">
                <input type="radio" name="sentiment" value="Negative" checked={formData.sentiment === 'Negative'} onChange={e => setFormData({...formData, sentiment: e.target.value})} />
                <Frown size={18} /> Negative
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Outcomes</label>
            <textarea 
              rows="3"
              value={formData.outcomes} 
              onChange={e => setFormData({...formData, outcomes: e.target.value})} 
              placeholder="Key outcomes or agreements..." 
            ></textarea>
          </div>

          <div className="form-group">
            <label>Follow-up Actions</label>
            <textarea 
              rows="3"
              value={formData.action_items} 
              onChange={e => setFormData({...formData, action_items: e.target.value})} 
              placeholder="Enter next steps or tasks..." 
            ></textarea>
          </div>

          <div className="ai-suggestions">
            <strong>AI Suggested Follow-ups:</strong>
            <ul>
              <li><Plus size={12}/> Schedule follow-up meeting in 2 weeks</li>
              <li><Plus size={12}/> Send OncoBoost Phase III PDF</li>
              <li><Plus size={12}/> Add Dr. Sharma to advisory board invite list</li>
            </ul>
          </div>

          <button type="submit" className="submit-btn primary">
             Save Interaction
          </button>
        </form>
      </div>

      <div className="chat-section">
        <h3>💬 AI Assistant</h3>
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {status === 'loading' && (
              <div className="message ai">Thinking...</div>
            )}
          </div>
          <form className="chat-input" onSubmit={handleSendChat}>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Or just type your interaction here..." 
              disabled={status === 'loading'}
            />
            <button type="submit" disabled={status === 'loading' || !input.trim()}>
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function DashboardView() {
  const dispatch = useDispatch();
  const { list, status } = useSelector((state) => state.interactions);

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: 600 }}>Recent Interactions</h2>
      {list.length === 0 ? (
        <div className="empty-state">
          <Activity size={48} style={{ margin: '0 auto 1rem', color: 'var(--text-muted)' }} />
          <p>No interactions logged yet. Use the Manual Form or AI Chat to log one.</p>
        </div>
      ) : (
        <div className="dashboard-grid">
          {list.map((interaction) => (
            <div key={interaction.id} className="card">
              <div className="card-header">
                <span className="card-title">{interaction.hcp_name}</span>
                <span className="badge">{interaction.interaction_type}</span>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                {interaction.interaction_date && <span>{interaction.interaction_date} {interaction.interaction_time} • </span>}
                {interaction.sentiment && <strong>Sentiment: {interaction.sentiment}</strong>}
              </div>
              <p style={{ fontSize: '0.95rem', marginBottom: '1rem' }}>{interaction.notes}</p>
              {interaction.action_items && (
                <div style={{ padding: '0.75rem', backgroundColor: '#F9FAFB', borderRadius: '0.5rem', fontSize: '0.875rem' }}>
                  <strong>Action Items:</strong> {interaction.action_items}
                </div>
              )}
              <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#9CA3AF' }}>
                Logged on {new Date(interaction.timestamp).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Sidebar() {
  const location = useLocation();

  return (
    <div className="sidebar">
      <h1>
        <Activity color="var(--primary)" />
        AI CRM
      </h1>
      <div className="nav-links">
        <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
          <MessageSquare size={20} />
          <span>Log Interaction</span>
        </Link>
        <Link to="/dashboard" className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </Link>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="container">
        <Sidebar />
        <div className="main-content">
          <div className="header">
            <Routes>
              <Route path="/" element="Log Interaction" />
              <Route path="/dashboard" element="Interactions Dashboard" />
            </Routes>
          </div>
          <div className="content-area">
            <Routes>
              <Route path="/" element={<LogInteractionView />} />
              <Route path="/dashboard" element={<DashboardView />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
