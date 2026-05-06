import { useState, useEffect } from 'react'
import { getProducts, createProduct, createOrder } from '../services/api'
import './Products.css'

function Products() {
  const [products, setProducts] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ name: '', price: '', category: '' })
  const [loading, setLoading] = useState(false)

  useEffect(() => { fetchProducts() }, [])

  const fetchProducts = async () => {
    try {
      const res = await getProducts()
      setProducts(res.data)
    } catch (error) {
      console.error('Error fetching products:', error)
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

  return (
    <div className="products-container">
      <div className="section-header">
        <div>
          <h3>Products</h3>
          <p className="section-subtitle">Manage your product catalog</p>
        </div>
        <button className="add-btn" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✕ Cancel' : '+ Add Product'}
        </button>
      </div>

      {showForm && (
        <div className="product-form-card">
          <h4>New Product</h4>
          <form onSubmit={handleSubmit}>
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
            <div className="form-row">
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
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Adding...' : 'Add Product'}
            </button>
          </form>
        </div>
      )}

      <div className="products-grid">
        {products.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📦</span>
            <p>No products yet. Add your first product!</p>
          </div>
        ) : (
          products.map(product => (
            <div key={product.id} className="product-card">
              <div className="product-icon">📦</div>
              <div className="product-info">
                <h4>{product.name}</h4>
                <p className="product-category">{product.category || 'Uncategorized'}</p>
              </div>
              <div className="product-price">${product.price.toFixed(2)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Products
