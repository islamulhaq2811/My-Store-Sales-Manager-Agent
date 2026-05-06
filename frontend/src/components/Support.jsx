import { useState, useEffect } from 'react'
import { createRefund, getRefunds, createWarranty, getWarranties, createDelivery, getDeliveries } from '../services/api'
import './Support.css'

function Support() {
  const [activeForm, setActiveForm] = useState(null)
  const [refunds, setRefunds] = useState([])
  const [warranties, setWarranties] = useState([])
  const [deliveries, setDeliveries] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetchAll() }, [])

  const fetchAll = async () => {
    try {
      const [refundsRes, warrantiesRes, deliveriesRes] = await Promise.all([
        getRefunds(),
        getWarranties(),
        getDeliveries()
      ])
      setRefunds(refundsRes.data)
      setWarranties(warrantiesRes.data)
      setDeliveries(deliveriesRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  const handleRefund = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const formData = new FormData(e.target)
      await createRefund({
        order_id: parseInt(formData.get('order_id')),
        customer_name: formData.get('customer_name'),
        reason: formData.get('reason'),
        amount: parseFloat(formData.get('amount')) || null
      })
      e.target.reset()
      setActiveForm(null)
      fetchAll()
    } catch (error) {
      console.error('Error creating refund:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleWarranty = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const formData = new FormData(e.target)
      await createWarranty({
        order_id: parseInt(formData.get('order_id')),
        product_id: parseInt(formData.get('product_id')),
        customer_name: formData.get('customer_name')
      })
      e.target.reset()
      setActiveForm(null)
      fetchAll()
    } catch (error) {
      console.error('Error creating warranty:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="support-container">
      <div className="section-header">
        <div>
          <h3>Support Center</h3>
          <p className="section-subtitle">Manage refunds, warranties, and deliveries</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="support-actions">
        <button className="support-action-card" onClick={() => setActiveForm(activeForm === 'refund' ? null : 'refund')}>
          <span className="action-icon">🔄</span>
          <span className="action-label">New Refund</span>
          <span className="action-count">{refunds.length}</span>
        </button>
        <button className="support-action-card" onClick={() => setActiveForm(activeForm === 'warranty' ? null : 'warranty')}>
          <span className="action-icon">🛡️</span>
          <span className="action-label">New Warranty</span>
          <span className="action-count">{warranties.length}</span>
        </button>
        <button className="support-action-card" onClick={() => setActiveForm(activeForm === 'delivery' ? null : 'delivery')}>
          <span className="action-icon">🚚</span>
          <span className="action-label">Update Delivery</span>
          <span className="action-count">{deliveries.length}</span>
        </button>
      </div>

      {/* Forms */}
      {activeForm === 'refund' && (
        <div className="support-form-card">
          <h4>Request Refund</h4>
          <form onSubmit={handleRefund}>
            <div className="form-row">
              <div className="form-group">
                <label>Order ID</label>
                <input name="order_id" type="number" required placeholder="e.g., 1" />
              </div>
              <div className="form-group">
                <label>Customer Name</label>
                <input name="customer_name" type="text" required placeholder="John Doe" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Amount ($)</label>
                <input name="amount" type="number" step="0.01" placeholder="0.00" />
              </div>
              <div className="form-group">
                <label>Reason</label>
                <input name="reason" type="text" placeholder="Defective product" />
              </div>
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Refund Request'}
            </button>
          </form>
        </div>
      )}

      {activeForm === 'warranty' && (
        <div className="support-form-card">
          <h4>Register Warranty</h4>
          <form onSubmit={handleWarranty}>
            <div className="form-row">
              <div className="form-group">
                <label>Order ID</label>
                <input name="order_id" type="number" required placeholder="e.g., 1" />
              </div>
              <div className="form-group">
                <label>Product ID</label>
                <input name="product_id" type="number" required placeholder="e.g., 1" />
              </div>
            </div>
            <div className="form-group">
              <label>Customer Name</label>
              <input name="customer_name" type="text" required placeholder="John Doe" />
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Registering...' : 'Register Warranty'}
            </button>
          </form>
        </div>
      )}

      {/* Data Tables */}
      <div className="support-tables">
        {refunds.length > 0 && (
          <div className="data-section">
            <h4>🔄 Recent Refunds</h4>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Order</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {refunds.slice(0, 5).map(r => (
                    <tr key={r.id}>
                      <td>#{r.id}</td>
                      <td>#{r.order_id}</td>
                      <td>{r.customer_name}</td>
                      <td>${r.amount?.toFixed(2) || '0.00'}</td>
                      <td><span className={`status-badge ${r.status}`}>{r.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {warranties.length > 0 && (
          <div className="data-section">
            <h4>🛡️ Active Warranties</h4>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Order</th>
                    <th>Customer</th>
                    <th>Status</th>
                    <th>End Date</th>
                  </tr>
                </thead>
                <tbody>
                  {warranties.slice(0, 5).map(w => (
                    <tr key={w.id}>
                      <td>#{w.id}</td>
                      <td>#{w.order_id}</td>
                      <td>{w.customer_name}</td>
                      <td><span className={`status-badge ${w.is_active}`}>{w.is_active}</span></td>
                      <td>{w.end_date ? new Date(w.end_date).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Support
