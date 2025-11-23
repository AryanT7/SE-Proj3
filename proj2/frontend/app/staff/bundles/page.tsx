'use client';
import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';

interface Product {
  id: number;
  name: string;
  unit_price: number;
  category: string;
}

interface BundleItem {
  product_id: number;
  product_name?: string;
  quantity: number;
  unit_price?: number;
}

interface Bundle {
  id: number;
  name: string;
  description: string;
  total_price: number;
  is_available: boolean;
  items: BundleItem[];
}

export default function BundleManagement() {
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingBundle, setEditingBundle] = useState<Bundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    total_price: 0,
    product_items: [] as BundleItem[],
  });

  const userId = Number(Cookies.get('user_id') || 0);

  useEffect(() => {
    fetchBundles();
    fetchProducts();
  }, []);

  const fetchBundles = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/bundles?include_unavailable=true', {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch bundles');
      const data = await response.json();
      setBundles(data.bundles || []);
    } catch (err) {
      setError('Failed to load bundles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/customers/products', {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch products');
      const data = await response.json();
      setProducts(data.products || []);
    } catch (err) {
      console.error('Failed to load products:', err);
    }
  };

  const handleAddProduct = () => {
    setFormData({
      ...formData,
      product_items: [...formData.product_items, { product_id: products[0]?.id || 0, quantity: 1 }],
    });
  };

  const handleRemoveProduct = (index: number) => {
    const newItems = formData.product_items.filter((_, i) => i !== index);
    setFormData({ ...formData, product_items: newItems });
  };

  const handleProductChange = (index: number, field: 'product_id' | 'quantity', value: number) => {
    const newItems = [...formData.product_items];
    newItems[index][field] = value;
    setFormData({ ...formData, product_items: newItems });
  };

  const calculateTotalPrice = () => {
    return formData.product_items.reduce((total, item) => {
      const product = products.find(p => p.id === item.product_id);
      return total + (product ? product.unit_price * item.quantity : 0);
    }, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const calculatedTotal = calculateTotalPrice();
      const bundleData = {
        ...formData,
        total_price: calculatedTotal,
      };

      const url = editingBundle
        ? `http://localhost:5000/api/bundles/${editingBundle.id}`
        : 'http://localhost:5000/api/bundles';
      
      const method = editingBundle ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(bundleData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to save bundle');
      }

      alert(editingBundle ? 'Bundle updated successfully!' : 'Bundle created successfully!');
      resetForm();
      fetchBundles();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleEdit = (bundle: Bundle) => {
    setEditingBundle(bundle);
    setFormData({
      name: bundle.name,
      description: bundle.description,
      total_price: bundle.total_price,
      product_items: bundle.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (bundleId: number) => {
    if (!confirm('Are you sure you want to delete this bundle?')) return;

    try {
      const response = await fetch(`http://localhost:5000/api/bundles/${bundleId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to delete bundle');

      alert('Bundle deleted successfully!');
      fetchBundles();
    } catch (err) {
      alert('Failed to delete bundle: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleToggleAvailability = async (bundleId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/bundles/${bundleId}/toggle`, {
        method: 'PATCH',
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to toggle availability');

      fetchBundles();
    } catch (err) {
      alert('Failed to toggle availability: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      total_price: 0,
      product_items: [],
    });
    setShowCreateForm(false);
    setEditingBundle(null);
  };

  if (loading) return <div className="p-4">Loading bundles...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Snack Bundle Management</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
        >
          {showCreateForm ? 'Cancel' : 'Create New Bundle'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {showCreateForm && (
        <div className="mb-8 p-6 border border-gray-300 rounded-lg bg-gray-50">
          <h3 className="text-xl font-semibold mb-4">
            {editingBundle ? 'Edit Bundle' : 'Create New Bundle'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Bundle Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                placeholder="e.g., Movie Night Special"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                rows={3}
                placeholder="Describe what's included in this bundle"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium">Products in Bundle</label>
                <button
                  type="button"
                  onClick={handleAddProduct}
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                >
                  + Add Product
                </button>
              </div>

              {formData.product_items.map((item, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <select
                    value={item.product_id}
                    onChange={(e) => handleProductChange(index, 'product_id', parseInt(e.target.value))}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.name} - ${product.unit_price.toFixed(2)} ({product.category})
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => handleProductChange(index, 'quantity', parseInt(e.target.value))}
                    className="w-20 px-4 py-2 border border-gray-300 rounded-lg"
                    placeholder="Qty"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveProduct(index)}
                    className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm">
                <strong>Bundle Price:</strong> ${calculateTotalPrice().toFixed(2)}
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
              >
                {editingBundle ? 'Update Bundle' : 'Create Bundle'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Existing Bundles</h3>
        {bundles.length === 0 ? (
          <p className="text-gray-500">No bundles created yet.</p>
        ) : (
          bundles.map((bundle) => (
            <div
              key={bundle.id}
              className={`p-4 border rounded-lg ${
                bundle.is_available ? 'border-gray-300 bg-white' : 'border-gray-200 bg-gray-100'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="text-lg font-semibold">
                    {bundle.name}
                    {!bundle.is_available && (
                      <span className="ml-2 text-sm text-red-600">(Unavailable)</span>
                    )}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">{bundle.description}</p>
                  <div className="mt-2 space-y-1">
                    <p className="text-sm">
                      <strong>Items:</strong>{' '}
                      {bundle.items.map((item) => `${item.quantity}x ${item.product_name}`).join(', ')}
                    </p>
                    <p className="text-sm font-semibold text-green-600">
                      <strong>Total Price:</strong> ${bundle.total_price.toFixed(2)}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col gap-2 ml-4">
                  <button
                    onClick={() => handleEdit(bundle)}
                    className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleToggleAvailability(bundle.id)}
                    className={`px-3 py-1 rounded text-sm ${
                      bundle.is_available
                        ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {bundle.is_available ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => handleDelete(bundle.id)}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
