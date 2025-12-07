import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

# Schema table names
tables = ['theatres', 'auditoriums', 'seats', 'users', 'staff', 'movies', 'movie_showings',
          'customers', 'customer_showings', 'payment_methods', 'drivers', 'suppliers',
          'products', 'deliveries', 'cart_items', 'delivery_items', 'coupons', 'snack_bundles', 'bundle_items']


# Drop a single table with foreign key checks temporarily disabled 
def drop_table(database, table):
    cursor = database.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute(f'DROP TABLE IF EXISTS {table}')
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    database.commit()
    cursor.close()


# Drop all existing tables in the connected database 
def drop_all_tables(database):
    cursor = database.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table[0]}')
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    database.commit()
    cursor.close()
    

# Ensure database exists and return a connection handle (using root credentials)
def get_database(db_name):

    my_host = os.getenv('DB_HOST', 'localhost')
    my_user = os.getenv('DB_USER', 'root')
    my_password = os.getenv('DB_PASSWORD', '')


    # Create the database if it does not exist (admin connection)
    root = mysql.connector.connect(
        host=my_host,
        user=my_user,
        password=my_password
    )
    temp_cursor = root.cursor()
    temp_cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
    root.commit()
    temp_cursor.close()
    root.close()

    # Connect to the requested database
    connection = mysql.connector.connect(
        host=my_host,
        user=my_user,
        password=my_password,
        database = db_name
    )
    return connection    


# Create all tables in dependency order
def create_tables(db):
    cursor_object = db.cursor()

    # Theatres: physical locations with unique (name, address)
    theatres = """CREATE TABLE IF NOT EXISTS theatres (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(128) NOT NULL,
                address VARCHAR(256) NOT NULL,
                phone VARCHAR(32) NOT NULL,
                is_open BOOLEAN NOT NULL DEFAULT FALSE,
                CONSTRAINT unique_theatre_address UNIQUE(name, address)
                )"""

    # Auditoriums: rooms in a theatre; positive number/capacity; cascade on theatre delete
    auditoriums = """CREATE TABLE IF NOT EXISTS auditoriums (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    theatre_id BIGINT NOT NULL,
                    number INT UNSIGNED NOT NULL,
                    capacity INT UNSIGNED NOT NULL,
                    FOREIGN KEY (theatre_id) REFERENCES theatres(id) ON DELETE CASCADE,
                    CONSTRAINT unique_theatre_number UNIQUE(theatre_id, number),
                    CONSTRAINT check_auditorium_number CHECK (number > 0),
                    CONSTRAINT check_auditorium_capacity CHECK (capacity > 0)
                    )"""

    # Seats: unique (auditorium, aisle, number); positive seat number
    seats = """CREATE TABLE IF NOT EXISTS seats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            aisle CHAR(1) NOT NULL,
            number INT UNSIGNED NOT NULL,
            auditorium_id BIGINT NOT NULL,
            FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id) ON DELETE CASCADE,
            CONSTRAINT unique_auditorium_seat UNIQUE (auditorium_id, aisle, number),
            CONSTRAINT check_seat_number CHECK (number > 0)
            )"""

    # Users: base accounts for all roles with timestamps and status
    users = """CREATE TABLE IF NOT EXISTS users (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            email VARCHAR(128) NOT NULL UNIQUE,
            phone VARCHAR(32) NOT NULL UNIQUE,
            birthday DATE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            role ENUM('customer', 'staff', 'driver', 'supplier') NOT NULL,
            account_status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
            date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )"""

    # Staff: staff profile per user; role enum and availability
    staff = """CREATE TABLE IF NOT EXISTS staff (
            user_id BIGINT PRIMARY KEY,
            theatre_id BIGINT NOT NULL,
            role ENUM('admin', 'runner') NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT FALSE,
            date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (theatre_id) REFERENCES theatres(id)
            )"""

    # Movies: catalog with rating constraint 0–5
    movies = """CREATE TABLE IF NOT EXISTS movies (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(128) NOT NULL,
            genre VARCHAR(64) NOT NULL,
            length_mins SMALLINT UNSIGNED NOT NULL,
            release_year SMALLINT UNSIGNED NOT NULL,
            keywords VARCHAR(256) NOT NULL,
            rating DECIMAL(3,2) NOT NULL,
            CONSTRAINT check_movie_rating CHECK(0.00 <= rating AND 5.00 >= rating)
            )"""

    # Movie showings: scheduled screenings; unique per (auditorium, start_time)
    movie_showings = """CREATE TABLE IF NOT EXISTS movie_showings (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    movie_id BIGINT NOT NULL,
                    auditorium_id BIGINT NOT NULL,
                    start_time DATETIME NOT NULL,
                    in_progress BOOLEAN DEFAULT FALSE,
                    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                    FOREIGN KEY (auditorium_id) REFERENCES auditoriums(id),
                    CONSTRAINT unique_auditorium_showing UNIQUE(auditorium_id, start_time)
                    )"""

    # Customers: profile mapping to default theatre
    customers = """CREATE TABLE IF NOT EXISTS customers (
                user_id BIGINT PRIMARY KEY,
                default_theatre_id BIGINT NOT NULL,
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (default_theatre_id) REFERENCES theatres(id)
                )"""

    # Customer showings: bookings with unique seat per showing
    customer_showings = """CREATE TABLE IF NOT EXISTS customer_showings (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        customer_id BIGINT NOT NULL,
                        movie_showing_id BIGINT NOT NULL,
                        seat_id BIGINT NOT NULL,
                        date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (movie_showing_id) REFERENCES movie_showings(id) ON DELETE CASCADE,
                        FOREIGN KEY (seat_id) REFERENCES seats(id),
                        CONSTRAINT unique_movie_seat UNIQUE(movie_showing_id, seat_id)
                        )"""

    # Payment methods: balances, expiration checks, and default flag
    payment_methods = """CREATE TABLE IF NOT EXISTS payment_methods (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        customer_id BIGINT NOT NULL,
                        card_number CHAR(16) NOT NULL,
                        expiration_month TINYINT UNSIGNED NOT NULL,
                        expiration_year SMALLINT UNSIGNED NOT NULL,
                        billing_address VARCHAR(256) NOT NULL,
                        balance DECIMAL(10,2) NOT NULL DEFAULT 100.00,
                        is_default BOOLEAN NOT NULL DEFAULT FALSE,
                        date_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers(user_id) ON DELETE CASCADE,
                        CONSTRAINT check_expiration_month CHECK (expiration_month BETWEEN 1 AND 12),
                        CONSTRAINT check_expiration_year CHECK (expiration_year >= 2025),
                        CONSTRAINT check_balance CHECK (balance >= 0)
                        )"""

    # Drivers: delivery drivers with vehicle info and rating bounds
    drivers = """CREATE TABLE IF NOT EXISTS drivers (
                user_id BIGINT PRIMARY KEY,
                license_plate VARCHAR(16) NULL,
                vehicle_type ENUM('car', 'bike', 'scooter', 'other') NOT NULL,
                vehicle_color VARCHAR(16) NOT NULL,
                duty_status ENUM('unavailable', 'available', 'on_delivery') NOT NULL DEFAULT 'unavailable',
                rating DECIMAL(3,2) NOT NULL DEFAULT 5.00,
                total_deliveries INT NOT NULL DEFAULT 0,
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT check_driver_rating CHECK (rating >= 0.00 AND rating <= 5.00)
                )"""

    # Suppliers: concession vendors with open/closed state
    suppliers = """CREATE TABLE IF NOT EXISTS suppliers (
                user_id BIGINT PRIMARY KEY,
                company_name VARCHAR(64) NOT NULL,
                company_address VARCHAR(256) NOT NULL,
                contact_phone VARCHAR(32) NOT NULL,
                is_open BOOLEAN NOT NULL DEFAULT FALSE,
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )"""

    # Products: menu items with pricing, inventory, category, and availability
    products = """CREATE TABLE IF NOT EXISTS products (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                supplier_id BIGINT NOT NULL,
                name VARCHAR(128) NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                inventory_quantity INT UNSIGNED DEFAULT 0 NOT NULL,
                size ENUM('small', 'medium', 'large') DEFAULT NULL,
                keywords VARCHAR(256),
                category ENUM('beverages', 'snacks', 'candy', 'food') NOT NULL,
                discount DECIMAL(10,2) UNSIGNED DEFAULT 0.00 NOT NULL,
                is_available BOOLEAN NOT NULL DEFAULT TRUE,
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(user_id) ON DELETE CASCADE,
                CONSTRAINT check_product_price CHECK (unit_price >= 0.00),
                CONSTRAINT check_product_inventory CHECK (inventory_quantity >= 0),
                CONSTRAINT unique_supplier_product UNIQUE(supplier_id, name),
                CONSTRAINT check_discount_value CHECK (discount >= 0.00)
                )"""

    # Deliveries: orders tying showings, payments, driver/staff, status, and totals
    deliveries = """CREATE TABLE IF NOT EXISTS deliveries (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            driver_id BIGINT,
            customer_showing_id BIGINT NOT NULL,
            payment_method_id BIGINT NOT NULL,
            staff_id BIGINT,
            payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending' NOT NULL,
            total_price DECIMAL(12,2) NOT NULL,
            coupon_id BIGINT DEFAULT NULL,
            coupon_code VARCHAR(64) DEFAULT NULL,
            discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            ngo_id INT DEFAULT NULL,
            ngo_name VARCHAR(128) DEFAULT NULL,
            donation_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            donation_percentage DECIMAL(5,2) DEFAULT NULL,
            delivery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_status ENUM('pending', 'accepted', 'in_progress', 'ready_for_pickup', 'in_transit', 
                        'delivered', 'fulfilled', 'cancelled') DEFAULT 'pending' NOT NULL,
            is_rated BOOLEAN NOT NULL DEFAULT FALSE,
            date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES drivers(user_id),
            FOREIGN KEY (customer_showing_id) REFERENCES customer_showings(id) ON DELETE CASCADE,
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
            FOREIGN KEY (staff_id) REFERENCES staff(user_id),
            CONSTRAINT check_total_price CHECK (total_price >= 0.00)
            )"""

    # Snack bundles: combo packages with discounted pricing
    snack_bundles = """CREATE TABLE IF NOT EXISTS snack_bundles (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(128) NOT NULL,
                    description VARCHAR(512),
                    original_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(10,2) NOT NULL,
                    created_by_staff_id BIGINT NOT NULL,
                    is_available BOOLEAN NOT NULL DEFAULT TRUE,
                    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by_staff_id) REFERENCES staff(user_id),
                    CONSTRAINT check_bundle_original_price CHECK (original_price >= 0.00),
                    CONSTRAINT check_bundle_price CHECK (total_price >= 0.00)
                    )"""

    # Bundle items: products included in bundles with quantities
    bundle_items = """CREATE TABLE IF NOT EXISTS bundle_items (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    bundle_id BIGINT NOT NULL,
                    product_id BIGINT NOT NULL,
                    quantity INT UNSIGNED NOT NULL DEFAULT 1,
                    FOREIGN KEY (bundle_id) REFERENCES snack_bundles(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    CONSTRAINT unique_bundle_product UNIQUE (bundle_id, product_id),
                    CONSTRAINT check_bundle_item_quantity CHECK (quantity > 0)
                    )"""
    
    # Cart items: unique (customer, product/bundle) with positive quantity
    cart_items = """CREATE TABLE IF NOT EXISTS cart_items (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    customer_id BIGINT NOT NULL,
                    product_id BIGINT,
                    bundle_id BIGINT,
                    quantity INT UNSIGNED NOT NULL DEFAULT 1,
                    FOREIGN KEY (customer_id) REFERENCES customers(user_id),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (bundle_id) REFERENCES snack_bundles(id) ON DELETE CASCADE,
                    CONSTRAINT check_cart_quantity CHECK (quantity > 0),
                    CONSTRAINT check_product_or_bundle CHECK ((product_id IS NOT NULL AND bundle_id IS NULL) OR (product_id IS NULL AND bundle_id IS NOT NULL))
                    )"""
    
    # Delivery items: link cart items to deliveries; unique pair
    delivery_items = """CREATE TABLE IF NOT EXISTS delivery_items (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                cart_item_id BIGINT NOT NULL,
                delivery_id BIGINT NOT NULL,
                discount DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
                FOREIGN KEY (cart_item_id) REFERENCES cart_items(id),
                FOREIGN KEY (delivery_id) REFERENCES deliveries(id) ON DELETE CASCADE,
                CONSTRAINT unique_delivery_item UNIQUE (delivery_id, cart_item_id)
                )"""

    # Coupons: discount codes unlocked by puzzles; difficulty represents puzzle difficulty
    coupons = """CREATE TABLE IF NOT EXISTS coupons (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(64) NOT NULL UNIQUE,
                difficulty INT NOT NULL DEFAULT 1,
                discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""

    # Code puzzles: store puzzle scripts and answers
    code_puzzles = """CREATE TABLE IF NOT EXISTS code_puzzles (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    folder VARCHAR(64) NOT NULL,
                    name VARCHAR(128) NOT NULL,
                    difficulty INT NOT NULL DEFAULT 1,
                    script TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )"""

    # NGO donations: track total donations per NGO
    ngo_donations = """CREATE TABLE IF NOT EXISTS ngo_donations (
                    ngo_id INT PRIMARY KEY NOT NULL,
                    total_amount_donated DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    CONSTRAINT check_ngo_donation_amount CHECK (total_amount_donated >= 0.00)
                    )"""

    # Execute DDL statements in dependency order
    cursor_object.execute(theatres)
    cursor_object.execute(auditoriums)
    cursor_object.execute(seats)
    cursor_object.execute(users)
    cursor_object.execute(staff)
    cursor_object.execute(movies)
    cursor_object.execute(movie_showings)
    cursor_object.execute(customers)
    cursor_object.execute(customer_showings)
    cursor_object.execute(payment_methods)
    cursor_object.execute(drivers)
    cursor_object.execute(suppliers)
    cursor_object.execute(products)
    cursor_object.execute(snack_bundles)
    cursor_object.execute(bundle_items)
    cursor_object.execute(deliveries)
    cursor_object.execute(cart_items)
    cursor_object.execute(delivery_items)
    cursor_object.execute(coupons)
    cursor_object.execute(code_puzzles)
    cursor_object.execute(ngo_donations)

    # Persist schema changes and close the connection
    db.commit()
    cursor_object.close()
    db.close()


# Recreate schema for production database
prod_database = get_database("movie_munchers_prod")
drop_all_tables(prod_database)
create_tables(prod_database)

# Recreate schema for development database
dev_database = get_database("movie_munchers_dev")
drop_all_tables(dev_database)
create_tables(dev_database)

# Recreate schema for testing database
test_database = get_database("movie_munchers_test")
drop_all_tables(test_database)
create_tables(test_database)
