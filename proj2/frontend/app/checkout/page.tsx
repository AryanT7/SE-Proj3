'use client';

import { useState, useEffect, useMemo } from 'react';
import Cookies from 'js-cookie';

// --- Configuration ---
// Note: Keeping API_BASE_URL pointing to the local backend for all non-ed operations (load/update cart, add funds).
const API_BASE_URL = 'http://localhost:5000/api';
const TAX_RATE = 0.08;
const DELIVERY_FEE = 5.0;

// --- TYPE DEFINITIONS ---
type Item = {
  item_id: string;
  quantity: string;
  product?: Product;
  bundle?: Bundle;
};

type Product = {
  id: string;
  name: string;
  unit_price: number;
  inventory_quantity: number;
  size: number;
  keywords: string;
  category: string;
  discount: number;
  is_available: boolean;
  supplier: IDtoSupplier;
};

type Bundle = {
  id: string;
  name: string;
  description: string;
  original_price: number;
  total_price: number;
  is_available: boolean;
  items: Array<{
    product_id: number;
    quantity: number;
  }>;
};

type Supplier = {
  company_name: string;
  company_address: string;
  contact_phone: string;
  is_open: string;
};

type IDtoSupplier = {
  id: string;
  supplier: Supplier;
};

type PaymentMethod = {
  id: string;
  card_number: number;
  expiration_month: number;
  expiration_year: number;
  balance: number;
  is_default: boolean;
  billing_address: string;
};

export default function CheckoutPage() {
  // --- STATE ---
  const [items, setItems] = useState<Item[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [suppliers, setSuppliers] = useState<IDtoSupplier[]>([]);

  const [selectedPaymentMethodId, setSelectedPaymentMethodId] = useState<
    string | null
  >(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [couponCode, setCouponCode] = useState<string>('');
  const [appliedCoupon, setAppliedCoupon] = useState<{code: string; discount_percent: number; new_total: number} | null>(null);
  const [availableCoupons, setAvailableCoupons] = useState<{id:number;code:string;difficulty:number;discount_percent:number}[]>([]);
  const [showPuzzleModal, setShowPuzzleModal] = useState(false);
  const [puzzleToken, setPuzzleToken] = useState<string | null>(null);
  const [puzzleQuestion, setPuzzleQuestion] = useState<string | null>(null);
  const [puzzleScript, setPuzzleScript] = useState<string | null>(null);
  const [puzzleAnswer, setPuzzleAnswer] = useState<string>('');
  const [skipPuzzle, setSkipPuzzle] = useState<boolean>(false);
  const [showManualCode, setShowManualCode] = useState<boolean>(false);
  const [ngos, setNgos] = useState<{id: number; name: string; cause: string; description: string}[]>([]);
  const [selectedNgoId, setSelectedNgoId] = useState<number | null>(null);
  const [donationType, setDonationType] = useState<'amount' | 'percentage'>('percentage');
  const [donationAmount, setDonationAmount] = useState<number>(0);
  const [donationPercentage, setDonationPercentage] = useState<number>(1.5);

  // --- API HANDLERS ---

  /**
   *  CHECKOUT FUNCTION: Simulates successful delivery and clears the cart state, then redirects.
   */
  const checkoutPay = async (selectedPaymentMethodId: string) => {
    if (!selectedPaymentMethodId) {
      setError('Please select a payment method.');
      return;
    }

    if (!hasSufficientFunds) {
      setError('Insufficient funds for this transaction.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const customerId = Cookies.get('user_id');
      const showRes = await fetch(
        `${API_BASE_URL}/customers/${customerId}/customer_showing`
      );
      let showingId = 0;
      if (showRes.ok) {
        const data = await showRes.json();
        showingId = data.id;

        console.log('Showing ID:', showingId);
      } else {
        console.error('Failed to fetch showings.');
      }
  console.debug('checkoutPay -> payload', { appliedCoupon, couponCode, puzzleToken, puzzleAnswer, skipPuzzle, selectedNgoId, donationType, donationAmount, donationPercentage });
  const response = await fetch(`${API_BASE_URL}/deliveries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_showing_id: showingId,
          payment_method_id: selectedPaymentMethodId,
          // coupon/puzzle fields
          coupon_code: appliedCoupon?.code || couponCode || null,
          puzzle_token: puzzleToken || null,
          puzzle_answer: puzzleAnswer || null,
          // If a coupon was already applied/verified via the coupon flow,
          // instruct the backend to skip puzzle verification when creating the delivery.
          skip_puzzle: appliedCoupon ? true : !!skipPuzzle,
          // donation fields
          ngo_id: selectedNgoId || null,
          donation_amount: selectedNgoId && donationType === 'amount' ? donationAmount : null,
          donation_percentage: selectedNgoId && donationType === 'percentage' ? donationPercentage : null,
        }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        throw new Error(errorResponse.message || 'Checkout failed.');
      }

      // Clear the cart if the order was successful
  setItems([]);
      alert('Order placed successfully!');
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyCouponCode = async () => {
    if (!couponCode) return setError('Enter a coupon code');
    setIsLoading(true);
    setError(null);
    try {
      // If user opted to skip puzzle, call apply directly with skip_puzzle
      if (skipPuzzle) {
        const res = await fetch(`${API_BASE_URL}/coupons/apply`, {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ code: couponCode, total, skip_puzzle: true }),
          credentials: 'include'
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || 'Invalid coupon');
        }
        const data = await res.json();
        setAppliedCoupon({ code: data.code, discount_percent: data.discount_percent, new_total: data.new_total });
        return;
      }

      // Otherwise request a puzzle for this coupon
      const puzzleRes = await fetch(`${API_BASE_URL}/coupons/${encodeURIComponent(couponCode)}/puzzle`, { credentials: 'include' });
      if (!puzzleRes.ok) {
        const err = await puzzleRes.json();
        throw new Error(err.error || 'Failed to fetch puzzle');
      }
  const puzzleData = await puzzleRes.json();
  // backend may return puzzle_script (python code) or legacy puzzle text
  setPuzzleScript(puzzleData.puzzle_script || null);
  setPuzzleQuestion(puzzleData.puzzle || null);
  setPuzzleToken(puzzleData.token);
  console.debug('applyCouponCode -> received puzzle token and question', { token: puzzleData.token, puzzle: puzzleData.puzzle, puzzle_script: puzzleData.puzzle_script });
      setShowPuzzleModal(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to apply coupon');
      setAppliedCoupon(null);
    } finally {
      setIsLoading(false);
    }
  };

  const submitPuzzleAnswer = async () => {
    if (!puzzleToken) return setError('Missing puzzle token');
    setIsLoading(true);
    setError(null);
    try {
      console.debug('submitPuzzleAnswer -> submitting', { couponCode, puzzleToken, puzzleAnswer });
      const res = await fetch(`${API_BASE_URL}/coupons/apply`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ code: couponCode, total, answer: puzzleAnswer, token: puzzleToken }),
        credentials: 'include'
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Failed to verify puzzle');
      }
      const data = await res.json();
      setAppliedCoupon({ code: data.code, discount_percent: data.discount_percent, new_total: data.new_total });
      setShowPuzzleModal(false);
      setPuzzleAnswer('');
      setPuzzleToken(null);
      setPuzzleQuestion(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to verify puzzle');
    } finally {
      setIsLoading(false);
    }
  };

  const removeAppliedCoupon = () => {
    setAppliedCoupon(null);
    setCouponCode('');
  };


  /**
   * item to remove
   * @param itemId of removing
   */
  const removeCartItem = async (itemId: string) => {
    try {
      await fetch(`${API_BASE_URL}/cart/${itemId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      await loadItems();
    } catch (error) {
      console.error('Error removing cart item:', error);
      setError('Failed to remove item.');
    }
  };

  /**
   * 
   * @param itemId of item to change
   * @param newQuantity new quantity
   * @returns 
   */
  const changeCartItemCount = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) {
      // IMPORTANT: Using window.confirm here as per current app implementation, but recommend custom modal.
      if (window.confirm('Are you sure you want to remove this item?')) {
        return removeCartItem(itemId);
      }
      return;
    }

    try {
      await fetch(`${API_BASE_URL}/cart/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity }),
        credentials: 'include',
      });
      await loadItems();
    } catch (error) {
      console.error('Error updating cart item:', error);
      setError('Failed to update quantity.');
    }
  };

  /**
   * 
   * @param paymentMethodId to add funds to
   * @param amount how much to add
   * @returns 
   */
  const addFundsToPaymentMethod = async (
    paymentMethodId: string,
    amount: number
  ) => {
    if (isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/payment-methods/${paymentMethodId}/add-funds`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: amount }),
          credentials: 'include',
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add funds.');
      }

      const data = await response.json();
      alert(
        `Successfully added $${amount.toFixed(
          2
        )}. New balance: $${data.new_balance.toFixed(2)}`
      );
      await loadPaymentMethods();
    } catch (e) {
      const errorMessage =
        e instanceof Error
          ? e.message
          : 'An unexpected error occurred while adding funds.';
      console.error('Add funds error:', e);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // --- LOAD IMPLEMENTATIONS (Unchanged - still use real API to load data) ---

  const loadSuppliers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/suppliers/all`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch suppliers.');
      const data = await response.json();
      setSuppliers(data.suppliers);
    } catch (error) {
      console.error('Error loading suppliers:', error);
      setError('Could not load supplier data.');
    }
  };

  /**
   * products -> state
   */
  const loadProducts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products/menu`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch products.');
      const data = await response.json();
      setProducts(data.products);
    } catch (error) {
      console.error('Error loading products:', error);
      setError('Could not load product data.');
    }
  };

  /**
   * bundles -> state
   */
  const loadBundles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/bundles`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch bundles.');
      const data = await response.json();
      setBundles(data.bundles || []);
    } catch (error) {
      console.error('Error loading bundles:', error);
      setError('Could not load bundle data.');
    }
  };

  /**
   * items -> state
   * @returns 
   */
  const loadItems = async () => {
    const customerId = Cookies.get('user_id') || '17';
    if (!customerId) return;

    const currentProducts = products;
    const currentBundles = bundles;

    if (currentProducts.length === 0 && currentBundles.length === 0) {
      console.warn(
        'Attempted to load cart items before products/bundles lists were populated.'
      );
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/customers/${customerId}/cart`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        if (response.status === 404) {
          setItems([]);
          return;
        }
        throw new Error('Failed to fetch cart items.');
      }
      const data = await response.json();

      const mappedItems: Item[] = data.items
        .map((cartItem: any) => {
          // Check if it's a product or bundle
          if (cartItem.product_id) {
            const cartProductIdString = String(cartItem.product_id);
            const productDetail = currentProducts.find(
              (p) => String(p.id) === cartProductIdString
            );

            if (!productDetail) {
              console.warn(
                `Product ID ${cartItem.product_id} not found in product list. Skipping item.`
              );
              return null;
            }

            return {
              item_id: String(cartItem.id),
              quantity: String(cartItem.quantity),
              product: productDetail,
            } as Item;
          } else if (cartItem.bundle_id) {
            const cartBundleIdString = String(cartItem.bundle_id);
            const bundleDetail = currentBundles.find(
              (b) => String(b.id) === cartBundleIdString
            );

            if (!bundleDetail) {
              console.warn(
                `Bundle ID ${cartItem.bundle_id} not found in bundle list. Skipping item.`
              );
              return null;
            }

            return {
              item_id: String(cartItem.id),
              quantity: String(cartItem.quantity),
              bundle: bundleDetail,
            } as Item;
          }
          
          return null;
        })
        .filter((item: Item | null): item is Item => item !== null);

      setItems(mappedItems);
    } catch (error) {
      console.error('Error loading cart items:', error);
      setError('Could not load shopping cart items.');
    }
  };

  /**
   * 
   * @returns payemnt methods -> state
   */
  const loadPaymentMethods = async () => {
    const customerId = Cookies.get('user_id') || '17';
    if (!customerId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/customers/${customerId}/payment-methods`,
        { credentials: 'include' }
      );
      if (!response.ok) throw new Error('Failed to fetch payment methods.');
      const data = await response.json();
      setPaymentMethods(data.payment_methods);

      const defaultMethod = data.payment_methods.find(
        (pm: PaymentMethod) => pm.is_default
      );
      if (defaultMethod) {
        setSelectedPaymentMethodId(defaultMethod.id);
      } else if (data.payment_methods.length > 0) {
        setSelectedPaymentMethodId(data.payment_methods[0].id);
      }
    } catch (error) {
      console.error('Error loading payment methods:', error);
      setError('Could not load payment methods.');
    }
  };

  // --- LOAD NGOs ---
  const loadNgos = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ngos`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch NGOs');
      const data = await response.json();
      setNgos(data.ngos || []);
    } catch (error) {
      console.error('Error loading NGOs:', error);
    }
  };

  // --- EFFECTS (Unchanged) ---
  useEffect(() => {
    setIsLoading(true);
    loadSuppliers();
    loadProducts();
    loadBundles();
    loadNgos();
    // load available coupons
    (async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/coupons`, { credentials: 'include' });
        if (!r.ok) return;
        const d = await r.json();
        setAvailableCoupons(d.coupons || []);
      } catch (e) {
        // ignore
      }
    })();
  }, []);

  // Clear any loaded puzzle data when the coupon code changes
  useEffect(() => {
    // When user switches coupon selection, remove any previously-loaded puzzle
    // so the modal won't display stale python code from another coupon.
    setPuzzleScript(null);
    setPuzzleQuestion(null);
    setPuzzleToken(null);
    setPuzzleAnswer('');
    setShowPuzzleModal(false);
  }, [couponCode]);

  useEffect(() => {
    if (products.length > 0 || bundles.length > 0) {
      loadItems();
      loadPaymentMethods();
      setIsLoading(false);
    }
  }, [products, bundles]);

  // --- COMPUTED VALUES (Unchanged) ---
  const total = useMemo(() => {
    return items.reduce((acc, item) => {
      const quantity = parseInt(item.quantity) || 0;
      if (item.product) {
        const price = item.product.unit_price || 0;
        return acc + price * quantity;
      } else if (item.bundle) {
        const price = item.bundle.total_price || 0;
        return acc + price * quantity;
      }
      return acc;
    }, 0);
  }, [items]);
  const effectiveTotal = appliedCoupon ? appliedCoupon.new_total : total;
  
  // Calculate donation amount based on type
  // This matches the backend calculation
  const calculatedDonationAmount = useMemo(() => {
    if (!selectedNgoId) return 0;
    if (donationType === 'amount') {
      return donationAmount;
    } else {
      // Percentage-based: calculate from original total (before coupon discount)
      return (total * donationPercentage) / 100;
    }
  }, [selectedNgoId, donationType, donationAmount, donationPercentage, total]);
  
  const finalTotal = effectiveTotal + calculatedDonationAmount;

  const selectedPaymentMethod = useMemo(() => {
    return paymentMethods.find((pm) => pm.id === selectedPaymentMethodId);
  }, [paymentMethods, selectedPaymentMethodId]);

  const hasSufficientFunds = useMemo(() => {
    if (!selectedPaymentMethod) return false;
    return selectedPaymentMethod.balance >= finalTotal;
  }, [selectedPaymentMethod, finalTotal]);
  
  // Reset donation inputs when NGO changes
  useEffect(() => {
    if (!selectedNgoId) {
      setDonationAmount(0);
      setDonationPercentage(1.5);
      setDonationType('percentage');
    }
  }, [selectedNgoId]);

  // --- HELPER FUNCTIONS (Unchanged) ---
  const getProductData = (item: Item) => {
    if (item.product) {
      const name = item.product.name || 'Unknown Product';
      const unitPrice = item.product.unit_price || 0;
      const quantity = parseInt(item.quantity) || 0;
      const itemId = item.item_id;
      return { itemId, name, unitPrice, quantity };
    } else if (item.bundle) {
      const name = item.bundle.name || 'Unknown Bundle';
      const unitPrice = item.bundle.total_price || 0;
      const quantity = parseInt(item.quantity) || 0;
      const itemId = item.item_id;
      return { itemId, name, unitPrice, quantity };
    }
    return { itemId: item.item_id, name: 'Unknown', unitPrice: 0, quantity: 0 };
  };

  const getPaymentData = (method: PaymentMethod) => {
    const cardNumberStr = String(method.card_number);
    const lastFour = cardNumberStr.slice(-4).padStart(4, '0');
    const balance = method.balance || 0;
    const expMonth = String(method.expiration_month).padStart(2, '0');
    const expYear = method.expiration_year;

    return { lastFour, balance, expMonth, expYear };
  };

  // --- JSX TEMPLATE (Unchanged layout) ---
  return (
    <section className="mx-auto mt-10 max-w-4xl px-4 font-inter">
      <div className="mb-6">
        <a
          href="/menu"
          className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-indigo-600 transition"
        >
          <svg
            className="h-4 w-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            ></path>
          </svg>
          Back to Menu
        </a>
      </div>

      <h1 className="text-4xl font-extrabold text-gray-900 mb-8">
        Shopping Cart
      </h1>

      {/* Error Message Display */}
      {error && (
        <div
          className="mb-6 rounded-xl bg-red-50 border border-red-300 p-4 shadow-sm"
          role="alert"
        >
          <p className="text-red-800 font-medium">Error: {error}</p>
          <p className="text-red-700 text-sm mt-1">
            **Check API:** Ensure your backend service is running and accessible
            for cart/payment data.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content: Cart Items & Payment */}
        <div className="lg:col-span-2 space-y-6">
          {/* Cart Management Section */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg">
            <h2 className="text-2xl font-semibold mb-6 pb-2 border-b">
              Your Items ({items.length})
            </h2>

            {/* Display loading state for a better UX */}
            {isLoading && items.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <svg
                  className="mx-auto h-8 w-8 animate-spin text-indigo-500"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <p className="mt-2">Loading cart and product data...</p>
              </div>
            ) : items.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed">
                <p className="text-gray-600 mb-4 font-medium">
                  Your cart is empty.
                </p>
                <a
                  href="/menu"
                  className="inline-flex items-center text-indigo-600 font-semibold hover:text-indigo-700 transition"
                >
                  Start Shopping
                  <svg
                    className="h-4 w-4 ml-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M14 5l7 7m0 0l-7 7m7-7H3"
                    ></path>
                  </svg>
                </a>
              </div>
            ) : (
              <div className="space-y-4">
                {items.map((item) => {
                  const data = getProductData(item);
                  return (
                    <div
                      key={item.item_id}
                      className="flex items-center justify-between p-4 border border-gray-100 bg-white rounded-xl shadow-sm hover:shadow-md transition duration-200"
                    >
                      <div className="flex-1 min-w-0 pr-4">
                        <p className="font-semibold text-gray-900 truncate">
                          {data.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          ${data.unitPrice.toFixed(2)} each
                        </p>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1 border border-gray-300 rounded-lg p-0.5">
                          <button
                            onClick={() =>
                              changeCartItemCount(
                                data.itemId,
                                data.quantity - 1
                              )
                            }
                            className="h-7 w-7 rounded-md text-sm text-gray-700 hover:bg-gray-100 transition disabled:opacity-50"
                            disabled={data.quantity <= 1 || isLoading}
                            title="Decrease quantity"
                          >
                            −
                          </button>
                          <span className="w-6 text-center text-sm font-medium">
                            {data.quantity}
                          </span>
                          <button
                            onClick={() =>
                              changeCartItemCount(
                                data.itemId,
                                data.quantity + 1
                              )
                            }
                            className="h-7 w-7 rounded-md text-sm text-gray-700 hover:bg-gray-100 transition"
                            disabled={isLoading}
                            title="Increase quantity"
                          >
                            +
                          </button>
                        </div>

                        <div className="text-right min-w-[5rem]">
                          <p className="font-bold text-gray-900">
                            ${(data.unitPrice * data.quantity).toFixed(2)}
                          </p>
                        </div>

                        <button
                          onClick={() => removeCartItem(data.itemId)}
                          className="text-red-500 hover:text-red-700 transition"
                          disabled={isLoading}
                          title="Remove item"
                        >
                          <svg
                            className="h-5 w-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Step 2: Payment Method Selection */}
          {items.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg">
              <h2 className="text-2xl font-semibold mb-6 pb-2 border-b">
                2. Select Payment
              </h2>

              {paymentMethods.length === 0 ? (
                <div className="text-center py-6 text-gray-600">
                  <p className="mb-3">
                    No payment methods found. Please add one to continue.
                  </p>
                  <button
                    onClick={() =>
                      setError(
                        'Feature: Adding new payment methods not yet implemented.'
                      )
                    }
                    className="rounded-lg bg-indigo-500 px-6 py-2 font-semibold text-white hover:bg-indigo-600 transition"
                  >
                    + Add New Card
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {paymentMethods.map((method) => {
                    const data = getPaymentData(method);
                    const isSelected = selectedPaymentMethodId === method.id;

                    return (
                      <div
                        key={method.id}
                        onClick={() => setSelectedPaymentMethodId(method.id)}
                        className={`cursor-pointer rounded-xl border-2 p-4 transition ${isSelected
                          ? 'border-indigo-500 ring-4 ring-indigo-100 shadow-md'
                          : 'border-gray-200 hover:border-gray-300'
                          }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <input
                              type="radio"
                              name="paymentMethod"
                              checked={isSelected}
                              onChange={() =>
                                setSelectedPaymentMethodId(method.id)
                              }
                              className="h-5 w-5 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                              aria-label={`Select payment method ending in ${data.lastFour}`}
                            />
                            <div>
                              <p className="font-semibold">
                                Card ending in {data.lastFour}
                              </p>
                          <p className="text-sm text-gray-500">
                            Expires {data.expMonth}/{data.expYear}
                          </p>
                            </div>
                          </div>
                          <p
                            className={`text-sm font-medium ${data.balance < finalTotal
                              ? 'text-red-500'
                              : 'text-green-600'
                              }`}
                          >
                            Balance: ${data.balance.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Insufficient funds warning */}
              {selectedPaymentMethod && !hasSufficientFunds && (
                <div className="mt-4 rounded-xl bg-red-100 border border-red-300 p-4">
                  <p className="text-red-800 text-sm font-medium">
                    <strong className="mr-1">Insufficient funds:</strong>{' '}
                    Selected card balance ($
                    {selectedPaymentMethod.balance.toFixed(2)}) is less than the
                    total order amount (${finalTotal.toFixed(2)}). Please select
                    another method or add funds.
                  </p>
                </div>
              )}

              {/* Add Funds Button for the selected method */}
              {selectedPaymentMethodId && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <button
                    onClick={() =>
                      addFundsToPaymentMethod(selectedPaymentMethodId, 100)
                    } // Hardcoded $100
                    disabled={isLoading}
                    className="w-full rounded-xl px-4 py-3 font-bold transition duration-200 shadow-md bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
                      ></path>
                    </svg>
                    {isLoading
                      ? 'Adding Funds...'
                      : 'Add $100 Funds to Selected Card'}
                  </button>
                  <p className="mt-2 text-xs text-gray-500 text-center">
                    Use this to test the checkout process when funds are low.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Order Total Summary */}
        {items.length > 0 && (
          <div className="lg:col-span-1">
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-lg sticky top-6">
              <h3 className="text-xl font-bold mb-4 border-b pb-2">
                Order Summary
              </h3>

              <div className="space-y-3">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Subtotal</span>
                  <span>${total.toFixed(2)}</span>
                </div>

                {appliedCoupon && (
                  <>
                    <div className="flex justify-between text-sm text-green-700">
                      <span>Coupon ({appliedCoupon.code}) — {appliedCoupon.discount_percent}%</span>
                      <span>- ${Math.max(0, (total - effectiveTotal)).toFixed(2)}</span>
                    </div>
                  </>
                )}

                {selectedNgoId && (
                  <div className="flex justify-between text-sm text-blue-700 pt-2">
                    <span>Donation {donationType === 'percentage' ? `(${donationPercentage}%)` : '(Fixed Amount)'}</span>
                    <span>+ ${calculatedDonationAmount.toFixed(2)}</span>
                  </div>
                )}

                <div className="flex justify-between font-extrabold text-2xl pt-4 border-t border-gray-200 mt-4">
                  <span>Total Due</span>
                  <span className="text-indigo-600">${finalTotal.toFixed(2)}</span>
                </div>
              </div>

              {/* Donation Section */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Make a Donation (Optional)
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Select an NGO and choose to donate a fixed amount or a percentage of your order
                </p>
                
                <select
                  value={selectedNgoId || ''}
                  onChange={(e) => setSelectedNgoId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full rounded-md border p-2 mb-3"
                >
                  <option value="">-- Select an NGO --</option>
                  {ngos.map((ngo) => (
                    <option key={ngo.id} value={ngo.id}>
                      {ngo.name} - {ngo.cause}
                    </option>
                  ))}
                </select>

                {selectedNgoId && (
                  <div className="mt-3 space-y-3">
                    {/* Donation Type Selection */}
                    <div className="flex gap-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="donationType"
                          value="percentage"
                          checked={donationType === 'percentage'}
                          onChange={(e) => setDonationType(e.target.value as 'percentage')}
                          className="mr-2"
                        />
                        <span className="text-sm">Percentage</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="donationType"
                          value="amount"
                          checked={donationType === 'amount'}
                          onChange={(e) => setDonationType(e.target.value as 'amount')}
                          className="mr-2"
                        />
                        <span className="text-sm">Fixed Amount</span>
                      </label>
                    </div>

                    {/* Percentage Input */}
                    {donationType === 'percentage' && (
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Donation Percentage: {donationPercentage}%
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="0.1"
                          value={donationPercentage}
                          onChange={(e) => setDonationPercentage(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>0%</span>
                          <span>100%</span>
                        </div>
                        <input
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          value={donationPercentage}
                          onChange={(e) => {
                            const val = parseFloat(e.target.value);
                            if (!isNaN(val) && val >= 0 && val <= 100) {
                              setDonationPercentage(val);
                            }
                          }}
                          className="w-full mt-2 rounded-md border p-2 text-sm"
                          placeholder="Enter percentage"
                        />
                      </div>
                    )}

                    {/* Fixed Amount Input */}
                    {donationType === 'amount' && (
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Donation Amount ($)
                        </label>
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          value={donationAmount}
                          onChange={(e) => {
                            const val = parseFloat(e.target.value);
                            if (!isNaN(val) && val >= 0) {
                              setDonationAmount(val);
                            } else if (e.target.value === '') {
                              setDonationAmount(0);
                            }
                          }}
                          className="w-full rounded-md border p-2 text-sm"
                          placeholder="Enter amount in dollars"
                        />
                      </div>
                    )}

                    {/* Donation Summary */}
                    {selectedNgoId && calculatedDonationAmount > 0 && (
                      <div className="mt-2 p-2 bg-blue-50 rounded-md">
                        <p className="text-xs text-blue-700">
                          <strong>Donating ${calculatedDonationAmount.toFixed(2)}</strong> to {ngos.find(n => n.id === selectedNgoId)?.name}
                        </p>
                        {donationType === 'percentage' && (
                          <p className="text-xs text-blue-600 mt-1">
                            ({donationPercentage}% of ${total.toFixed(2)})
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Coupon input */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700">Coupon Code</label>
                {/* Manual input on top */}
                <div className="mt-2">
                  <input
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    className="w-full rounded-md border p-2"
                    placeholder="Enter coupon code or select below"
                  />
                </div>

                {/* Dropdown below manual input */}
                <div className="mt-2">
                  <select className="w-full rounded-md border p-2" value={couponCode} onChange={(e)=>setCouponCode(e.target.value)}>
                    <option value="">-- Select coupon --</option>
                    {availableCoupons.map(c => (
                      <option key={c.id} value={c.code}>{c.code} — {c.discount_percent}% (difficulty {c.difficulty})</option>
                    ))}
                  </select>
                </div>

                {/* Apply button below dropdown */}
                <div className="mt-3">
                  <button
                    onClick={applyCouponCode}
                    disabled={isLoading}
                    className="w-full rounded-md bg-indigo-600 text-white px-4 py-2"
                  >
                    {isLoading ? 'Applying...' : 'Apply Coupon'}
                  </button>
                </div>
                
                {appliedCoupon && (
                  <div className="mt-2">
                    <p className="text-sm text-green-700">Applied {appliedCoupon.code}: {appliedCoupon.discount_percent}% off</p>
                    <button onClick={removeAppliedCoupon} className="text-xs text-red-600 underline mt-1">Remove coupon</button>
                  </div>
                )}
              </div>

              {/* Place Order Button - Now uses the  checkout */}
                <div className="mt-8">
                {/* Puzzle Modal */}
                {showPuzzleModal && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center">
                    <div className="absolute inset-0 bg-black opacity-40" onClick={() => { setShowPuzzleModal(false); setPuzzleToken(null); setPuzzleQuestion(null); setPuzzleAnswer(''); }} />
                    <div className="relative z-10 w-full max-w-md bg-white rounded-lg p-6 shadow-lg">
                      <h4 className="text-lg font-semibold mb-3">Verify Coupon</h4>
                      {puzzleScript ? (
                        <pre className="bg-gray-100 rounded-md p-3 text-sm overflow-auto mb-4"><code>{puzzleScript}</code></pre>
                      ) : (
                        <p className="text-sm text-gray-700 mb-4">{puzzleQuestion}</p>
                      )}
                      <input
                        type="text"
                        value={puzzleAnswer}
                        onChange={(e) => setPuzzleAnswer(e.target.value)}
                        className="w-full rounded-md border p-2 mb-4"
                        placeholder="Enter puzzle answer"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => { setShowPuzzleModal(false); setPuzzleToken(null); setPuzzleQuestion(null); setPuzzleAnswer(''); }}
                          className="rounded-md px-4 py-2 border"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={submitPuzzleAnswer}
                          disabled={isLoading}
                          className="rounded-md bg-indigo-600 text-white px-4 py-2"
                        >
                          {isLoading ? 'Verifying...' : 'Submit'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
                <button
                  onClick={() =>
                    selectedPaymentMethodId &&
                    checkoutPay(selectedPaymentMethodId)
                  }
                  disabled={
                    !selectedPaymentMethodId || !hasSufficientFunds || isLoading
                  }
                  className={`w-full rounded-xl px-4 py-3 font-bold transition duration-200 shadow-md ${!selectedPaymentMethodId || !hasSufficientFunds || isLoading
                    ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                    : 'bg-red-600 text-white hover:bg-red-700 hover:shadow-lg' // Changed color to red to indicate
                    }`}
                >
                  {isLoading
                    ? ' Processing Order...'
                    : ` Pay $${finalTotal.toFixed(2)} Now`}
                </button>

                {/* Status messages for disabled state */}
                {!selectedPaymentMethodId && (
                  <p className="mt-3 text-sm text-center text-red-500 font-medium">
                    Please select a payment method.
                  </p>
                )}
                {selectedPaymentMethodId && !hasSufficientFunds && (
                  <p className="mt-3 text-sm text-center text-red-500 font-medium">
                    Insufficient funds on selected card. Need ${finalTotal.toFixed(2)} but have ${selectedPaymentMethod?.balance.toFixed(2) || '0.00'}.
                  </p>
                )}
              </div>
              <p className="mt-3 text-xs text-center text-red-600 font-semibold">
                This button uses delivery logic.
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
