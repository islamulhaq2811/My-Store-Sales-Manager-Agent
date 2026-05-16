import { useState, useEffect } from 'react'
import { getCampaigns, createCampaign, getPromotions, createPromotion, getLeads, addLead } from '../services/api'
import './Marketing.css'

function Marketing() {
  const [campaigns, setCampaigns] = useState([])
  const [promotions, setPromotions] = useState([])
  const [leads, setLeads] = useState([])
  const [activeForm, setActiveForm] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchAll() }, [])

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [campRes, promoRes, leadRes] = await Promise.all([
        getCampaigns(), getPromotions(), getLeads()
      ])
      setCampaigns(campRes.data)
      setPromotions(promoRes.data)
      setLeads(leadRes.data)
    } catch (error) {
      console.error('Error fetching marketing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCampaign = async (e) => {
    e.preventDefault()
    const fd = new FormData(e.target)
    try {
      await createCampaign({
        name: fd.get('name'),
        campaign_type: fd.get('type'),
        budget: parseFloat(fd.get('budget')) || 0
      })
      e.target.reset()
      setActiveForm(null)
      fetchAll()
    } catch (error) {
      console.error('Error creating campaign:', error)
    }
  }

  const handlePromotion = async (e) => {
    e.preventDefault()
    const fd = new FormData(e.target)
    try {
      await createPromotion({
        name: fd.get('name'),
        discount_type: fd.get('type'),
        discount_value: parseFloat(fd.get('value'))
      })
      e.target.reset()
      setActiveForm(null)
      fetchAll()
    } catch (error) {
      console.error('Error creating promotion:', error)
    }
  }

  if (loading) return <div className="loading"><div className="loading-spinner" /> Loading marketing data...</div>

  return (
    <div className="marketing-container">
      <div className="section-header">
        <div>
          <h3>Marketing Hub</h3>
          <p className="section-subtitle">Campaigns, promotions & lead management</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,58,237,0.1)', color: '#7c3aed' }}>M</div>
          <div className="stat-content">
            <p className="stat-label">Campaigns</p>
            <p className="stat-value">{campaigns.length}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>%</div>
          <div className="stat-content">
            <p className="stat-label">Promotions</p>
            <p className="stat-value">{promotions.length}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }}>L</div>
          <div className="stat-content">
            <p className="stat-label">Leads</p>
            <p className="stat-value">{leads.length}</p>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button
          className={`action-btn ${activeForm === 'campaign' ? 'active' : ''}`}
          onClick={() => setActiveForm(activeForm === 'campaign' ? null : 'campaign')}
        >
          <span className="action-btn-icon gradient-purple">C</span>
          <span className="action-btn-label">New Campaign</span>
        </button>
        <button
          className={`action-btn ${activeForm === 'promotion' ? 'active' : ''}`}
          onClick={() => setActiveForm(activeForm === 'promotion' ? null : 'promotion')}
        >
          <span className="action-btn-icon gradient-green">P</span>
          <span className="action-btn-label">Create Promotion</span>
        </button>
        <button
          className={`action-btn ${activeForm === 'lead' ? 'active' : ''}`}
          onClick={() => setActiveForm(activeForm === 'lead' ? null : 'lead')}
        >
          <span className="action-btn-icon gradient-orange">L</span>
          <span className="action-btn-label">Add Lead</span>
        </button>
      </div>

      {activeForm === 'campaign' && (
        <div className="form-card slide-in">
          <div className="form-card-header">
            <h4>New Campaign</h4>
            <button className="btn-icon" onClick={() => setActiveForm(null)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <form onSubmit={handleCampaign}>
            <div className="form-row">
              <div className="form-group">
                <label>Campaign Name</label>
                <input name="name" type="text" required placeholder="Summer Sale 2026" />
              </div>
              <div className="form-group">
                <label>Type</label>
                <select name="type">
                  <option value="email">Email</option>
                  <option value="social">Social Media</option>
                  <option value="ppc">PPC</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Budget ($)</label>
              <input name="budget" type="number" step="0.01" placeholder="1000" />
            </div>
            <button type="submit" className="submit-btn">Create Campaign</button>
          </form>
        </div>
      )}

      {activeForm === 'promotion' && (
        <div className="form-card slide-in">
          <div className="form-card-header">
            <h4>New Promotion</h4>
            <button className="btn-icon" onClick={() => setActiveForm(null)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <form onSubmit={handlePromotion}>
            <div className="form-row">
              <div className="form-group">
                <label>Promotion Name</label>
                <input name="name" type="text" required placeholder="Flash Sale" />
              </div>
              <div className="form-group">
                <label>Discount Type</label>
                <select name="type">
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Discount Value</label>
              <input name="value" type="number" step="0.01" required placeholder="20" />
            </div>
            <button type="submit" className="submit-btn">Create Promotion</button>
          </form>
        </div>
      )}

      <div className="data-sections">
        <div className="card">
          <h4>Active Campaigns</h4>
          {campaigns.length === 0 ? (
            <p className="no-data">No campaigns yet.</p>
          ) : (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr><th>Name</th><th>Type</th><th>Budget</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {campaigns.slice(0, 5).map(c => (
                    <tr key={c.id}>
                      <td className="cell-name">{c.name}</td>
                      <td><span className="cell-tag">{c.campaign_type}</span></td>
                      <td>${c.budget?.toFixed(2)}</td>
                      <td><span className="status-badge active">{c.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <h4>Active Promotions</h4>
          {promotions.length === 0 ? (
            <p className="no-data">No promotions yet.</p>
          ) : (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr><th>Name</th><th>Type</th><th>Value</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {promotions.slice(0, 5).map(p => (
                    <tr key={p.id}>
                      <td className="cell-name">{p.name}</td>
                      <td><span className="cell-tag">{p.discount_type}</span></td>
                      <td>{p.discount_value}%</td>
                      <td><span className="status-badge active">{p.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Marketing
