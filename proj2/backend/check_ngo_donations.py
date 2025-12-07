"""
Quick script to check NGO donations status
"""
from app.app import create_app, db
from app.models import Deliveries, NgoDonations

app = create_app('development')

with app.app_context():
    # Check recent deliveries with donations
    print("=== Recent Deliveries with Donations ===")
    deliveries = Deliveries.query.filter(Deliveries.ngo_id.isnot(None)).order_by(Deliveries.id.desc()).limit(5).all()
    for d in deliveries:
        print(f"Delivery ID: {d.id}, NGO ID: {d.ngo_id}, NGO Name: {d.ngo_name}, Donation Amount: ${d.donation_amount}")
    
    print("\n=== NGO Donations Table Status ===")
    # Check if table exists and has records
    try:
        ngo_records = NgoDonations.query.all()
        print(f"Found {len(ngo_records)} NGO records in table:")
        for ngo in ngo_records:
            print(f"  NGO {ngo.ngo_id}: ${ngo.total_amount_donated}")
    except Exception as e:
        print(f"ERROR: Could not query ngo_donations table: {e}")
        print("  -> Table might not exist. Run: python migrate_create_ngo_donations_table.py")

