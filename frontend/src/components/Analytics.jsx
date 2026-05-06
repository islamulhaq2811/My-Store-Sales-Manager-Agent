import { useState, useEffect } from 'react'
import { getSalesTrends, getForecast, getKpiDashboard, getProductPerformance } from '../services/api'
import './Analytics.css'

function Analytics() {
  const [kpi, setKpi] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [trends, setTrends] = useState([])
  const [performance, setPerformance] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchAll() }, [])

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [kpiRes, forecastRes, trendsRes, perfRes] = await Promise.all([
        getKpiDashboard(), getForecast(), getSalesTrends(7), getProductPerformance()
      ])
      setKpi(kpiRes.data)
      setForecast(forecastRes.data)
      setTrends(trendsRes.data)
      setPerformance(perfRes.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading analytics...</div>

  const maxRevenue = Math.max(...trends.map(t => t.revenue), 1)

  return (
    <div className="analytics-container">
      <div className="section-header">
        <div>
          <h3>Analytics Dashboard</h3>
          <p className="section-subtitle">Insights, forecasts & performance metrics</p>
        </div>
        <button className="refresh-btn" onClick={fetchAll}>🔄 Refresh</button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card gradient-purple">
          <span className="kpi-icon">💰</span>
          <div className="kpi-content">
            <p className="kpi-label">Monthly Revenue</p>
            <p className="kpi-value">${kpi?.monthly_revenue?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="kpi-card gradient-blue">
          <span className="kpi-icon">📊</span>
          <div className="kpi-content">
            <p className="kpi-label">Monthly Orders</p>
            <p className="kpi-value">{kpi?.monthly_orders || 0}</p>
          </div>
        </div>
        <div className="kpi-card gradient-green">
          <span className="kpi-icon">📈</span>
          <div className="kpi-content">
            <p className="kpi-label">Avg Order Value</p>
            <p className="kpi-value">${kpi?.avg_order_value?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="kpi-card gradient-orange">
          <span className="kpi-icon">⭐</span>
          <div className="kpi-content">
            <p className="kpi-label">Conversion Rate</p>
            <p className="kpi-value">{kpi?.conversion_rate || 0}%</p>
          </div>
        </div>
      </div>

      {/* Forecast Section */}
      {forecast && (
        <div className="forecast-section">
          <h4>🔮 7-Day Forecast</h4>
          <div className="forecast-card">
            <div className="forecast-main">
              <p className="forecast-label">Predicted Revenue</p>
              <p className="forecast-value">${forecast.forecast_revenue?.toFixed(2)}</p>
            </div>
            <div className="forecast-details">
              <div className="forecast-item">
                <span className="forecast-item-label">Daily Avg</span>
                <span className="forecast-item-value">${forecast.avg_daily_revenue?.toFixed(2)}</span>
              </div>
              <div className="forecast-item">
                <span className="forecast-item-label">Confidence</span>
                <span className={`confidence-badge ${forecast.confidence}`}>{forecast.confidence}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sales Trends Chart */}
      <div className="trends-section">
        <h4>📊 7-Day Sales Trends</h4>
        <div className="chart-container">
          <div className="bar-chart">
            {trends.map((day, idx) => (
              <div key={idx} className="bar-wrapper">
                <div className="bar-value">${day.revenue?.toFixed(0)}</div>
                <div
                  className="bar"
                  style={{height: `${(day.revenue / maxRevenue) * 200}px`}}
                ></div>
                <div className="bar-label">{new Date(day.date).toLocaleDateString('en', {weekday: 'short'})}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Product Performance */}
      <div className="performance-section">
        <h4>🏆 Product Performance</h4>
        <div className="product-performance-list">
          {performance.slice(0, 5).map((p, idx) => (
            <div key={idx} className="performance-item">
              <div className="rank">{idx + 1}</div>
              <div className="perf-details">
                <p className="perf-name">{p.product}</p>
                <p className="perf-stats">{p.units_sold} units · ${p.revenue?.toFixed(2)}</p>
              </div>
              <div className="perf-bar">
                <div
                  className="perf-fill"
                  style={{width: `${Math.min(100, (p.revenue / (performance[0]?.revenue || 1)) * 100)}%`}}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Analytics
