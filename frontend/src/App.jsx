import { useState } from 'react'
import Chat from './components/Chat'
import Products from './components/Products'
import SalesReport from './components/SalesReport'
import Support from './components/Support'
import Marketing from './components/Marketing'
import Analytics from './components/Analytics'
import Inventory from './components/Inventory'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const menuItems = [
    { id: 'chat', label: 'AI Assistant', icon: '🤖' },
    { id: 'products', label: 'Products', icon: '📦' },
    { id: 'sales', label: 'Sales Reports', icon: '📊' },
    { id: 'marketing', label: 'Marketing', icon: '📢' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
    { id: 'inventory', label: 'Inventory', icon: '📦' },
    { id: 'support', label: 'Support', icon: '🎧' },
  ]

  const renderContent = () => {
    switch(activeTab) {
      case 'chat': return <Chat />
      case 'products': return <Products />
      case 'sales': return <SalesReport />
      case 'marketing': return <Marketing />
      case 'analytics': return <Analytics />
      case 'inventory': return <Inventory />
      case 'support': return <Support />
      default: return <Chat />
    }
  }

  return (
    <div className="app">
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            {sidebarOpen && <span className="logo-text">SalesAgent</span>}
          </div>
          <button className="collapse-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {sidebarOpen && <span className="nav-label">{item.label}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          {sidebarOpen && <p className="version">v2.0.0</p>}
        </div>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <div className="header-left">
            <h2>{menuItems.find(m => m.id === activeTab)?.label}</h2>
            <p className="header-subtitle">Powered by Islam Ul Haq</p>
          </div>
          <div className="header-right">
            <div className="status-badge online">
              <span className="status-dot"></span>
              Online
            </div>
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
