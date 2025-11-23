"""
Migration script to add original_price column to snack_bundles table.
Run this script to update existing databases.
"""
from database import get_database
import os

db_name = os.getenv("DB_NAME", "movie_munchers_dev")
database = get_database(db_name)
cursor = database.cursor()

try:
    # Check if column already exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'snack_bundles' 
        AND COLUMN_NAME = 'original_price'
    """, (db_name,))
    
    column_exists = cursor.fetchone()[0] > 0
    
    if not column_exists:
        # Add original_price column
        cursor.execute("""
            ALTER TABLE snack_bundles 
            ADD COLUMN original_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 
            AFTER description
        """)
        
        # Update existing records to set original_price = total_price / 0.80
        # This reverses the 20% discount to get the original price
        cursor.execute("""
            UPDATE snack_bundles 
            SET original_price = ROUND(total_price / 0.80, 2)
            WHERE original_price = 0.00
        """)
        
        database.commit()
        print("✅ Successfully added original_price column to snack_bundles table")
        print("✅ Updated existing bundles with calculated original prices")
    else:
        print("ℹ️  Column original_price already exists, skipping migration")
    
except Exception as e:
    print(f"❌ Error: {e}")
    database.rollback()
    
finally:
    cursor.close()
    database.close()
