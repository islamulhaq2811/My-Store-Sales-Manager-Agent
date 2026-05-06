import { useState, useEffect } from 'react'
import { getInventoryStatus, getLowStockItems, getAlerts, addInventoryItem, getSuppliers, createPurchaseOrder } from '../services/api'
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

  if (loading) return <div className="loading">Loading inventory...</div>

  return (
    <div className="inventory-container">
      <div className="section-header">
        <div>
          <h3>Inventory Management</h3>
          <p className="section-subtitle">Stock tracking, alerts & suppliers</p>
        </div>
        <button className="add-btn" onClick={() => setActiveForm(activeForm === 'stock' ? null : 'stock')}>
          + Add Stock
        </button>
      </div>

      {/* Status Cards */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <span className="stat-icon">📦</span>
          <div className="stat-content">
            <p className="stat-label">Products</p>
            <p className="stat-value">{status?.total_products || 0}</p>
          </div>
        </div>
        <div className="stat-card danger">
          <span className="stat-icon">⚠️</span>
          <div className="stat-content">
            <p className="stat-label">Low Stock</p>
            <p className="stat-value">{status?.low_stock_count || 0}</p>
          </div>
        </div>
        <div className="stat-card success">
          <span className="stat-icon">💰</span>
          <div className="stat-content">
            <p className="stat-label">Total Value</p>
            <p className="stat-value">${status?.total_inventory_value?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="stat-card info">
          <span className="stat-icon">📊</span>
          <div className="stat-content">
            <p className="stat-label">Health</p>
            <p className="stat-value" style={{fontSize: '18px'}}>{status?.stock_health || 'Good'}</p>
          </div>
        </div>
      </div>

      {/* Add Stock Form */}
      {activeForm === 'stock' && (
        <div className="form-card">
          <h4>Add Inventory Item</h4>
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

      {/* Low Stock Alert */}
      {lowStock.length > 0 && (
        <div className="alert-section">
          <h4>⚠️ Low Stock Alerts</h4>
          <div className="alert-list">
            {lowStock.map((item, idx) => (
              <div key={idx} className="alert-card">
                <span className="alert-icon">⚠️</span>
                <div className="alert-content">
                  <p className="alert-product">{item.product?.name || `Product #${item.product_id}`}</p>
                  <p className="alert-details">{item.quantity_in_stock} units left (reorder at {item.reorder_point})</p>
                </div>
                <span className="alert-badge low">Low Stock</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="data-section">
          <h4>🔔 Active Alerts</h4>
          <div className="alert-list">
            {alerts.slice(0, 5).map((alert, idx) => (
              <div key={idx} className="alert-item">
                <span className="alert-type">{alert.alert_type}</span>
                <p className="alert-message">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suppliers */}
      <div className="data-section">
        <h4>🏭 Suppliers ({suppliers.length})</h4>
        <div className="table-wrapper">
          {suppliers.length === 0 ? <p className="no-data">No suppliers registered.</p> : (
            <table className="data-table">
              <thead>
                <tr><th>Name</th><th>Contact</th><th>Email</th></tr>
              </thead>
              <tbody>
                {suppliers.slice(0, 5).map(s => (
                  <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.contact_name || 'N/A'}</td>
                    <td>{s.email || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default Inventory
