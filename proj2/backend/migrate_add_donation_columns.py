"""
Migration script to add donation columns to the deliveries table.
Run this script to update existing databases with the new donation fields.
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_database(db_name):
    """Add donation columns to deliveries table if they don't exist."""
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
        
        # Check if columns exist and add them if they don't
        columns_to_add = [
            ("ngo_id", "INT DEFAULT NULL"),
            ("ngo_name", "VARCHAR(128) DEFAULT NULL"),
            ("donation_amount", "DECIMAL(12,2) NOT NULL DEFAULT 0.00"),
            ("donation_percentage", "DECIMAL(5,2) DEFAULT NULL")
        ]
        
        for column_name, column_def in columns_to_add:
            # Check if column exists
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = 'deliveries' 
                AND COLUMN_NAME = '{column_name}'
            """)
            
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE deliveries ADD COLUMN {column_name} {column_def}")
                connection.commit()
                print(f"  ✓ Added {column_name}")
            else:
                print(f"  - Column {column_name} already exists, skipping")
        
        cursor.close()
        connection.close()
        print(f"\nMigration completed for {db_name}")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error migrating {db_name}: {e}")
        return False

if __name__ == "__main__":
    print("Starting migration to add donation columns to deliveries table...\n")
    
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

