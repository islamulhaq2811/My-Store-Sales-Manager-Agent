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

  if (loading) return <div className="loading"><div className="loading-spinner" /> Loading sales data...</div>

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
          className="period-select"
        >
          <option value="daily">Today</option>
          <option value="weekly">This Week</option>
          <option value="monthly">This Month</option>
        </select>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,58,237,0.1)', color: '#7c3aed' }}>#</div>
          <div className="stat-content">
            <p className="stat-label">Total Orders</p>
            <p className="stat-value">{report?.total_orders || 0}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>$</div>
          <div className="stat-content">
            <p className="stat-label">Revenue</p>
            <p className="stat-value">${report?.total_revenue?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }}>O</div>
          <div className="stat-content">
            <p className="stat-label">Today's Orders</p>
            <p className="stat-value">{ordersToday?.count || 0}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(6,182,212,0.1)', color: '#06b6d4' }}>P</div>
          <div className="stat-content">
            <p className="stat-label">{period.charAt(0).toUpperCase() + period.slice(1)}</p>
            <p className="stat-value" style={{ fontSize: '20px' }}>{report?.period || period}</p>
          </div>
        </div>
      </div>

      <div className="sales-grid">
        <div className="card">
          <h4>
            Top Selling Products
          </h4>
          {topProducts.length === 0 ? (
            <p className="no-data">No sales data available yet.</p>
          ) : (
            <div className="rank-list">
              {topProducts.map((product, idx) => (
                <div key={idx} className="rank-item">
                  <div className="rank-badge">{idx + 1}</div>
                  <div className="rank-details">
                    <p className="rank-name">{product.product_name}</p>
                    <p className="rank-stats">{product.total_sold} sold · ${product.total_revenue?.toFixed(2)}</p>
                  </div>
                  <div className="rank-bar">
                    <div
                      className="rank-fill"
                      style={{ width: `${Math.min(100, (product.total_revenue / (topProducts[0]?.total_revenue || 1)) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {ordersToday && ordersToday.orders && ordersToday.orders.length > 0 && (
          <div className="card">
            <h4>
            Today's Orders
            </h4>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {ordersToday.orders.slice(0, 5).map(order => (
                    <tr key={order.id}>
                      <td><span className="order-id">#{order.id}</span></td>
                      <td>{order.customer_name}</td>
                      <td className="amount-cell">${order.total_amount?.toFixed(2)}</td>
                      <td><span className={`status-badge ${order.status}`}>{order.status}</span></td>
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

export default SalesReport
