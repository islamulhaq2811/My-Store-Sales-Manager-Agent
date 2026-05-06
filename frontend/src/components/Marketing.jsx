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

  if (loading) return <div className="loading">Loading marketing data...</div>

  return (
    <div className="marketing-container">
      <div className="section-header">
        <div>
          <h3>Marketing Hub</h3>
          <p className="section-subtitle">Campaigns, promotions & lead management</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <span className="stat-icon">📢</span>
          <div className="stat-content">
            <p className="stat-label">Campaigns</p>
            <p className="stat-value">{campaigns.length}</p>
          </div>
        </div>
        <div className="stat-card success">
          <span className="stat-icon">🏷️</span>
          <div className="stat-content">
            <p className="stat-label">Promotions</p>
            <p className="stat-value">{promotions.length}</p>
          </div>
        </div>
        <div className="stat-card warning">
          <span className="stat-icon">🎯</span>
          <div className="stat-content">
            <p className="stat-label">Leads</p>
            <p className="stat-value">{leads.length}</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="marketing-actions">
        <button className="action-btn" onClick={() => setActiveForm(activeForm === 'campaign' ? null : 'campaign')}>
          📢 New Campaign
        </button>
        <button className="action-btn" onClick={() => setActiveForm(activeForm === 'promotion' ? null : 'promotion')}>
          🏷️ Create Promotion
        </button>
        <button className="action-btn" onClick={() => setActiveForm(activeForm === 'lead' ? null : 'lead')}>
          🎯 Add Lead
        </button>
      </div>

      {/* Forms */}
      {activeForm === 'campaign' && (
        <div className="form-card">
          <h4>New Campaign</h4>
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
        <div className="form-card">
          <h4>New Promotion</h4>
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

      {/* Data Tables */}
      <div className="data-sections">
        <div className="data-section">
          <h4>📢 Active Campaigns</h4>
          <div className="table-wrapper">
            {campaigns.length === 0 ? <p className="no-data">No campaigns yet.</p> : (
              <table className="data-table">
                <thead>
                  <tr><th>Name</th><th>Type</th><th>Budget</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {campaigns.slice(0, 5).map(c => (
                    <tr key={c.id}>
                      <td>{c.name}</td>
                      <td>{c.campaign_type}</td>
                      <td>${c.budget?.toFixed(2)}</td>
                      <td><span className="status-badge active">{c.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="data-section">
          <h4>🏷️ Active Promotions</h4>
          <div className="table-wrapper">
            {promotions.length === 0 ? <p className="no-data">No promotions yet.</p> : (
              <table className="data-table">
                <thead>
                  <tr><th>Name</th><th>Type</th><th>Value</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {promotions.slice(0, 5).map(p => (
                    <tr key={p.id}>
                      <td>{p.name}</td>
                      <td>{p.discount_type}</td>
                      <td>{p.discount_value}%</td>
                      <td><span className="status-badge active">{p.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Marketing
