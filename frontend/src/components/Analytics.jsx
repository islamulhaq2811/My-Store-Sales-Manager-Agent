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

  if (loading) return <div className="loading"><div className="loading-spinner" /> Loading analytics...</div>

  const maxRevenue = Math.max(...trends.map(t => t.revenue), 1)

  const getConfidenceColor = (level) => {
    switch(level) {
      case 'high': return { bg: 'rgba(16,185,129,0.1)', color: '#10b981' }
      case 'medium': return { bg: 'rgba(245,158,11,0.1)', color: '#f59e0b' }
      case 'low': return { bg: 'rgba(239,68,68,0.1)', color: '#ef4444' }
      default: return { bg: 'rgba(100,116,139,0.1)', color: '#64748b' }
    }
  }

  return (
    <div className="analytics-container">
      <div className="section-header">
        <div>
          <h3>Analytics Dashboard</h3>
          <p className="section-subtitle">Insights, forecasts & performance metrics</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchAll}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M21 2v6h-6" /><path d="M3 12a9 9 0 0115.6-5.6L21 8" /><path d="M3 22v-6h6" /><path d="M21 12a9 9 0 01-15.6 5.6L3 16" />
          </svg>
          Refresh
        </button>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card kpi-purple">
          <div className="kpi-icon">$</div>
          <div className="kpi-content">
            <p className="kpi-label">Monthly Revenue</p>
            <p className="kpi-value">${kpi?.monthly_revenue?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="kpi-card kpi-blue">
          <div className="kpi-icon">#</div>
          <div className="kpi-content">
            <p className="kpi-label">Monthly Orders</p>
            <p className="kpi-value">{kpi?.monthly_orders || 0}</p>
          </div>
        </div>
        <div className="kpi-card kpi-green">
          <div className="kpi-icon">A</div>
          <div className="kpi-content">
            <p className="kpi-label">Avg Order Value</p>
            <p className="kpi-value">${kpi?.avg_order_value?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        <div className="kpi-card kpi-orange">
          <div className="kpi-icon">%</div>
          <div className="kpi-content">
            <p className="kpi-label">Conversion Rate</p>
            <p className="kpi-value">{kpi?.conversion_rate || 0}%</p>
          </div>
        </div>
      </div>

      <div className="analytics-grid">
        {forecast && (
          <div className="card">
            <h4>7-Day Forecast</h4>
            <div className="forecast-card">
              <div className="forecast-main">
                <p className="forecast-label">Predicted Revenue</p>
                <p className="forecast-value">${forecast.forecast_revenue?.toFixed(2)}</p>
              </div>
              <div className="forecast-divider" />
              <div className="forecast-meta">
                <div className="forecast-meta-item">
                  <span className="meta-label">Daily Avg</span>
                  <span className="meta-value">${forecast.avg_daily_revenue?.toFixed(2)}</span>
                </div>
                <div className="forecast-meta-item">
                  <span className="meta-label">Confidence</span>
                  <span
                    className="confidence-badge"
                    style={getConfidenceColor(forecast.confidence)}
                  >
                    {forecast.confidence}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="card">
          <h4>7-Day Trends</h4>
          <div className="bar-chart">
            {trends.length === 0 ? (
              <p className="no-data">No trend data available.</p>
            ) : (
              trends.map((day, idx) => (
                <div key={idx} className="bar-item">
                  <span className="bar-val">${day.revenue?.toFixed(0)}</span>
                  <div
                    className="bar"
                    style={{ height: `${(day.revenue / maxRevenue) * 180}px` }}
                  />
                  <span className="bar-label">
                    {new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h4>🏆 Product Performance</h4>
        {performance.length === 0 ? (
          <p className="no-data">No performance data available.</p>
        ) : (
          <div className="perf-list">
            {performance.slice(0, 5).map((p, idx) => (
              <div key={idx} className="perf-item">
                <div className="perf-rank">{idx + 1}</div>
                <div className="perf-info">
                  <p className="perf-name">{p.product}</p>
                  <p className="perf-stats">{p.units_sold} units · ${p.revenue?.toFixed(2)}</p>
                </div>
                <div className="perf-bar">
                  <div
                    className="perf-fill"
                    style={{ width: `${Math.min(100, (p.revenue / (performance[0]?.revenue || 1)) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Analytics
