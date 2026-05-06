import { useState, useEffect } from 'react'
import { getSalesReport, getTopProducts, getTodaysOrders } from '../services/api'
import './SalesReport.css'

function SalesReport() {
  const [report, setReport] = useState(null)
  const [topProducts, setTopProducts] = useState([])
  const [ordersToday, setOrdersToday] = useState(null)
  const [period, setPeriod] = useState('daily')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAllData()
  }, [period])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      const [reportRes, topRes, ordersRes] = await Promise.all([
        getSalesReport(period),
        getTopProducts(5),
        getTodaysOrders()
      ])
      setReport(reportRes.data)
      setTopProducts(topRes.data)
      setOrdersToday(ordersRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading sales data...</div>

  return (
    <div className="sales-container">
      <div className="section-header">
        <div>
          <h3>Sales Dashboard</h3>
          <p className="section-subtitle">Track your business performance</p>
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="period-selector"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <span className="stat-icon">📊</span>
          <div className="stat-content">
            <p className="stat-label">Total Orders</p>
            <p className="stat-value">{report?.total_orders || 0}</p>
          </div>
        </div>
        <div className="stat-card success">
          <span className="stat-icon">💰</span>
          <div className="stat-content">
            <p className="stat-label">Revenue</p>
            <p className="stat-value">${report?.total_revenue?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="stat-card warning">
          <span className="stat-icon">📦</span>
          <div className="stat-content">
            <p className="stat-label">Today's Orders</p>
            <p className="stat-value">{ordersToday?.count || 0}</p>
          </div>
        </div>
        <div className="stat-card info">
          <span className="stat-icon">📈</span>
          <div className="stat-content">
            <p className="stat-label">Period</p>
            <p className="stat-value" style={{fontSize: '18px'}}>{period.charAt(0).toUpperCase() + period.slice(1)}</p>
          </div>
        </div>
      </div>

      {/* Top Products */}
      <div className="top-products-section">
        <h4>🏆 Top Selling Products</h4>
        <div className="top-products-list">
          {topProducts.length === 0 ? (
            <p className="no-data">No sales data available yet.</p>
          ) : (
            topProducts.map((product, idx) => (
              <div key={idx} className="top-product-item">
                <div className="rank-badge">{idx + 1}</div>
                <div className="product-details">
                  <p className="product-name">{product.product_name}</p>
                  <p className="product-stats">{product.total_sold} sold · ${product.total_revenue?.toFixed(2)}</p>
                </div>
                <div className="revenue-bar">
                  <div
                    className="revenue-fill"
                    style={{width: `${Math.min(100, (product.total_revenue / (topProducts[0]?.total_revenue || 1)) * 100)}%`}}
                  ></div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Orders */}
      {ordersToday && ordersToday.orders && ordersToday.orders.length > 0 && (
        <div className="recent-orders-section">
          <h4>📋 Today's Orders</h4>
          <div className="orders-table-wrapper">
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {ordersToday.orders.slice(0, 5).map(order => (
                  <tr key={order.id}>
                    <td>#{order.id}</td>
                    <td>{order.customer_name}</td>
                    <td>${order.total_amount?.toFixed(2)}</td>
                    <td><span className={`status-badge ${order.status}`}>{order.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default SalesReport
