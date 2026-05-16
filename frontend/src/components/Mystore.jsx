import { useState, useEffect } from 'react'
import { getMystoreStatus, getMystoreTables, getMystoreTableData, getMystoreStats, getMystoreTableSchema, executeMystoreQuery } from '../services/api'
import './Mystore.css'

function Mystore() {
  const [status, setStatus] = useState(null)
  const [tables, setTables] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedTable, setSelectedTable] = useState(null)
  const [tableData, setTableData] = useState(null)
  const [tableSchema, setTableSchema] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dataLoading, setDataLoading] = useState(false)
  const [sqlQuery, setSqlQuery] = useState('')
  const [sqlResult, setSqlResult] = useState(null)
  const [sqlLoading, setSqlLoading] = useState(false)
  const [sqlError, setSqlError] = useState(null)

  useEffect(() => {
    fetchStatus()
  }, [])

  const fetchStatus = async () => {
    setLoading(true)
    try {
      const [statusRes, tablesRes, statsRes] = await Promise.all([
        getMystoreStatus(),
        getMystoreTables(),
        getMystoreStats()
      ])
      setStatus(statusRes.data)
      setTables(tablesRes.data?.tables || [])
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error fetching Mystore data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTable = async (tableName) => {
    setSelectedTable(tableName)
    setDataLoading(true)
    setSqlResult(null)
    try {
      const [dataRes, schemaRes] = await Promise.all([
        getMystoreTableData(tableName, 100),
        getMystoreTableSchema(tableName)
      ])
      setTableData(dataRes.data)
      setTableSchema(schemaRes.data)
    } catch (error) {
      console.error('Error loading table:', error)
      setTableData(null)
    } finally {
      setDataLoading(false)
    }
  }

  const runSql = async () => {
    if (!sqlQuery.trim()) return
    setSqlLoading(true)
    setSqlError(null)
    setSqlResult(null)
    try {
      const res = await executeMystoreQuery(sqlQuery)
      if (res.data.response) {
        setSqlResult({ message: res.data.response })
      } else if (res.data.error) {
        setSqlError(res.data.error)
      } else {
        setSqlResult(res.data)
      }
    } catch (error) {
      setSqlError(error.message || 'Query failed')
    } finally {
      setSqlLoading(false)
    }
  }

  if (loading) return <div className="loading"><div className="loading-spinner" /> Connecting to Mystore...</div>

  if (status && !status.configured) {
    return (
      <div className="mystore-container">
        <div className="section-header">
          <div>
            <h3>Mystore E-Commerce</h3>
            <p className="section-subtitle">Connect your online store</p>
          </div>
        </div>
        <div className="setup-card">
          <div className="setup-icon">S</div>
          <h3>Connect Your Mystore Database</h3>
          <p>Add your Mystore MySQL database credentials to the <code>.env</code> file:</p>
          <div className="setup-code">
            MYSTORE_DB_HOST=your-database-host<br />
            MYSTORE_DB_PORT=3306<br />
            MYSTORE_DB_USER=your-username<br />
            MYSTORE_DB_PASSWORD=your-password<br />
            MYSTORE_DB_NAME=mystore
          </div>
        </div>
      </div>
    )
  }

  const totalRecords = stats?.total_records || 0

  return (
    <div className="mystore-container">
      <div className="section-header">
        <div>
          <h3>Mystore E-Commerce</h3>
          <p className="section-subtitle">{tables.length} tables &middot; {totalRecords} total records</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchStatus}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M21 2v6h-6" /><path d="M3 12a9 9 0 0115.6-5.6L21 8" /><path d="M3 22v-6h6" /><path d="M21 12a9 9 0 01-15.6 5.6L3 16" />
          </svg>
          Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,58,237,0.1)', color: '#7c3aed' }}>T</div>
          <div className="stat-content">
            <p className="stat-label">Tables</p>
            <p className="stat-value">{tables.length}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>R</div>
          <div className="stat-content">
            <p className="stat-label">Total Records</p>
            <p className="stat-value">{totalRecords.toLocaleString()}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(6,182,212,0.1)', color: '#06b6d4' }}>DB</div>
          <div className="stat-content">
            <p className="stat-label">Database</p>
            <p className="stat-value" style={{ fontSize: '16px' }}>Connected</p>
          </div>
        </div>
      </div>

      <div className="mystore-layout">
        <div className="mystore-sidebar">
          <h4>Tables</h4>
          <div className="table-list">
            {tables.map(t => (
              <button
                key={t}
                className={`table-list-item ${selectedTable === t ? 'active' : ''}`}
                onClick={() => loadTable(t)}
              >
                <span className="table-list-icon">{t.charAt(0).toUpperCase()}</span>
                <span className="table-list-name">{t}</span>
                <span className="table-list-count">{stats?.stats?.[t]?.record_count || 0}</span>
              </button>
            ))}
            {tables.length === 0 && <p className="no-data">No tables found</p>}
          </div>
        </div>

        <div className="mystore-content">
          {!selectedTable && !sqlResult && (
            <div className="mystore-welcome">
              <div className="welcome-icon">S</div>
              <h3>Mystore Connected</h3>
              <p>Select a table from the left to browse data, or run a custom SQL query below.</p>
            </div>
          )}

          {dataLoading && (
            <div className="loading"><div className="loading-spinner" /> Loading table data...</div>
          )}

          {tableData && !dataLoading && (
            <div className="table-viewer">
              <div className="table-viewer-header">
                <h4>{selectedTable}</h4>
                <span className="record-count">{tableData.total} records</span>
              </div>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      {tableData.columns.map(col => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.rows.map((row, idx) => (
                      <tr key={idx}>
                        {tableData.columns.map(col => {
                          const val = row[col]
                          return (
                            <td key={col} title={String(val)}>
                              {val === null ? <span className="null-value">NULL</span>
                                : typeof val === 'object' && val instanceof Date ? val.toLocaleDateString()
                                : String(val).substring(0, 50)}
                            </td>
                          )
                        })}
                      </tr>
                    ))}
                    {tableData.rows.length === 0 && (
                      <tr><td colSpan={tableData.columns.length} className="no-data">No records</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {sqlResult && !sqlResult.error && (
            <div className="table-viewer">
              <div className="table-viewer-header">
                <h4>Query Result</h4>
                <span className="record-count">{sqlResult.total || sqlResult.affected || (sqlResult.message ? 'response' : '0')} {sqlResult.total ? 'rows' : sqlResult.affected ? 'affected' : ''}</span>
              </div>
              {sqlResult.message && (
                <div className="sql-message">{sqlResult.message}</div>
              )}
              {sqlResult.columns && (
                <div className="table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {sqlResult.columns.map(col => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sqlResult.rows?.map((row, idx) => (
                        <tr key={idx}>
                          {sqlResult.columns.map(col => (
                            <td key={col} title={String(row[col])}>
                              {row[col] === null ? <span className="null-value">NULL</span>
                                : String(row[col]).substring(0, 50)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {sqlError && (
            <div className="error-card">
              <p className="error-title">Query Error</p>
              <p className="error-msg">{sqlError}</p>
            </div>
          )}
        </div>
      </div>

      <div className="sql-section">
        <h4>Custom SQL Query</h4>
        <div className="sql-input-row">
          <input
            type="text"
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runSql()}
            placeholder="SELECT * FROM products LIMIT 10"
            className="sql-input"
          />
          <button className="btn btn-primary" onClick={runSql} disabled={sqlLoading || !sqlQuery.trim()}>
            {sqlLoading ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Mystore
