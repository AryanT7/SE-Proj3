"use client";
import { useState, useEffect } from "react";
import Cookies from "js-cookie";

/**
 * delivery object
 */
interface Delivery {
    id: number;
    customer_showing_id: number;
    payment_method_id: number;
    driver_id: number | null;
    staff_id: number | null;
    total_price: number;
    payment_status: string;
    delivery_status:
    | "pending"
    | "accepted"
    | "in_progress"
    | "ready_for_pickup"
    | "in_transit"
    | "delivered"
    | "fulfilled"
    | "completed"
    | "cancelled";
    is_rated: boolean;
}

/**
 * extra details if necessary
 */
interface DeliveryDetails {
    id: number;
    driver_id: number | null;
    total_price: number;
    delivery_time: string | null;
    delivery_status: string;
    items: { name: string; quantity: number }[];
    theatre_name: string;
    theatre_address: string;
    movie_title: string;
    driver_name: string;
    donation?: {
        ngo_id: number | null;
        ngo_name: string | null;
        donation_amount: number;
        donation_percentage: number | null;
    } | null;
}

export default function CustomerDashboardPage() {
    const [customerName, setCustomerName] = useState<string | null>(null);
    const [deliveries, setDeliveries] = useState<Delivery[]>([]);
    const [loading, setLoading] = useState(true);
    const [ratings, setRatings] = useState<Record<number, number>>({});
    const [submitting, setSubmitting] = useState<number | null>(null);
    const [canceling, setCanceling] = useState<number | null>(null);
    const [details, setDetails] = useState<DeliveryDetails | null>(null);
    const [detailsLoading, setDetailsLoading] = useState(false);
    const [showings, setShowings] = useState<any[]>([]);
    const [driverNames, setDriverNames] = useState<{ [key: number]: string }>(
        {}
    );

    const customerId = Number(Cookies.get("user_id") || 0);

    /**
     * set status text
     * @param text what to set status
     * @param type color
     * @returns html element
     */
    const statusBadge = (
        text: string,
        type: "green" | "red" | "yellow" | "gray" | "blue"
    ) => {
        const colors: Record<string, string> = {
            green: "bg-green-100 text-green-700 border border-green-300",
            red: "bg-red-100 text-red-700 border border-red-300",
            yellow: "bg-yellow-100 text-yellow-700 border border-yellow-300",
            gray: "bg-gray-100 text-gray-700 border border-gray-300",
            blue: "bg-blue-100 text-blue-700 border border-blue-300",
        };
        return (
            <span
                className={`px-2 py-1 rounded-full font-medium ${colors[type]}`}
            >
                {text}
            </span>
        );
    };

    /**
     * onload and on customer id change: get information
     */
    useEffect(() => {
        fetch(`http://localhost:5000/api/users/${customerId}`)
            .then((res) => res.json())
            .then((data) => {
                if (data) setCustomerName(data.name);
            })
            .catch((err) => console.error("Error fetching showings:", err));
    }, [customerId]);

    /**
     * get your current deliveries
     */
    const fetchDeliveries = async () => {
        try {
            const res = await fetch(
                `http://localhost:5000/api/customers/${customerId}/deliveries`
            );
            const data = await res.json();
            setDeliveries(data.deliveries || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    /** get deliveries on load and relog */
    useEffect(() => {
        if (customerId) fetchDeliveries();
    }, [customerId]);

    /** get your current showings on load and relog */
    useEffect(() => {
        fetch(`http://localhost:5000/api/customers/${customerId}/showings`)
            .then((res) => res.json())
            .then((data) => {
                if (data.showings) setShowings(data.showings);
            })
            .catch((err) => console.error("Error fetching showings:", err));
    }, [customerId]);

    // --- Submit driver rating ---
    const submitRating = async (deliveryId: number) => {
        const rating = ratings[deliveryId];
        if (!rating) return alert("Please select a rating first.");
        try {
            setSubmitting(deliveryId);
            const res = await fetch(
                `http://localhost:5000/api/deliveries/${deliveryId}/rate`,
                {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ rating }),
                }
            );
            const data = await res.json();
            if (res.ok) {
                alert(`Driver rated ${rating}/5 successfully!`);
                setRatings((prev) => ({ ...prev, [deliveryId]: 0 }));
                fetchDeliveries(); // refresh data
            } else {
                alert(data.error || "Failed to submit rating.");
            }
        } catch (err) {
            console.error(err);
        } finally {
            setSubmitting(null);
        }
    };

    useEffect(() => {
        if (deliveries.length > 0) {
            const uniqueDriverIds = Array.from(
                new Set(
                    deliveries
                        .map((d) => d.driver_id)
                        .filter((id) => id != null)
                )
            );

            uniqueDriverIds.forEach((id) => {
                fetch(`http://localhost:5000/api/users/${id}`)
                    .then((res) => res.json())
                    .then((data) => {
                        setDriverNames((prev) => ({
                            ...prev,
                            [id]: data.name,
                        }));
                    })
                    .catch(() => {
                        setDriverNames((prev) => ({
                            ...prev,
                            [id]: `Driver #${id}`,
                        }));
                    });
            });
        }
    }, [deliveries]);

    // --- Cancel delivery ---
    const cancelDelivery = async (deliveryId: number) => {
        const confirmCancel = confirm(
            "Are you sure you want to cancel this delivery?"
        );
        if (!confirmCancel) return;

        try {
            setCanceling(deliveryId);
            const res = await fetch(
                `http://localhost:5000/api/deliveries/${deliveryId}/cancel`,
                { method: "POST" }
            );
            const data = await res.json();
            if (res.ok) {
                alert(`Delivery #${deliveryId} has been cancelled.`);
                fetchDeliveries();
            } else {
                alert(data.error || "Failed to cancel delivery.");
            }
        } catch (err) {
            console.error(err);
        } finally {
            setCanceling(null);
        }
    };

    // --- Fetch and show delivery details ---
    const viewDetails = async (deliveryId: number) => {
        try {
            setDetailsLoading(true);
            const res = await fetch(
                `http://localhost:5000/api/deliveries/${deliveryId}/details`
            );
            const data = await res.json();
            if (res.ok && data) {
                const userRes = await fetch(
                    `http://localhost:5000/api/users/${data.driver_id}`
                );
                const userData = await userRes.json();

                setDetails({ ...data, driver_name: userData.name });
            } else {
                alert(data.error || "Failed to load delivery details.");
            }
        } catch (err) {
            console.error(err);
        } finally {
            setDetailsLoading(false);
        }
    };

    /**
     * set details when closing
     * @returns 
     */
    const closeDetails = () => setDetails(null);

    /**
     * if you're loading put this text
     */
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen text-gray-500">
                Loading customer dashboard...
            </div>
        );
    }

    return (
        <section className="mx-auto max-w-6xl px-4 py-8 space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-4">Customer Dashboard</h1>
                <h2 className="text-xl font-semibold mb-2">Welcome, {customerName}</h2>
            </div>

            {/* Delivery History */}
            <div className="border rounded-lg shadow-lg p-6 bg-white">
                <h2 className="text-xl font-bold mt-8 mb-4">Delivery History</h2>

                {deliveries.length ? (
                    <div className="overflow-x-auto">
                        <table className="w-full table-auto border-collapse border border-gray-200 text-left">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="border px-4 py-2 text-gray-700">
                                        ID
                                    </th>
                                    <th className="border px-4 py-2 text-gray-700">
                                        Driver
                                    </th>
                                    <th className="border px-4 py-2 text-gray-700">
                                        Status
                                    </th>
                                    <th className="border px-4 py-2 text-gray-700">
                                        Total
                                    </th>
                                    <th className="border px-4 py-2 text-gray-700">
                                        Payment
                                    </th>
                                    <th className="border px-4 py-2 text-gray-700">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {deliveries.map((d, index) => {
                                    const isCompleted = [
                                        "fulfilled",
                                        "completed",
                                    ].includes(d.delivery_status);
                                    const isCancelled =
                                        d.delivery_status ===
                                        "cancelled";

                                    return (
                                        <tr
                                            key={d.id}
                                            className={
                                                index % 2 === 0
                                                    ? "bg-white"
                                                    : "bg-gray-50"
                                            }
                                        >
                                            <td className="border px-4 py-2 font-medium text-gray-700">
                                                {d.id}
                                            </td>
                                            <td className="border px-4 py-2 text-gray-700">
                                                {d.driver_id
                                                    ? driverNames[
                                                    d.driver_id
                                                    ] || "Loading..."
                                                    : "Unassigned"}
                                            </td>
                                            <td className="border px-4 py-2">
                                                {statusBadge(
                                                    d.delivery_status,
                                                    isCompleted
                                                        ? "green"
                                                        : isCancelled
                                                            ? "red"
                                                            : "yellow"
                                                )}
                                            </td>
                                            <td className="border px-4 py-2 text-gray-700">
                                                $
                                                {d.total_price.toFixed(
                                                    2
                                                )}
                                            </td>
                                            <td className="border px-4 py-2 text-gray-700">
                                                {d.payment_status}
                                            </td>
                                            <td className="border px-4 py-2 text-gray-700 space-y-2">
                                                {/* View Details */}
                                                <button
                                                    onClick={() =>
                                                        viewDetails(
                                                            d.id
                                                        )
                                                    }
                                                    className="w-full px-3 py-1 rounded font-medium text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 transition"
                                                >
                                                    {detailsLoading &&
                                                        details?.id === d.id
                                                        ? "Loading..."
                                                        : "View Details"}
                                                </button>

                                                {/* Cancel */}
                                                {!isCompleted &&
                                                    !isCancelled && (
                                                        <button
                                                            onClick={() =>
                                                                cancelDelivery(
                                                                    d.id
                                                                )
                                                            }
                                                            disabled={
                                                                canceling ===
                                                                d.id
                                                            }
                                                            className={`w-full px-3 py-1 rounded font-medium text-sm ${canceling ===
                                                                    d.id
                                                                    ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                                                                    : "bg-red-100 text-red-700 hover:bg-red-200 transition"
                                                                }`}
                                                        >
                                                            {canceling ===
                                                                d.id
                                                                ? "Cancelling..."
                                                                : "Cancel"}
                                                        </button>
                                                    )}

                                                {/* Rate */}
                                                {isCompleted && !d.is_rated && (
                                                    <div className="flex items-center justify-center space-x-2">
                                                        <select
                                                            value={
                                                                ratings[
                                                                d.id
                                                                ] || ""
                                                            }
                                                            onChange={(
                                                                e
                                                            ) =>
                                                                setRatings(
                                                                    (
                                                                        prev
                                                                    ) => ({
                                                                        ...prev,
                                                                        [d.id]:
                                                                            Number(
                                                                                e
                                                                                    .target
                                                                                    .value
                                                                            ),
                                                                    })
                                                                )
                                                            }
                                                            className="border border-gray-300 rounded-lg px-2 py-1"
                                                        >
                                                            <option value="">
                                                                Rate
                                                            </option>
                                                            {[
                                                                1, 2, 3,
                                                                4, 5,
                                                            ].map(
                                                                (r) => (
                                                                    <option
                                                                        key={
                                                                            r
                                                                        }
                                                                        value={
                                                                            r
                                                                        }
                                                                    >
                                                                        {
                                                                            r
                                                                        }
                                                                    </option>
                                                                )
                                                            )}
                                                        </select>
                                                        <button
                                                            onClick={() =>
                                                                submitRating(
                                                                    d.id
                                                                )
                                                            }
                                                            disabled={
                                                                submitting ===
                                                                d.id
                                                            }
                                                            className={`px-3 py-1 rounded font-medium ${submitting ===
                                                                    d.id
                                                                    ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                                                                    : "bg-blue-100 text-blue-700 hover:bg-blue-200"
                                                                }`}
                                                        >
                                                            {submitting ===
                                                                d.id
                                                                ? "Submitting..."
                                                                : "Submit"}
                                                        </button>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-gray-500 italic">
                        You have no deliveries yet.
                    </p>
                )}
            </div>

            {/* Showings Table */}
            <div className="border rounded-lg shadow-lg p-6 bg-white">
                <h2 className="text-xl font-bold mt-8 mb-4">Your Showings</h2>
                <table className="min-w-full border-collapse border border-gray-200">
                    <thead>
                        <tr>
                            <th className="border px-4 py-2">Movie Title</th>
                            <th className="border px-4 py-2">Seat</th>
                            <th className="border px-4 py-2">Start Time</th>
                            <th className="border px-4 py-2">Auditorium</th>
                            <th className="border px-4 py-2">Theatre</th>
                        </tr>
                    </thead>
                    <tbody>
                        {showings.map((s) => (
                            <tr key={s.id}>
                                <td className="border px-4 py-2 text-center">
                                    {s.movie_title}
                                </td>
                                <td className="border px-4 py-2 text-center">
                                    {s.seat}
                                </td>
                                <td className="border px-4 py-2 text-center">
                                    {new Date(s.start_time).toLocaleString()}
                                </td>
                                <td className="border px-4 py-2 text-center">
                                    {s.auditorium}
                                </td>
                                <td className="border px-4 py-2 text-center">
                                    {s.theatre_name}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* --- Details Modal --- */}
            {details && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
                    <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6 relative">
                        <button
                            onClick={closeDetails}
                            className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 text-2xl"
                        >
                            ×
                        </button>
                        <h2 className="text-xl font-bold mb-3">
                            Delivery #{details.id} Details
                        </h2>
                        <p>
                            <strong>Movie:</strong> {details.movie_title}
                        </p>
                        <p>
                            <strong>Theatre:</strong> {details.theatre_name}
                        </p>
                        <p className="mb-2 text-sm text-gray-500">
                            {details.theatre_address}
                        </p>
                        <p>
                            <strong>Status:</strong> {details.delivery_status}
                        </p>
                        <p>
                            <strong>Driver:</strong>{" "}
                            {details.driver_id
                                ? `${details.driver_name}`
                                : "Unassigned"}
                        </p>
                        <p>
                            <strong>Total Price:</strong> $
                            {details.total_price.toFixed(2)}
                        </p>
                        {details.donation && (
                            <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                                <p className="font-semibold text-blue-800 mb-1">
                                    Donation Made
                                </p>
                                <p className="text-sm text-blue-700">
                                    <strong>NGO:</strong> {details.donation.ngo_name}
                                </p>
                                <p className="text-sm text-blue-700">
                                    <strong>Amount:</strong> ${details.donation.donation_amount.toFixed(2)}
                                </p>
                                {details.donation.donation_percentage && (
                                    <p className="text-sm text-blue-700">
                                        <strong>Percentage:</strong> {details.donation.donation_percentage}%
                                    </p>
                                )}
                            </div>
                        )}
                        {details.delivery_time && (
                            <p>
                                <strong>Delivery Time:</strong>{" "}
                                {new Date(
                                    details.delivery_time
                                ).toLocaleString()}
                            </p>
                        )}
                        <h3 className="mt-4 font-semibold">Items:</h3>
                        <ul className="list-disc ml-6 text-gray-700">
                            {details.items.map((item, idx) => (
                                <li key={idx}>
                                    {item.name} × {item.quantity}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </section>
    );
}
