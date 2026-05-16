import { useState, useEffect } from 'react'
import { getProducts, createProduct } from '../services/api'
import './Products.css'

function Products() {
  const [products, setProducts] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ name: '', price: '', category: '' })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => { fetchProducts() }, [])

  const fetchProducts = async () => {
    try {
      const res = await getProducts()
      setProducts(res.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    } finally {
      setFetching(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createProduct({
        name: formData.name,
        price: parseFloat(formData.price),
        category: formData.category
      })
      setFormData({ name: '', price: '', category: '' })
      setShowForm(false)
      fetchProducts()
    } catch (error) {
      console.error('Error creating product:', error)
    } finally {
      setLoading(false)
    }
  }

  if (fetching) return <div className="loading"><div className="loading-spinner" /> Loading products...</div>

  return (
    <div className="products-container">
      <div className="section-header">
        <div>
          <h3>Products</h3>
          <p className="section-subtitle">Manage your product catalog</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          {showForm ? 'Cancel' : 'Add Product'}
        </button>
      </div>

      {showForm && (
        <div className="form-card slide-in">
          <div className="form-card-header">
            <h4>New Product</h4>
            <button className="btn-icon" onClick={() => setShowForm(false)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  placeholder="e.g., iPhone Cable"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <input
                  type="text"
                  placeholder="e.g., Electronics"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                />
              </div>
            </div>
            <div className="form-group">
              <label>Price ($)</label>
              <input
                type="number"
                step="0.01"
                placeholder="0.00"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
                required
              />
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Adding...' : 'Add Product'}
            </button>
          </form>
        </div>
      )}

      {products.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">P</span>
          <p>No products yet. Add your first product!</p>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Product
          </button>
        </div>
      ) : (
        <div className="products-grid">
          {products.map((product, idx) => (
            <div key={product.id} className="product-card" style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="product-card-top">
                <div className="product-icon-wrap gradient-purple">
                  <span className="product-icon">P</span>
                </div>
                <span className="product-category-badge">{product.category || 'General'}</span>
              </div>
              <div className="product-card-body">
                <h4>{product.name}</h4>
                <div className="product-price">${product.price.toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Products
