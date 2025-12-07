from app.app import db
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, SMALLINT, DECIMAL
from sqlalchemy.sql import func, expression
from flask_login import UserMixin

class Theatres(db.Model):
    __tablename__ = 'theatres'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    name = db.Column(db.String(128), nullable = False)
    address = db.Column(db.String(256), nullable = False)
    phone = db.Column(db.String(32), nullable = False)
    is_open = db.Column(db.Boolean, server_default = expression.false(), nullable = False, )
    __table_args__ = (db.UniqueConstraint('name', 'address', name = 'unique_theatre_address'), )

    def __repr__(self):
        return f'<Theatre id = {self.id} name = {self.name!r} address = {self.address!r} is_open = {self.is_open}>'
    
class Auditoriums(db.Model):
    __tablename__ = 'auditoriums'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    theatre_id = db.Column(db.BigInteger, db.ForeignKey('theatres.id', ondelete='CASCADE'), nullable = False)
    number = db.Column(INTEGER(unsigned = True), nullable = False)
    capacity = db.Column(INTEGER(unsigned = True), nullable = False)
    __table_args__ = (db.UniqueConstraint('theatre_id', 'number', name = 'unique_theatre_number'), db.CheckConstraint('number > 0', name = 'check_auditorium_number'), db.CheckConstraint('capacity > 0', name = 'check_auditorium_capacity'))

    def __repr__(self):
        return f'<Auditorium id = {self.id} number = {self.number} theatre = {self.theatre_id}>'
    
class Seats(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    aisle = db.Column(db.String(1), nullable = False)
    number = db.Column(INTEGER(unsigned = True), nullable = False)
    auditorium_id = db.Column(db.BigInteger, db.ForeignKey('auditoriums.id', ondelete='CASCADE'), nullable = False)
    __table_args__ = (db.UniqueConstraint('auditorium_id', 'aisle', 'number', name = 'unique_auditorium_seat'), db.CheckConstraint('number > 0', name = 'check_seat_number'))

    def __repr__(self):
        return f'<Seat id = {self.id} aisle = {self.aisle} number = {self.number} auditorium = {self.auditorium_id}>'

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    name = db.Column(db.String(128), nullable = False)
    email = db.Column(db.String(128), unique = True, nullable = False)
    phone = db.Column(db.String(128), unique = True, nullable = False)
    birthday = db.Column(db.Date, nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    role = db.Column(db.Enum('customer', 'staff', 'driver', 'supplier', name = 'user_role'), nullable = False)
    account_status = db.Column(db.Enum('active', 'inactive', name = 'account_status'), nullable = False, server_default = 'active')
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())

    def __repr__(self):
        return f'<User id = {self.id} email = {self.email!r} role = {self.role} status = {self.account_status}>'
    
    @property
    def is_active(self):
        return self.account_status == 'active'

class Staff(db.Model):
    __tablename__ = 'staff'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key = True)
    theatre_id = db.Column(db.BigInteger, db.ForeignKey('theatres.id'), nullable = False)
    role = db.Column(db.Enum('admin', 'runner', name = 'staff_role'), nullable = False)
    is_available = db.Column(db.Boolean, nullable = False, server_default = expression.false())
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())

    def __repr__(self):
        return f'<Staff user_id = {self.user_id} theatre_id = {self.theatre_id} role = {self.role} is_available = {self.is_available}>'
    
class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    title = db.Column(db.String(128), nullable = False)
    genre = db.Column(db.String(64), nullable = False)
    length_mins = db.Column(SMALLINT(unsigned = True), nullable = False)
    release_year = db.Column(SMALLINT(unsigned = True), nullable = False)
    keywords = db.Column(db.String(256), nullable = False)
    rating = db.Column(DECIMAL(3,2), nullable = False)
    __table_args__ = (db.CheckConstraint('0.00 <= rating AND 5.00 >= rating', name = 'check_movie_rating'),)

    def __repr__(self):
        return f'<Movie id = {self.id} title = {self.title!r} length_mins = {self.length_mins} rating = {self.rating}>'
    
class MovieShowings(db.Model):
    __tablename__ = 'movie_showings'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    movie_id = db.Column(db.BigInteger, db.ForeignKey('movies.id', ondelete='CASCADE'),  nullable = False)
    auditorium_id = db.Column(db.BigInteger, db.ForeignKey('auditoriums.id'), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)
    in_progress = db.Column(db.Boolean, server_default = expression.false())
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.UniqueConstraint('auditorium_id', 'start_time', name = 'unique_auditorium_showing'),)

    def __repr__(self):
        return f'<Movie Showings id = {self.id} movie_id = {self.movie_id} theatre_id = {self.theatre_id} auditorium_id = {self.auditorium_id} start_time = {self.start_time}>'

class Customers(db.Model):
    __tablename__ = 'customers'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key = True)
    default_theatre_id = db.Column(db.BigInteger, db.ForeignKey('theatres.id'), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())

    def __repr__(self):
        return f'<Customers user_id = {self.user_id} default_theatre_id = {self.default_theatre_id}>'
    
class CustomerShowings(db.Model):
    __tablename__ = 'customer_showings'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customers.user_id', ondelete='CASCADE'), nullable = False)
    movie_showing_id = db.Column(db.BigInteger, db.ForeignKey('movie_showings.id', ondelete='CASCADE'), nullable = False)
    seat_id = db.Column(db.BigInteger, db.ForeignKey('seats.id'), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.UniqueConstraint('movie_showing_id', 'seat_id', name = 'unique_movie_seat'),)

    def __repr__(self):
        return f'<Customer Showings id = {self.id} customer_id = {self.customer_id} movie_showing_id = {self.movie_showing_id} seat_id = {self.seat_id}>'


class PaymentMethods(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customers.user_id', ondelete='CASCADE'), nullable = False)
    card_number = db.Column(db.String(16), nullable = False)
    expiration_month = db.Column(TINYINT(unsigned = True), nullable = False)
    expiration_year = db.Column(SMALLINT(unsigned = True), nullable = False)
    billing_address = db.Column(db.String(256), nullable = False)
    balance = db.Column(DECIMAL(10,2), server_default = u'0.00', nullable = False)
    is_default = db.Column(db.Boolean, server_default = expression.false(), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.CheckConstraint('expiration_month BETWEEN 1 AND 12', name = 'check_expiration_month'), db.CheckConstraint('expiration_year >= 2025', name = 'check_expiration_year'), db.CheckConstraint('balance >= 0', name = 'check_balance'))

    def __repr__(self):
        last4 = self.card_number[-4:]
        return f'<Payment Methods id = {self.id} customer_id = {self.customer_id} last4 = {last4!r} expiration_date = {self.expiration_month:02d/self.expiration_year} is_default = {self.is_default}>'

class Drivers(db.Model):
    __tablename__ = 'drivers'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key = True)
    license_plate = db.Column(db.String(16), nullable = False)
    vehicle_type = db.Column(db.Enum('car', 'bike', 'scooter', 'other'), nullable = False)
    vehicle_color = db.Column(db.String(16), nullable = False)
    duty_status = db.Column(db.Enum('unavailable', 'available', 'on_delivery'), server_default = 'unavailable', nullable = False)
    rating = db.Column(DECIMAL(3,2), server_default = u'5.00', nullable = False)
    total_deliveries = db.Column(db.Integer, server_default = '0', nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.CheckConstraint('rating >= 0.00 AND rating <= 5.00', name = 'check_driver_rating'),)

    def __repr__(self):
        return f'<Drivers user_id = {self.user_id} license_plate = {self.license_plate!r} vehicle_type = {self.vehicle_type} duty_status = {self.duty_status} rating = {self.rating} total_deliveries = {self.total_deliveries}>'

class Suppliers(db.Model):
    __tablename__ = 'suppliers'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key = True)
    company_name = db.Column(db.String(64), nullable = False)
    company_address = db.Column(db.String(256), nullable = False)
    contact_phone = db.Column(db.String(32), nullable = False)
    is_open = db.Column(db.Boolean, server_default = expression.false(), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())

    def __repr__(self):
        return f'<Suppliers user_id = {self.user_id} company_name = {self.company_name!r} is_open = {self.is_open}>'

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    supplier_id = db.Column(db.BigInteger, db.ForeignKey('suppliers.user_id', ondelete='CASCADE'), nullable = False)
    name = db.Column(db.String(128), nullable = False)
    unit_price = db.Column(DECIMAL(10,2), nullable = False)
    inventory_quantity = db.Column(INTEGER(unsigned = True), server_default = '0', nullable = False)
    size = db.Column(db.Enum('small', 'medium', 'large'), nullable = True)
    keywords = db.Column(db.String(256))
    category = db.Column(db.Enum('beverages', 'snacks', 'candy', 'food'), nullable = False)
    discount = db.Column(DECIMAL(10,2), server_default = u'0.00', nullable = False)
    is_available = db.Column(db.Boolean, server_default = expression.true(), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.CheckConstraint('unit_price >= 0.00', name = 'check_product_price'), db.CheckConstraint('inventory_quantity >= 0', name = 'check_product_inventory'), db.UniqueConstraint('supplier_id', 'name', name = 'unique_supplier_product'), db.CheckConstraint('discount >= 0.00', name = 'check_discount_value'))

    def __repr__(self):
        return f'<Products id = {self.id} name = {self.name!r} category = {self.category} supplier_id = {self.supplier_id} unit_price = {self.unit_price} size = {self.size} inventory_quantity = {self.inventory_quantity} is_available = {self.is_available}>'

class Deliveries(db.Model):
    __tablename__ = 'deliveries'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    driver_id = db.Column(db.BigInteger, db.ForeignKey('drivers.user_id'))
    customer_showing_id = db.Column(db.BigInteger, db.ForeignKey('customer_showings.id', ondelete='CASCADE'), nullable = False)
    payment_method_id = db.Column(db.BigInteger, db.ForeignKey('payment_methods.id'), nullable = False)
    staff_id = db.Column(db.BigInteger, db.ForeignKey('staff.user_id'))
    payment_status = db.Column(db.Enum('pending', 'completed', 'failed'), server_default = 'pending', nullable = False)
    # Total before any coupon discount is applied
    total_price = db.Column(DECIMAL(12,2), nullable = False)
    # Optional coupon fields to record applied coupon and discount amount
    coupon_id = db.Column(db.BigInteger, nullable=True)
    coupon_code = db.Column(db.String(64), nullable=True)
    discount_amount = db.Column(DECIMAL(12,2), nullable=False, server_default=u'0.00')
    # Donation fields
    ngo_id = db.Column(db.Integer, nullable=True)
    ngo_name = db.Column(db.String(128), nullable=True)
    donation_amount = db.Column(DECIMAL(12,2), nullable=False, server_default=u'0.00')
    donation_percentage = db.Column(DECIMAL(5,2), nullable=True)
    delivery_time = db.Column(db.DateTime, server_default = 'CURRENT_TIMESTAMP', server_onupdate = 'CURRENT_TIMESTAMP', nullable = False)
    delivery_status = db.Column(db.Enum('pending', 'accepted', 'in_progress', 'ready_for_pickup', 'in_transit', 'delivered', 'fulfilled', 'cancelled'), server_default = 'pending', nullable = False)
    is_rated = db.Column(db.Boolean, server_default = expression.false(), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.CheckConstraint('total_price >= 0.00', name = 'check_total_price'),)

    def __repr__(self):
        return f'<Deliveries id = {self.id} driver_id = {self.driver_id} customer_showing_id = {self.customer_showing_id} payment_method_id = {self.payment_method_id} staff_id = {self.staff_id} payment_status = {self.payment_status} total_price = {self.total_price} coupon_code = {self.coupon_code} discount_amount = {self.discount_amount} ngo_name = {self.ngo_name} donation_amount = {self.donation_amount} delivery_time = {self.delivery_time} delivery_status = {self.delivery_status}>'
    
class DeliveryItems(db.Model):
    __tablename__ = 'delivery_items'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    cart_item_id = db.Column(db.BigInteger, db.ForeignKey('cart_items.id'), nullable = False)
    delivery_id = db.Column(db.BigInteger, db.ForeignKey('deliveries.id', ondelete='CASCADE'), nullable = False)
    __table_args__ = (db.UniqueConstraint('delivery_id', 'cart_item_id', name = 'unique_delivery_item'),)

    def __repr__(self):
        return f'<Delivery Items id = {self.id} cart_item_id = {self.cart_item_id} delivery_id = {self.delivery_id}>'

class CartItems(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customers.user_id'), nullable = False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id', ondelete='CASCADE'), nullable = True)
    bundle_id = db.Column(db.BigInteger, db.ForeignKey('snack_bundles.id', ondelete='CASCADE'), nullable = True)
    quantity = db.Column(INTEGER(unsigned = True), server_default = '1', nullable = False)
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name = 'check_cart_quantity'),
        db.CheckConstraint('(product_id IS NOT NULL AND bundle_id IS NULL) OR (product_id IS NULL AND bundle_id IS NOT NULL)', name = 'check_product_or_bundle')
    )

    def __repr__(self):
        return f'<Cart Items id = {self.id} customer_id = {self.customer_id} product id = {self.product_id} quantity = {self.quantity}>'


class Coupons(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    # Difficulty indicates how hard the puzzle is to unlock this coupon (e.g., 1..10)
    difficulty = db.Column(db.Integer, nullable=False, server_default='1')
    # Discount percentage applied to the order total (0.00 - 100.00)
    discount_percent = db.Column(DECIMAL(5,2), nullable=False, server_default='0.00')
    is_active = db.Column(db.Boolean, nullable=False, server_default=expression.true())
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())

    def __repr__(self):
        return f'<Coupons id={self.id} code={self.code!r} difficulty={self.difficulty} discount_percent={self.discount_percent} active={self.is_active}>'


class CodePuzzles(db.Model):
    __tablename__ = 'code_puzzles'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    folder = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)  # filename without extension
    difficulty = db.Column(db.Integer, nullable=False, server_default='1')
    script = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default=expression.true())
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())

    def __repr__(self):
        return f'<CodePuzzles id={self.id} folder={self.folder!r} name={self.name!r} difficulty={self.difficulty} active={self.is_active}>'
class SnackBundles(db.Model):
    __tablename__ = 'snack_bundles'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.String(512))
    original_price = db.Column(DECIMAL(10,2), nullable = False)
    total_price = db.Column(DECIMAL(10,2), nullable = False)
    created_by_staff_id = db.Column(db.BigInteger, db.ForeignKey('staff.user_id'), nullable = False)
    is_available = db.Column(db.Boolean, server_default = expression.true(), nullable = False)
    date_added = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone = True), nullable = False, server_default = func.current_timestamp(), server_onupdate = func.current_timestamp())
    __table_args__ = (db.CheckConstraint('original_price >= 0.00', name = 'check_bundle_original_price'), db.CheckConstraint('total_price >= 0.00', name = 'check_bundle_price'),)

    def __repr__(self):
        return f'<SnackBundle id = {self.id} name = {self.name!r} total_price = {self.total_price} is_available = {self.is_available}>'

class BundleItems(db.Model):
    __tablename__ = 'bundle_items'
    id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)
    bundle_id = db.Column(db.BigInteger, db.ForeignKey('snack_bundles.id', ondelete='CASCADE'), nullable = False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.id', ondelete='CASCADE'), nullable = False)
    quantity = db.Column(INTEGER(unsigned = True), server_default = '1', nullable = False)
    __table_args__ = (db.UniqueConstraint('bundle_id', 'product_id', name = 'unique_bundle_product'), db.CheckConstraint('quantity > 0', name = 'check_bundle_item_quantity'))

    def __repr__(self):
        return f'<BundleItem id = {self.id} bundle_id = {self.bundle_id} product_id = {self.product_id} quantity = {self.quantity}>'

class NgoDonations(db.Model):
    __tablename__ = 'ngo_donations'
    ngo_id = db.Column(db.Integer, primary_key=True, nullable=False)
    total_amount_donated = db.Column(DECIMAL(12,2), nullable=False, server_default=u'0.00')
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    last_updated = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp())
    __table_args__ = (db.CheckConstraint('total_amount_donated >= 0.00', name='check_ngo_donation_amount'),)

    def __repr__(self):
        return f'<NgoDonations ngo_id = {self.ngo_id} total_amount_donated = {self.total_amount_donated}>'
