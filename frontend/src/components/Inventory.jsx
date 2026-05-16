import { useState, useEffect } from 'react'
import { getInventoryStatus, getLowStockItems, getAlerts, addInventoryItem, getSuppliers } from '../services/api'
import './Inventory.css'

function Inventory() {
  const [status, setStatus] = useState(null)
  const [lowStock, setLowStock] = useState([])
  const [alerts, setAlerts] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [activeForm, setActiveForm] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchAll() }, [])

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [statusRes, lowStockRes, alertsRes, suppliersRes] = await Promise.all([
        getInventoryStatus(), getLowStockItems(), getAlerts(), getSuppliers()
      ])
      setStatus(statusRes.data)
      setLowStock(lowStockRes.data)
      setAlerts(alertsRes.data)
      setSuppliers(suppliersRes.data)
    } catch (error) {
      console.error('Error fetching inventory:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddStock = async (e) => {
    e.preventDefault()
    const fd = new FormData(e.target)
    try {
      await addInventoryItem(
        parseInt(fd.get('product_id')),
        parseInt(fd.get('quantity')),
        parseInt(fd.get('reorder_point')) || 10
      )
      e.target.reset()
      setActiveForm(null)
      fetchAll()
    } catch (error) {
      console.error('Error adding stock:', error)
    }
  }

  if (loading) return <div className="loading"><div className="loading-spinner" /> Loading inventory...</div>

  return (
    <div className="inventory-container">
      <div className="section-header">
        <div>
          <h3>Inventory Management</h3>
          <p className="section-subtitle">Stock tracking, alerts & suppliers</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setActiveForm(activeForm === 'stock' ? null : 'stock')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Stock
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,58,237,0.1)', color: '#7c3aed' }}>P</div>
          <div className="stat-content">
            <p className="stat-label">Products</p>
            <p className="stat-value">{status?.total_products || 0}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444' }}>!</div>
          <div className="stat-content">
            <p className="stat-label">Low Stock</p>
            <p className="stat-value">{status?.low_stock_count || 0}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>$</div>
          <div className="stat-content">
            <p className="stat-label">Total Value</p>
            <p className="stat-value">${status?.total_inventory_value?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(6,182,212,0.1)', color: '#06b6d4' }}>H</div>
          <div className="stat-content">
            <p className="stat-label">Health</p>
            <p className="stat-value" style={{ fontSize: '20px' }}>{status?.stock_health || 'Good'}</p>
          </div>
        </div>
      </div>

      {activeForm === 'stock' && (
        <div className="form-card slide-in">
          <div className="form-card-header">
            <h4>Add Inventory Item</h4>
            <button className="btn-icon" onClick={() => setActiveForm(null)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <form onSubmit={handleAddStock}>
            <div className="form-row">
              <div className="form-group">
                <label>Product ID</label>
                <input name="product_id" type="number" required placeholder="1" />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input name="quantity" type="number" required placeholder="100" />
              </div>
            </div>
            <div className="form-group">
              <label>Reorder Point</label>
              <input name="reorder_point" type="number" placeholder="10" />
            </div>
            <button type="submit" className="submit-btn">Add to Inventory</button>
          </form>
        </div>
      )}

      {lowStock.length > 0 && (
        <div className="alert-section">
          <div className="alert-section-header">
            <h4>Low Stock Alerts</h4>
            <span className="alert-count">{lowStock.length} items</span>
          </div>
          <div className="alert-cards">
            {lowStock.map((item, idx) => (
              <div key={idx} className="alert-card">
                <div className="alert-icon-wrap">!</div>
                <div className="alert-info">
                  <p className="alert-title">{item.product?.name || `Product #${item.product_id}`}</p>
                  <p className="alert-desc">{item.quantity_in_stock} units left · reorder at {item.reorder_point}</p>
                </div>
                <span className="alert-badge">{item.quantity_in_stock} left</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="inventory-grid">
        {alerts.length > 0 && (
          <div className="card">
            <h4>Active Alerts</h4>
            <div className="alert-list">
              {alerts.slice(0, 5).map((alert, idx) => (
                <div key={idx} className="alert-item">
                  <span className="alert-item-type">{alert.alert_type}</span>
                  <p className="alert-item-msg">{alert.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="card">
          <h4>Suppliers ({suppliers.length})</h4>
          {suppliers.length === 0 ? (
            <p className="no-data">No suppliers registered.</p>
          ) : (
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr><th>Name</th><th>Contact</th><th>Email</th></tr>
                </thead>
                <tbody>
                  {suppliers.slice(0, 5).map(s => (
                    <tr key={s.id}>
                      <td className="cell-name">{s.name}</td>
                      <td>{s.contact_name || 'N/A'}</td>
                      <td>{s.email || 'N/A'}</td>
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

export default Inventory
