import axios from 'axios';

const API_URL = 'http://localhost:8000';
const API_KEY = 'your-secret-api-key-change-this';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

// Chat & Basic
export const chatWithAgent = (query) => api.post('/chat', { query });
export const getProducts = () => api.get('/products');
export const createProduct = (product) => api.post('/products', product);

// Sales
export const createOrder = (order) => api.post('/orders', order);
export const getTodaysOrders = () => api.get('/orders/today');
export const getSalesReport = (period = 'daily') => api.get(`/sales/report?period=${period}`);
export const getTopProducts = (limit = 5) => api.get(`/sales/top-products?limit=${limit}`);

// Support
export const createRefund = (refund) => api.post('/refunds', refund);
export const getRefunds = (orderId) => api.get(`/refunds${orderId ? `?order_id=${orderId}` : ''}`);
export const createWarranty = (warranty) => api.post('/warranties', warranty);
export const getWarranties = (orderId) => api.get(`/warranties${orderId ? `?order_id=${orderId}` : ''}`);
export const createDelivery = (delivery) => api.post('/deliveries', delivery);
export const getDeliveries = (orderId) => api.get(`/deliveries${orderId ? `?order_id=${orderId}` : ''}`);

// Marketing
export const getCampaigns = (status = 'active') => api.get(`/marketing/campaigns?status=${status}`);
export const createCampaign = (campaign) => api.post('/marketing/campaigns', campaign);
export const getPromotions = (status = 'active') => api.get(`/marketing/promotions?status=${status}`);
export const createPromotion = (promotion) => api.post('/marketing/promotions', promotion);
export const getLeads = (status) => api.get(`/marketing/leads${status ? `?status=${status}` : ''}`);
export const addLead = (lead) => api.post('/marketing/leads', lead);
export const getCampaignPerformance = (campaignId) => api.get(`/marketing/performance${campaignId ? `?campaign_id=${campaignId}` : ''}`);

// Analytics
export const getSalesTrends = (days = 30) => api.get(`/analytics/trends?days=${days}`);
export const getForecast = (daysAhead = 7) => api.get(`/analytics/forecast?days_ahead=${daysAhead}`);
export const getCustomerBehavior = () => api.get('/analytics/customer-behavior');
export const getProductPerformance = () => api.get('/analytics/product-performance');
export const getKpiDashboard = () => api.get('/analytics/kpi');

// Inventory
export const getInventoryStatus = () => api.get('/inventory/items');
export const getLowStockItems = () => api.get('/inventory/low-stock');
export const addInventoryItem = (item) => api.post('/inventory/items', item);
export const updateStock = (productId, qtyChange) => api.post(`/inventory/stock/update?product_id=${productId}&quantity_change=${qtyChange}`);
export const getSuppliers = () => api.get('/inventory/suppliers');
export const addSupplier = (supplier) => api.post('/inventory/suppliers', supplier);
export const getPurchaseOrders = () => api.get('/inventory/purchase-orders');
export const createPurchaseOrder = (po) => api.post('/inventory/purchase-orders', po);
export const getAlerts = (unresolvedOnly = true) => api.get(`/inventory/alerts?unresolved_only=${unresolvedOnly}`);

export default api;
