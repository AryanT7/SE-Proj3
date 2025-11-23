"use client";
import React, { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import Navbar from '../components/Navbar';

/**
 * BundleCard component to display snack bundle information.
 */
const BundleCard = ({ bundle, onAddBundle, isAdmin, onEdit, onDelete }: any) => (
  <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 shadow-xl rounded-xl transition hover:shadow-2xl hover:scale-[1.02] duration-300 transform border-2 border-purple-200">
    <div className="flex justify-between items-start mb-2">
      <h2 className="text-xl font-semibold text-purple-800 flex items-center">
        🎁 {bundle.name}
        <span className="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
          BUNDLE
        </span>
      </h2>
      {isAdmin && (
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(bundle)}
            className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
            title="Edit Bundle"
          >
            ✏️ Edit
          </button>
          <button
            onClick={() => onDelete(bundle.id)}
            className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
            title="Delete Bundle"
          >
            🗑️ Delete
          </button>
        </div>
      )}
    </div>

    {/* Description */}
    <p className="text-sm text-gray-600 mb-3">{bundle.description}</p>

    {/* Items included */}
    <div className="mb-3 p-2 bg-white rounded-lg">
      <p className="text-xs font-semibold text-gray-700 mb-1">Includes:</p>
      <ul className="text-xs text-gray-600 space-y-1">
        {bundle.items.map((item: any, idx: number) => (
          <li key={idx}>• {item.quantity}x {item.product_name}</li>
        ))}
      </ul>
    </div>

    {/* Pricing */}
    <div className="mb-3">
      <div className="flex items-baseline gap-2">
        <p className="text-3xl font-bold text-purple-600">
          ${bundle.total_price.toFixed(2)}
        </p>
        <span className="text-sm line-through text-gray-400">
          ${bundle.original_price.toFixed(2)}
        </span>
      </div>
      <p className="text-xs font-semibold text-green-600 mt-1">
        Save 20% on this bundle!
      </p>
    </div>

    {/* ADD TO CART BUTTON */}
    <button
      onClick={() => onAddBundle(bundle)}
      className="mt-4 w-full py-2 px-4 rounded-lg font-bold transition duration-200 shadow-md bg-purple-600 hover:bg-purple-700 text-white"
    >
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 inline mr-2 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
      Add Bundle to Cart
    </button>
  </div>
);

/**
 * ProductCard component to display individual product information.
 * Uses robust Tailwind styling for a clean, responsive card layout.
 */
const ProductCard = ({ product, supplierName, onAddToCart }: any) => (
  <div className="p-4 bg-white shadow-xl rounded-xl transition hover:shadow-2xl hover:scale-[1.02] duration-300 transform border border-gray-100">
    <div className="flex justify-between items-start mb-2">
      <h2 className="text-xl font-semibold text-gray-800">{product.name}</h2>
      <span className={`px-3 py-1 text-xs font-medium rounded-full ${product.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
        {product.is_available ? 'Available' : 'Out of Stock'}
      </span>
    </div>

    {/* ADD SUPPLIER NAME HERE */}
    <p className="text-xs text-gray-500 mb-3 font-medium">
      Supplier: {supplierName}
    </p>

    {/* Display the price prominently */}
    <p className="text-3xl font-bold text-indigo-600 mb-3">${product.unit_price.toFixed(2)}</p>

    {/* ADD TO CART BUTTON */}
    <button
      onClick={() => onAddToCart(product.id)}
      disabled={!product.is_available || product.inventory_quantity === 0}
      className={`mt-4 w-full py-2 px-4 rounded-lg font-bold transition duration-200 shadow-md ${product.is_available && product.inventory_quantity > 0
        ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      title={product.is_available && product.inventory_quantity > 0 ? "Add to Cart" : "Currently unavailable"}
    >
      {/* Icon: Shopping Cart */}
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 inline mr-2 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
      {product.inventory_quantity === 0 ? 'Sold Out' : 'Add to Cart'}
    </button>

    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm text-gray-600">
      {/* Category */}
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>
        <span className="font-medium">Category:</span> {product.category}
      </div>
      {/* Size */}
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c1.657 0 3 .895 3 2s-1.343 2-3 2-3-.895-3-2 1.343-2 3-2z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2-1.343-2-3-2z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 4v4" /></svg>
        <span className="font-medium">Size:</span> {product.size}
      </div>
      {/* Inventory */}
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 1.1.9 2 2 2h12a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" /></svg>
        <span className="font-medium">Inventory:</span> {product.inventory_quantity}
      </div>
      {/* Discount */}
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 11.5V14m0-2.5v2.5M15 11.5V14m0-2.5v2.5M8 10a1 1 0 011-1h6a1 1 0 011 1v4a1 1 0 01-1 1H9a1 1 0 01-1-1v-4zM7 4h10a2 2 0 012 2v1h-14V6a2 2 0 012-2z" /></svg>
        <span className="font-medium">Discount:</span> {product.discount * 100}%
      </div>
    </div>
  </div>
);

/**
 * Main application component responsible for fetching and displaying the menu.
 */
const App = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [bundles, setBundles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [supplierMap, setSupplierMap] = useState<any>({}); // <-- ADD THIS LINE
  const [isAdmin, setIsAdmin] = useState(false);
  const [showBundleForm, setShowBundleForm] = useState(false);
  const [editingBundle, setEditingBundle] = useState<any>(null);
  const [bundleFormData, setBundleFormData] = useState({
    name: '',
    description: '',
    original_price: 0,
    product_items: [] as { product_id: number; quantity: number }[],
  });

  // Helper function for fetching with exponential backoff
  const exponentialBackoffFetch = async (url: any, options: any, retries = 3) => {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response;
      } catch (e) {
        if (i < retries - 1) {
          const delay = Math.pow(2, i) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          throw e;
        }
      }
    }
  };

  // Function to handle adding a product to the cart
  const addToCart = async (productId: any) => {
    try {
      const response = await exponentialBackoffFetch(`http://localhost:5000/api/customers/${Cookies.get('user_id')}/cart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          quantity: 1 // Always adding 1 unit for simplicity
        }),
      });

      if (!response) throw new Error("Add to cart request failed.");

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Use console.log for success feedback (since alert() is forbidden)
      console.log(`✅ Success: Product ${productId} added to cart. Cart Item ID: ${data.cart_item_id}`);
      alert('Product added to cart!');

    } catch (err: unknown) {
      console.error("Failed to add item to cart:", err instanceof Error ? err.message : "");
      // Log an error if the request fails
      console.error(`❌ Error adding product ${productId}: ${err instanceof Error ? err.message : ""}`);
      alert('Failed to add product to cart: ' + (err instanceof Error ? err.message : ""));
    }
  };

  // Function to handle adding a bundle to the cart
  const addBundleToCart = async (bundle: any) => {
    try {
      const customerId = Cookies.get('user_id');
      if (!customerId) {
        alert('Please log in to add items to cart');
        return;
      }

      const response = await exponentialBackoffFetch(`http://localhost:5000/api/customers/${customerId}/cart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bundle_id: bundle.id,
          quantity: 1
        }),
      });

      if (!response) throw new Error("Failed to add bundle to cart");

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      alert(`Bundle "${bundle.name}" added to cart!`);
    } catch (err: unknown) {
      console.error("Failed to add bundle to cart:", err instanceof Error ? err.message : "");
      alert('Failed to add bundle to cart: ' + (err instanceof Error ? err.message : ""));
    }
  };

  // Function to fetch all supplier names and create a map
  const fetchSuppliers = async () => {
    try {
      // Endpoint is now relative: /api/suppliers/all becomes just '/suppliers/all'
      const response = await exponentialBackoffFetch('http://localhost:5000/api/suppliers/all', {
        method: 'GET',
        // No headers/body needed for this standard GET route
      });

      if (!response) throw new Error("Supplier list failed.");

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      // Create a map: { 'supplierId1': 'CompanyName A', ...}
      const map = data.suppliers.reduce((acc: any, s: any) => {
        // Ensure user_id is a string for mapping consistency
        acc[String(s.user_id)] = s.company_name;
        return acc;
      }, {});

      setSupplierMap(map);
      return map;

    } catch (err) {
      console.error("Failed to fetch suppliers:", err);
      return {};
    }
  };

  /**
   * stores products to state
   */
  const fetchProducts = async () => {
    setLoading(true);
    setError("");
    try {
      // 1. FETCH SUPPLIERS FIRST
      const suppliers = await fetchSuppliers(); // Gets the ID -> Name Map

      // 2. FETCH PRODUCTS using the new /products/menu route
      const response = await exponentialBackoffFetch('http://localhost:5000/api/products/menu', {
        method: 'GET',
        // NOTE: No headers or body are needed for this standard GET route!
      });

      if (!response) throw new Error("Network request failed or returned no response.");

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      // 3. ENRICH AND SANITIZE PRODUCT DATA
      const enrichedProducts = data.products.map((p: any) => {
        // Find the supplier name using the product's supplier_id
        const name = suppliers[String(p.supplier_id)] || "Unknown Supplier";

        return {
          ...p,
          supplierName: name, // <-- Attach the fetched name
          unit_price: parseFloat(p.unit_price) || 0.0,
          inventory_quantity: parseInt(p.inventory_quantity) || 0,
          size: p.size || "Standard",
          keywords: Array.isArray(p.keywords) ? p.keywords : [],
          discount: parseFloat(p.discount) || 0.0,
          is_available: !!p.is_available
        };
      });

      // NEW FILTER: Only keep products whose supplierName is NOT "Unknown Supplier"
      const filteredProducts = enrichedProducts.filter(
        (p: any) => p.supplierName !== "Unknown Supplier"
      );

      setProducts(filteredProducts); // <-- Use the filtered list

    } catch (err) {
      console.error("Failed to fetch products:", err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch snack bundles from the backend
   */
  const fetchBundles = async () => {
    try {
      const response = await exponentialBackoffFetch('http://localhost:5000/api/bundles', {
        method: 'GET',
      });

      if (!response) throw new Error("Failed to fetch bundles.");

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setBundles(data.bundles || []);
    } catch (err) {
      console.error("Failed to fetch bundles:", err);
    }
  };

  /**
   * Check if current user is an admin
   */
  const checkAdminStatus = async () => {
    const userId = Cookies.get('user_id');
    if (!userId) return;

    try {
      const response = await fetch(`http://localhost:5000/api/staff/${userId}`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const staffData = await response.json();
        setIsAdmin(staffData.role === 'admin');
      }
    } catch (err) {
      console.error("Failed to check admin status:", err);
    }
  };

  /**
   * Handle bundle creation
   */
  const handleCreateBundle = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const calculatedOriginalPrice = bundleFormData.product_items.reduce((total, item) => {
        const product = products.find((p: any) => p.id === item.product_id);
        return total + (product ? product.unit_price * item.quantity : 0);
      }, 0);

      const url = editingBundle 
        ? `http://localhost:5000/api/bundles/${editingBundle.id}`
        : 'http://localhost:5000/api/bundles';
      
      const method = editingBundle ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ...bundleFormData,
          original_price: calculatedOriginalPrice,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to ${editingBundle ? 'update' : 'create'} bundle`);
      }

      alert(`Bundle ${editingBundle ? 'updated' : 'created'} successfully!`);
      setBundleFormData({
        name: '',
        description: '',
        original_price: 0,
        product_items: [],
      });
      setEditingBundle(null);
      setShowBundleForm(false);
      fetchBundles();
    } catch (err) {
      alert(`Error ${editingBundle ? 'updating' : 'creating'} bundle: ` + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleEditBundle = (bundle: any) => {
    setEditingBundle(bundle);
    setBundleFormData({
      name: bundle.name,
      description: bundle.description,
      original_price: bundle.original_price,
      product_items: bundle.items.map((item: any) => ({
        product_id: item.product_id,
        quantity: item.quantity
      })),
    });
    setShowBundleForm(true);
  };

  const handleDeleteBundle = async (bundleId: number) => {
    if (!confirm('Are you sure you want to delete this bundle?')) return;

    try {
      const response = await fetch(`http://localhost:5000/api/bundles/${bundleId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete bundle');
      }

      alert('Bundle deleted successfully!');
      fetchBundles();
    } catch (err) {
      alert('Error deleting bundle: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleAddProductToBundle = () => {
    setBundleFormData({
      ...bundleFormData,
      product_items: [...bundleFormData.product_items, { product_id: products[0]?.id || 0, quantity: 1 }],
    });
  };

  const handleRemoveProductFromBundle = (index: number) => {
    const newItems = bundleFormData.product_items.filter((_, i) => i !== index);
    setBundleFormData({ ...bundleFormData, product_items: newItems });
  };

  const handleBundleProductChange = (index: number, field: 'product_id' | 'quantity', value: number) => {
    const newItems = [...bundleFormData.product_items];
    newItems[index][field] = value;
    setBundleFormData({ ...bundleFormData, product_items: newItems });
  };

  const calculateBundleTotal = () => {
    return bundleFormData.product_items.reduce((total, item) => {
      const product = products.find((p: any) => p.id === item.product_id);
      return total + (product ? product.unit_price * item.quantity : 0);
    }, 0);
  };

  // Fetch data on component mount
  useEffect(() => {
    fetchProducts();
    fetchBundles();
    checkAdminStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-8 font-sans">
      <section className="max-w-7xl mx-auto">
        <header className="text-center mb-10 pt-4">
          <div className="flex justify-between items-center max-w-7xl mx-auto mb-4">
            <div className="flex-1"></div>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-indigo-800 tracking-tight flex-1 text-center">
              Our Menu
            </h1>
            <div className="flex-1 flex justify-end">
              {isAdmin && (
                <button
                  onClick={() => setShowBundleForm(!showBundleForm)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium text-sm shadow-md"
                >
                  {showBundleForm ? 'Cancel' : '+ Create Bundle'}
                </button>
              )}
            </div>
          </div>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Explore our curated selection of products. Inventory status is updated in real-time.
          </p>
        </header>

        {/* Bundle Creation Form (Admin Only) */}
        {isAdmin && showBundleForm && (
          <div className="mb-8 p-6 border-2 border-purple-300 rounded-xl bg-purple-50 shadow-lg">
            <h3 className="text-2xl font-bold text-purple-800 mb-4">
              {editingBundle ? 'Edit Snack Bundle' : 'Create New Snack Bundle'}
            </h3>
            <form onSubmit={handleCreateBundle} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Bundle Name *</label>
                <input
                  type="text"
                  value={bundleFormData.name}
                  onChange={(e) => setBundleFormData({ ...bundleFormData, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., Movie Night Special"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Description</label>
                <textarea
                  value={bundleFormData.description}
                  onChange={(e) => setBundleFormData({ ...bundleFormData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={2}
                  placeholder="Describe what's included in this bundle"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">Products in Bundle *</label>
                  <button
                    type="button"
                    onClick={handleAddProductToBundle}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium"
                  >
                    + Add Product
                  </button>
                </div>

                {bundleFormData.product_items.length === 0 && (
                  <p className="text-sm text-gray-500 italic">No products added yet. Click "+ Add Product" to start.</p>
                )}

                {bundleFormData.product_items.map((item, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <select
                      value={item.product_id}
                      onChange={(e) => handleBundleProductChange(index, 'product_id', parseInt(e.target.value))}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      {products.filter((p: any) => p.is_available).map((product: any) => (
                        <option key={product.id} value={product.id}>
                          {product.name} - ${product.unit_price.toFixed(2)} ({product.category})
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => handleBundleProductChange(index, 'quantity', parseInt(e.target.value))}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      placeholder="Qty"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveProductFromBundle(index)}
                      className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="space-y-1">
                  <p className="text-sm text-gray-700">
                    Original Price: <span className="line-through">${calculateBundleTotal().toFixed(2)}</span>
                  </p>
                  <p className="text-lg font-bold text-green-600">
                    Discounted Price (20% off): ${(calculateBundleTotal() * 0.80).toFixed(2)}
                  </p>
                  <p className="text-xs text-green-600">
                    You save: ${(calculateBundleTotal() * 0.20).toFixed(2)}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={bundleFormData.product_items.length === 0}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {editingBundle ? 'Update Bundle' : 'Create Bundle'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowBundleForm(false);
                    setEditingBundle(null);
                    setBundleFormData({
                      name: '',
                      description: '',
                      original_price: 0,
                      product_items: [],
                    });
                  }}
                  className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Loading State UI */}
        {loading && (
          <div className="flex flex-col justify-center items-center h-64 text-indigo-600">
            <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-indigo-500"></div>
            <p className="mt-4 text-xl font-medium">Fetching the latest menu...</p>
          </div>
        )}

        {/* Error State UI */}
        {error && !loading && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-lg shadow max-w-lg mx-auto mb-6" role="alert">
            <strong className="font-bold">Connection Issue:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        {/* Empty Menu State UI */}
        {!loading && products.length === 0 && bundles.length === 0 && !error && (
          <div className="text-center py-12 bg-white rounded-xl shadow-lg border border-gray-100">
            <p className="text-xl text-gray-500 font-medium">The menu is currently empty.</p>
            <p className="text-md text-gray-400 mt-1">Please check back soon for new additions!</p>
          </div>
        )}

        {/* Bundles Section */}
        {!loading && bundles.length > 0 && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-purple-800 mb-6 text-center">
              🎁 Special Snack Bundles
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {bundles.map((bundle: any) => (
                <BundleCard
                  key={bundle.id}
                  bundle={bundle}
                  onAddBundle={addBundleToCart}
                  isAdmin={isAdmin}
                  onEdit={handleEditBundle}
                  onDelete={handleDeleteBundle}
                />
              ))}
            </div>
          </div>
        )}

        {/* Products Grid Display */}
        {!loading && products.length > 0 && (
          <>
            <h2 className="text-3xl font-bold text-indigo-800 mb-6 text-center">
              Individual Items
            </h2>
            <div className="grid grid-cols-1 gap-6">
              {products.map((product: any) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  supplierName={product.supplierName} // <-- USE THE NAME FROM THE PRODUCT OBJECT
                  onAddToCart={addToCart}
                />
              ))}
            </div>
          </>
        )}

        <footer className="mt-16 text-center text-sm text-gray-400">
          Product data is retrieved from the supplier's backend system.
        </footer>
      </section>
    </div>
  );
};

export default App;