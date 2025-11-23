from database import get_database
import os

# Create development database and define cursor object
db_name = os.getenv("DB_NAME", "movie_munchers_dev")
database = get_database(db_name)
cursor_object = database.cursor()

from argon2.low_level import hash_secret, Type

# Helper function for deterministic password hashing 
def deterministic_hash(password):
    return hash_secret(
        secret=password.encode(),
        salt=b"fixedsalt",
        time_cost=3,
        memory_cost=2**16,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    ).decode()

ADMIN_HASH = deterministic_hash("password")

# HELPER FUNCTION FOR EXECUTING SQL QUERIES
def insert(query, values):
    cursor_object.executemany(query, values)
    database.commit()

# Function to populate existing database
def populate_db():
   # Theatres data
   insert("""INSERT INTO theatres (name, address, phone, is_open) VALUES (%s, %s, %s, %s)""",
         [('Theatre A', '123 A St', '555-0001', True),
            ('Theatre B', '123 B St', '555-0002', True)])

   # Auditoriums data
   insert("""INSERT INTO auditoriums (theatre_id, number, capacity) VALUES (%s, %s, %s)""",
         [(1, 1, 4),
            (2, 1, 4)])

   # Seats data
   insert("""INSERT INTO seats (aisle, number, auditorium_id) VALUES (%s, %s, %s)""",
         [('A', 1, 1),
            ('A', 1, 2),
            ('B', 1, 1),
            ('B', 1, 2),
            ('C', 1, 1),
            ('C', 1, 2),
            ('D', 1, 1),
            ('D', 1, 2)])

   # Users data
   insert("""INSERT INTO users (name, email, phone, birthday, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s)""",
         [('Alice', 'alice@ncsu.edu', '555-1000', '1990-01-01', ADMIN_HASH, 'staff'),
            ('Bob', 'bob@ncsu.edu', '555-2000', '1990-01-02', ADMIN_HASH, 'staff'),
            ('Charles', 'charles@ncsu.edu', '555-3000', '1990-01-03', ADMIN_HASH, 'staff'),
            ('Daisy', 'daisy@ncsu.edu', '555-4000', '1990-01-04', ADMIN_HASH, 'staff'),
            ('Evelyn', 'evelyn@ncsu.edu', '555-5000', '1990-01-04', ADMIN_HASH, 'customer'),
            ('Fergus', 'fergus@ncsu.edu', '555-6000', '1990-01-06', ADMIN_HASH, 'customer'),
            ('Grace', 'grace@ncsu.edu', '555-7000', '1990-01-07', ADMIN_HASH, 'customer' ),
            ('Hunter', 'hunter@ncsu.edu', '555-8000', '1990-01-08', ADMIN_HASH, 'customer'),
            ('Ingrid', 'ingrid@ncsu.edu', '555-9000', '1990-01-09', ADMIN_HASH, 'driver'),
            ('Jack', 'jack@ncsu.edu', '555-0100', '1990-01-10', ADMIN_HASH, 'driver'),
            ('Kyle', 'kyle@ncsu.edu', '555-0200', '1990-01-11', ADMIN_HASH, 'driver' ),
            ('Linda', 'linda@ncsu.edu', '555-0300', '1990-01-12', ADMIN_HASH, 'driver'),
            ('Molly', 'molly@ncsu.edu', '555-0400', '1990-01-13', ADMIN_HASH, 'supplier'),
            ('Nick', 'nick@ncsu.edu', '555-0500', '1990-01-14', ADMIN_HASH, 'supplier'),
            ('Oscar', 'oscar@ncsu.edu', '555-0600', '1990-01-15', ADMIN_HASH, 'supplier' ),
            ('Patricia', 'patricia@ncsu.edu', '555-0700', '1990-01-16', ADMIN_HASH, 'supplier')])
   # Staff data
   insert("""INSERT INTO staff (user_id, theatre_id, role, is_available) VALUES (%s, %s, %s, %s)""",
         [(1, 1, 'runner', True),
            (2, 2, 'admin', False),
            (3, 1, 'runner', True),
            (4, 2, 'admin', False)])
   # Movies data
   insert("""INSERT INTO movies (title, genre, length_mins, release_year, keywords, rating) VALUES (%s, %s, %s, %s, %s, %s)""", 
         [('Interstellar', 'Sci-Fi', 169, 2014, 'space, time, drama, intense, sweet', 4.8),
            ('The Dark Knight', 'Action', 152, 2008, 'action, intense, classic, hero, energy', 4.9)])

   # Movie showings data
   insert("""INSERT INTO movie_showings (movie_id, auditorium_id, start_time, in_progress) VALUES (%s, %s, %s, %s)""",
         [(1, 1, '2025-11-04 19:30:00', False),
            (2, 2, '2025-10-31 20:00:00', False)])

   # Customers data
   insert("""INSERT INTO customers (user_id, default_theatre_id) VALUES (%s, %s)""",
         [(5, 1),
            (6, 2),
            (7, 1),
            (8, 2)])

   # Customer showings data
   insert("""INSERT INTO customer_showings (customer_id, movie_showing_id, seat_id) VALUES (%s, %s, %s)""",
         [(5, 1, 1),
            (6, 2, 2)])

   # Payment methods data
   insert("""INSERT INTO payment_methods (customer_id, card_number, expiration_month, expiration_year, billing_address, balance, is_default) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
         [(5, '1234567812345678', 11, 2028, '123 Suburb Rd', 200, True),
            (6, '1111222233334444', 1, 2026, '456 Suburb Rd', 5, False)])

   # Drivers data
   insert("""INSERT INTO drivers (user_id, license_plate, vehicle_type, vehicle_color, duty_status, rating, total_deliveries) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
         [(9, 'ABCD123', 'car', 'red', 'available', 5.00, 10),
            (10, None, 'bike', 'blue', 'available', 5.00, 20),
            (11, None, 'scooter', 'green', 'unavailable', 4.25, 30),
            (12, 'WXYZ789', 'car', 'silver', 'on_delivery', 4.95, 15)])

   # Suppliers data
   insert("""INSERT INTO suppliers (user_id, company_name, company_address, contact_phone, is_open) VALUES (%s, %s, %s, %s, %s)""",
         [(13, 'Company A', '123 Company Way', '555-0010', True),
            (14, 'Company B', '456 Company Way', '555-0020', True),
            (15, 'Company C', '789 Company Way', '555-0030', True),
            (16, 'Company D', '223 Company Way', '555-0040', True)])

   # Products data - includes all food menu items for snack bundles
   insert("""INSERT INTO products (supplier_id, name, unit_price, inventory_quantity, size, keywords, category, discount, is_available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
         [(13, 'Pepsi', 3.00, 100, 'medium', 'sweet, refreshing, cold, quick, energy', 'beverages', 0.00, True),
            (13, 'Coca-Cola', 3.00, 100, 'medium', 'sweet, refreshing, cold, classic', 'beverages', 0.00, True),
            (13, 'Sprite', 3.00, 100, 'medium', 'refreshing, lemon-lime, cold', 'beverages', 0.00, True),
            (13, 'Juice Box', 2.50, 150, 'small', 'fruity, healthy, kids, refreshing', 'beverages', 0.00, True),
            (14, 'Chips', 4.00, 200, None, 'crispy, salty, bold, quick, shareable', 'snacks', 0.00, True),
            (14, 'Normal Popcorn', 5.00, 150, 'large', 'classic, buttery, warm, movie-night', 'snacks', 0.00, True),
            (14, 'Air Popped Popcorn', 5.50, 100, 'large', 'healthy, light, low-salt, guilt-free', 'snacks', 0.00, True),
            (14, 'Nachos', 6.00, 80, None, 'cheesy, crispy, savory, shareable', 'snacks', 0.00, True),
            (14, 'Nuts Pack', 4.50, 120, None, 'protein, healthy, salty, crunchy', 'snacks', 0.00, True),
            (15, 'Skittles', 3.50, 150, None, 'fun, colorful, tangy, sweet, fruity', 'candy', 0.00, True),
            (15, 'Chocolate Bars', 3.00, 200, None, 'sweet, creamy, indulgent, classic', 'candy', 0.00, True),
            (15, 'Dark Chocolate Bars', 3.50, 150, None, 'rich, sophisticated, less-sweet, antioxidants', 'candy', 0.00, True),
            (16, 'Hot Dog', 7.00, 100, None, 'savory, filling, classic, flavorful', 'food', 0.00, True),
            (16, 'Protein Bars', 4.00, 80, None, 'healthy, filling, energy, nutritious', 'food', 0.00, True),
            (16, 'Fruits', 3.50, 60, None, 'healthy, fresh, sweet, natural', 'food', 0.00, True)])

   # Deliveries data 
   insert("""INSERT INTO deliveries (driver_id, customer_showing_id, payment_method_id, staff_id, payment_status, total_price, is_rated) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
         [(9, 1, 1, 1, 'completed', 3.00, False),
            (10, 2, 2, 1, 'completed', 8.00, False)])
   
     
   # Cart items data
   insert("""INSERT INTO cart_items (customer_id, product_id, quantity) VALUES (%s, %s, %s)""",
          [(5, 1, 1),
            (6, 2, 2)])

   # Delivery items data
   insert("""INSERT INTO delivery_items (cart_item_id, delivery_id) VALUES (%s, %s)""",
         [(1, 1),
            (2, 2)])

   # Coupons seed data (unlocked by puzzles with difficulty levels)
   insert("""INSERT INTO coupons (code, difficulty, discount_percent, is_active) VALUES (%s, %s, %s, %s)""",
               [('PUZZLE10', 1, 10.00, True),
                ('MASTER50', 8, 50.00, True)])

   # Scan code_puzzle folders and insert into code_puzzles table
   base_dir = os.path.join(os.path.dirname(__file__), 'app', 'code_puzzle')
   puzzles_to_insert = []
   if os.path.exists(base_dir):
      for folder in ['easy', 'medium', 'hard']:
         folder_path = os.path.join(base_dir, folder)
         if not os.path.isdir(folder_path):
            continue
         for fname in os.listdir(folder_path):
            if not fname.endswith('.py'):
               continue
            name = os.path.splitext(fname)[0]
            py_path = os.path.join(folder_path, fname)
            txt_path = os.path.join(folder_path, name + '.txt')
            try:
               with open(py_path, 'r', encoding='utf-8') as f:
                  script = f.read()
               answer = ''
               if os.path.exists(txt_path):
                  with open(txt_path, 'r', encoding='utf-8') as f:
                     answer = f.read().strip()
               # map folder difficulty to integer (simple mapping)
               if folder == 'easy':
                  diff = 1
               elif folder == 'medium':
                  diff = 5
               else:
                  diff = 8
               puzzles_to_insert.append((folder, name, diff, script, answer, True))
            except Exception:
               continue

   if puzzles_to_insert:
      insert("""INSERT INTO code_puzzles (folder, name, difficulty, script, answer, is_active) VALUES (%s, %s, %s, %s, %s, %s)""",
           puzzles_to_insert)

      # After inserting puzzles, create a coupon per puzzle (avoid duplicates)
      try:
         cursor_object.execute("SELECT code FROM coupons")
         existing_codes = set(r[0] for r in cursor_object.fetchall())

         cursor_object.execute("SELECT id, folder, name, difficulty FROM code_puzzles")
         rows = cursor_object.fetchall()
         coupons_for_puzzles = []
         for r in rows:
            pid, folder, name, diff = r[0], r[1], r[2], r[3]
            code = f"PUZ{pid}_{folder}_{name}".upper()
            if code in existing_codes:
               continue
            # map difficulty to discount: easy->10, medium->25, hard->50
            if diff <= 3:
               discount = 10.00
            elif diff <= 6:
               discount = 25.00
            else:
               discount = 50.00
            coupons_for_puzzles.append((code, diff, discount, True))

         if coupons_for_puzzles:
            insert("""INSERT INTO coupons (code, difficulty, discount_percent, is_active) VALUES (%s, %s, %s, %s)""",
                   coupons_for_puzzles)
      except Exception:
         # non-fatal; continue
         pass

# Call function to populate database
populate_db()
