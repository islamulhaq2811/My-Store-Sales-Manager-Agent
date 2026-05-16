import { useState } from 'react'
import Chat from './components/Chat'
import Products from './components/Products'
import SalesReport from './components/SalesReport'
import Support from './components/Support'
import Marketing from './components/Marketing'
import Analytics from './components/Analytics'
import Inventory from './components/Inventory'
import Mystore from './components/Mystore'
import './App.css'

const menuItems = [
  { id: 'chat', label: 'AI Assistant', icon: '⬡', gradient: 'gradient-purple' },
  { id: 'products', label: 'Products', icon: '⊞', gradient: 'gradient-blue' },
  { id: 'sales', label: 'Sales Reports', icon: '⊟', gradient: 'gradient-green' },
  { id: 'marketing', label: 'Marketing', icon: '⊡', gradient: 'gradient-orange' },
  { id: 'analytics', label: 'Analytics', icon: '⊠', gradient: 'gradient-rose' },
  { id: 'inventory', label: 'Inventory', icon: '▦', gradient: 'gradient-blue' },
  { id: 'support', label: 'Support', icon: '⊕', gradient: 'gradient-purple' },
  { id: 'mystore', label: 'MyStore', icon: 'S', gradient: 'gradient-green' },
]

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const renderContent = () => {
    switch(activeTab) {
      case 'chat': return <Chat />
      case 'products': return <Products />
      case 'sales': return <SalesReport />
      case 'marketing': return <Marketing />
      case 'analytics': return <Analytics />
      case 'inventory': return <Inventory />
      case 'support': return <Support />
      case 'mystore': return <Mystore />
      default: return <Chat />
    }
  }

  return (
    <div className="app">
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon-wrap">
              <span className="logo-icon">⚡</span>
            </div>
            {sidebarOpen && (
              <div className="logo-text-wrap">
                <span className="logo-text">SalesAgent</span>
                <span className="logo-sub">Management Suite</span>
              </div>
            )}
          </div>
          <button className="collapse-btn" onClick={() => setSidebarOpen(!sidebarOpen)} title={sidebarOpen ? 'Collapse' : 'Expand'}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <path d={sidebarOpen ? "M15 18l-6-6 6-6" : "M9 18l6-6-6-6"} />
            </svg>
          </button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className={`nav-icon-wrap ${item.gradient}`}>
                <span className="nav-icon">{item.icon}</span>
              </span>
              {sidebarOpen && <span className="nav-label">{item.label}</span>}
              {sidebarOpen && activeTab === item.id && <span className="nav-indicator" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          {sidebarOpen && (
            <div className="user-card">
              <div className="user-avatar">IH</div>
              <div className="user-info">
                <span className="user-name">Islam Ul Haq</span>
                <span className="user-role">Administrator</span>
              </div>
            </div>
          )}
        </div>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <div className="header-left">
            <div className="header-title-row">
              <h2>{menuItems.find(m => m.id === activeTab)?.label}</h2>
              <div className="header-badge">
                <span className="status-dot" />
                Online
              </div>
            </div>
            <p className="header-subtitle">Sales Manager Agent v2.0</p>
          </div>
          <div className="header-right">
            <button className="header-action-btn" title="Notifications">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 01-3.46 0" />
              </svg>
              <span className="notification-dot" />
            </button>
            <div className="header-avatar">IH</div>
          </div>
        </header>
        <div className="content-wrapper">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}

export default App
