"""
Migration script to create ngo_donations table and seed it with initial data.
Run this script to create the table and initialize all NGOs with 0 donations.
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Hardcoded list of NGOs (must match customer_service.py)
NGOS = [
    {"id": 1, "name": "Animal Care Foundation", "cause": "Animal Care", "description": "Supporting animal welfare and rescue operations"},
    {"id": 2, "name": "Elderly Protection Network", "cause": "Abused Elderly", "description": "Protecting and supporting abused elderly individuals"},
    {"id": 3, "name": "Hope for Children", "cause": "Orphan Children", "description": "Providing care and education for orphaned children"},
    {"id": 4, "name": "Medical Support Alliance", "cause": "Cancer/HIV Patients", "description": "Supporting cancer and HIV patients with medical care"},
    {"id": 5, "name": "Disease Relief Fund", "cause": "Disease People", "description": "Helping people affected by various diseases"},
    {"id": 6, "name": "Homeless Shelter Initiative", "cause": "Homeless", "description": "Providing shelter and support for homeless individuals"}
]

def migrate_database(db_name):
    """Create ngo_donations table and seed it with initial data."""
    my_host = os.getenv('DB_HOST', 'localhost')
    my_user = os.getenv('DB_USER', 'root')
    my_password = os.getenv('DB_PASSWORD', '')
    
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            database=db_name
        )
        cursor = connection.cursor()
        
        print(f"Connected to database: {db_name}")
        
        # Check if table exists
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{db_name}' 
            AND TABLE_NAME = 'ngo_donations'
        """)
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("Creating ngo_donations table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ngo_donations (
                    ngo_id INT PRIMARY KEY NOT NULL,
                    total_amount_donated DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT check_ngo_donation_amount CHECK (total_amount_donated >= 0.00)
                )
            """)
            connection.commit()
            print("  ✓ Created ngo_donations table")
        else:
            print("  - Table ngo_donations already exists, skipping creation")
        
        # Seed the table with all NGOs initialized to 0
        print("\nSeeding ngo_donations table with initial data...")
        for ngo in NGOS:
            cursor.execute("""
                INSERT INTO ngo_donations (ngo_id, total_amount_donated)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE ngo_id = ngo_id
            """, (ngo["id"], 0.00))
            connection.commit()
            print(f"  ✓ Seeded NGO {ngo['id']}: {ngo['name']}")
        
        cursor.close()
        connection.close()
        print(f"\nMigration completed for {db_name}")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error migrating {db_name}: {e}")
        return False

if __name__ == "__main__":
    print("Starting migration to create ngo_donations table...\n")
    
    # Migrate all three databases
    databases = [
        os.getenv("DB_NAME", "movie_munchers_dev"),
        "movie_munchers_test",
        "movie_munchers_prod"
    ]
    
    for db_name in databases:
        print(f"\n{'='*50}")
        print(f"Migrating: {db_name}")
        print(f"{'='*50}")
        migrate_database(db_name)
    
    print("\n" + "="*50)
    print("All migrations completed!")
    print("="*50)

