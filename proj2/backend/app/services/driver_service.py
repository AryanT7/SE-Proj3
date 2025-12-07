from app.models import *
from app.app import db
from app.services.user_service import UserService
import decimal

class DriverService:
    """Service layer for driver accounts and delivery operations.

    This module provides validation utilities and operations for drivers,
    plus helpers for assignment, completion, rating, and basic queries.
    """
    
    def __init__(self):
        """Initialize dependencies used by driver operations."""
        self.user_service = UserService()   

    def validate_driver(self, user_id):
        """Ensure the given user_id belongs to a driver.

        Args:
            user_id: The user's id to validate.

        Returns:
            Drivers: The driver record.

        Raises:
            ValueError: If no driver exists for the provided id.
        """
        driver = Drivers.query.filter_by(user_id=user_id).first()
        if not driver:
            raise ValueError(f"Driver {user_id} not found")
        return driver

    def validate_license_plate(self, license_plate):
        """Validate a license plate string (non-empty, ≤16 chars).

        Args:
            license_plate: The plate value to validate.

        Returns:
            str: The normalized plate string.

        Raises:
            ValueError: If not a string, empty/whitespace, or longer than 16.
        """
        try:
            str(license_plate)
            if not license_plate.strip():
                raise ValueError("License plate is required")
            if len(license_plate) > 16:
                raise ValueError("License plate must be 16 characters or less")
            return license_plate.strip()
        except:
            raise ValueError("License plate must be a string")

    def validate_vehicle_type(self, vehicle_type):
        """Validate vehicle type against the allowed set.

        Allowed values: 'car', 'bike', 'scooter', 'other'.

        Args:
            vehicle_type: The vehicle type to validate.

        Returns:
            str: The validated vehicle type.

        Raises:
            ValueError: If not a string or not in the allowed set.
        """
        try:
            str(vehicle_type)
            if vehicle_type not in ['car', 'bike', 'scooter', 'other']:
                raise ValueError("Vehicle type must be 'car', 'bike', 'scooter', or 'other")
            return vehicle_type
        except:
            raise ValueError("Vehicle type must be a string")

    def validate_vehicle_color(self, vehicle_color):
        """Validate vehicle color string (non-empty, ≤16 chars).

        Args:
            vehicle_color: The color to validate.

        Returns:
            str: The normalized color string.

        Raises:
            ValueError: If not a string, empty/whitespace, or longer than 16.
        """
        try:
            str(vehicle_color)
            if not vehicle_color.strip():
                raise ValueError("Vehicle color is required")
            if len(vehicle_color) > 16:
                raise ValueError("Vehicle color must be 16 characters or less")
            return vehicle_color.strip()
        except:
            raise ValueError("Vehicle color must be a string")
        
    def validate_duty_status(self, duty_status):
        """Validate driver duty status against the allowed set.

        Allowed values: 'unavailable', 'available', 'on_delivery'.

        Args:
            duty_status: The status to validate.

        Returns:
            str: The validated duty status.

        Raises:
            ValueError: If not a string or not in the allowed set.
        """
        try:
            str(duty_status)
            if duty_status not in ['unavailable', 'available', 'on_delivery']:
                raise ValueError("Duty status must be 'unavailable', 'available', or 'on_delivery'")
            return duty_status
        except:
            raise ValueError("Duty status must be a string")
    
    def validate_rating(self, rating):
        """Validate a numeric rating in the inclusive range [0.00, 5.00].

        Args:
            rating: A number (int/float/Decimal-like) to validate.

        Returns:
            Decimal: The normalized rating as Decimal.

        Raises:
            ValueError: If not numeric or out of bounds.
        """
        try:
            rating = decimal.Decimal(str(rating))
            if rating < decimal.Decimal('0.00') or rating > decimal.Decimal('5.00'):
                raise ValueError("Rating must be between 0.00 and 5.00")
            return rating
        except:
            raise ValueError("Rating must be a valid decimal number")
    
    def validate_total_deliveries(self, total_deliveries):
        """Validate total deliveries as a non-negative integer.

        Args:
            total_deliveries: The count to validate.

        Returns:
            int: The normalized deliveries count.

        Raises:
            ValueError: If not an integer or negative.
        """
        try:
            total_deliveries = int(total_deliveries)
            if total_deliveries < 0:
                raise ValueError("Total deliveries cannot be negative")
            return total_deliveries
        except:
            raise ValueError("Total deliveries must be an integer")

    def create_driver(self, name, email, phone, birthday, password, role,
                      license_plate, vehicle_type, vehicle_color,
                      duty_status, rating, total_deliveries):
        """Create a user with the driver role and matching driver record.

        Validation is performed for all driver-specific fields before creation.

        Args:
            name: Driver full name.
            email: Unique email address.
            phone: Unique phone number.
            birthday: Date of birth (YYYY-MM-DD or date).
            password: Plaintext password (will be hashed).
            role: Must be 'driver'.
            license_plate: Plate string (≤16 chars).
            vehicle_type: One of 'car', 'bike', 'scooter', 'other'.
            vehicle_color: Color string (≤16 chars).
            duty_status: One of 'unavailable', 'available', 'on_delivery'.
            rating: Initial rating in [0.00, 5.00].
            total_deliveries: Initial completed deliveries count (≥0).

        Returns:
            Drivers: The created driver record.

        Raises:
            ValueError: If role is not 'driver' or any validation fails.
        """
        if role != 'driver':
            raise ValueError("User role must be 'driver'")
        
        license_plate = self.validate_license_plate(license_plate=license_plate)
        vehicle_type = self.validate_vehicle_type(vehicle_type=vehicle_type)
        vehicle_color = self.validate_vehicle_color(vehicle_color=vehicle_color)
        duty_status = self.validate_duty_status(duty_status=duty_status)
        rating = self.validate_rating(rating=rating)
        total_deliveries = self.validate_total_deliveries(total_deliveries=total_deliveries)

        user = self.user_service.create_user(
            name=name, 
            email=email, 
            phone=phone, 
            birthday=birthday, 
            password=password, 
            role=role
        )
        
        driver = Drivers(
            user_id=user.id, 
            license_plate=license_plate, 
            vehicle_type=vehicle_type, 
            vehicle_color=vehicle_color, 
            duty_status=duty_status, 
            rating=rating, 
            total_deliveries=total_deliveries
        )

        db.session.add(driver)
        db.session.commit()
        return driver
    
    def update_driver_details(self, user_id, license_plate, vehicle_type, vehicle_color):
        """Update a driver's plate, vehicle type, and color.

        Args:
            user_id: Driver's user id.
            license_plate: New plate string.
            vehicle_type: New vehicle type.
            vehicle_color: New color string.

        Returns:
            Drivers: The updated driver record.

        Raises:
            ValueError: If the driver doesn't exist or plate is already used.
        """
        driver = self.validate_driver(user_id=user_id)
        plate_owner = Drivers.query.filter_by(license_plate=license_plate).first()
        if not plate_owner or plate_owner.user_id == driver.user_id:
            driver.license_plate = self.validate_license_plate(license_plate=license_plate)
            driver.vehicle_type = self.validate_vehicle_type(vehicle_type=vehicle_type)
            driver.vehicle_color = self.validate_vehicle_color(vehicle_color=vehicle_color)
            db.session.commit()
            return driver
        raise ValueError("License plate already in use")
    
    def update_driver_status(self, user_id, new_status):
        """Set the duty status for a given driver.

        Args:
            user_id: Driver's user id.
            new_status: New duty status string.

        Returns:
            Drivers: The updated driver record.

        Raises:
            ValueError: If the driver doesn't exist or status is invalid.
        """
        driver = self.validate_driver(user_id=user_id)
        driver.duty_status = self.validate_duty_status(duty_status=new_status)
        db.session.commit()
        return driver
    
    def get_available_drivers(self):
        """Return all drivers currently marked as available.

        Returns:
            list[Drivers]: Available driver records (possibly empty).
        """
        return Drivers.query.filter(Drivers.duty_status == 'available').all()
    
    def get_best_available_driver(self):
        """Return the highest-rated available driver.

        Returns:
            Drivers | None: The best available driver or None if none available.
        """
        best_driver = Drivers.query.filter_by(duty_status='available').order_by(Drivers.rating.desc()).first()
        return best_driver
    
    def try_assign_driver(self, delivery):
        """Assign the best available driver to a delivery.

        Sets delivery.driver_id, updates delivery_status to 'accepted',
        and moves the driver's duty status to 'on_delivery'.

        Args:
            delivery: A Deliveries model instance to be assigned.

        Returns:
            bool: True if assignment succeeded; False if no drivers available.

        Raises:
            ValueError: If the delivery reference is missing.
        """
        if not delivery:
            raise ValueError("Delievry not found")
        driver = self.get_best_available_driver()
        if not driver:
            return False
        delivery.driver_id = driver.user_id
        delivery.delivery_status = 'accepted'
        self.update_driver_status(user_id=delivery.driver_id, new_status='on_delivery')
        return True
    
    def delete_driver(self, user_id):
        """Delete a driver by removing the underlying user.

        Args:
            user_id: Driver's user id.

        Returns:
            bool: True if deletion succeeded.

        Raises:
            ValueError: If the driver does not exist.
        """
        driver = self.validate_driver(user_id=user_id)
        self.user_service.delete_user(driver.user_id)
        return True
    
    def complete_delivery(self, delivery_id):
        """Mark an accepted delivery as delivered and update driver stats.

        Increments driver's total_deliveries, sets delivery_status to 'delivered',
        and moves driver back to 'available'. Requires driver to be 'on_delivery'.

        Args:
            delivery_id: The delivery id to complete.

        Returns:
            Deliveries: The updated delivery record.

        Raises:
            ValueError: If delivery is missing, not accepted, driver missing,
                or driver is not currently 'on_delivery'.
        """
        delivery = Deliveries.query.filter_by(id=delivery_id).first()
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        if delivery.delivery_status != 'accepted':
            raise ValueError("Delivery must be accepted to be completed")
        
        driver = self.validate_driver(user_id=delivery.driver_id)
        if not driver:
            raise ValueError("Driver not found for this delivery")
        
        driver.total_deliveries += 1
        delivery.delivery_status = 'delivered'
        driver.duty_status = 'available'
        db.session.commit()
        db.session.refresh(delivery)
        return delivery
    
    def rate_driver(self, delivery_id, new_rating):
        """Rate the driver for a fulfilled delivery and update the average.

        If the driver has no prior deliveries, the rating is set directly;
        otherwise the new average is computed from the existing rating and count.

        Args:
            delivery_id: The delivery id to rate.
            new_rating: The rating value to apply.

        Returns:
            tuple[Drivers, Deliveries]: The updated driver and delivery.

        Raises:
            ValueError: If delivery is missing, not fulfilled, already rated,
                driver missing, or rating invalid.
        """
        delivery = Deliveries.query.filter_by(id=delivery_id).first()
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")
        
        if delivery.delivery_status != 'fulfilled': 
            raise ValueError("Can only rate fulfilled deliveries")
        
        if delivery.is_rated:
            raise ValueError(f"Delivery {delivery_id} has already been rated")
        
        driver = self.validate_driver(user_id=delivery.driver_id)
        if not driver:
            raise ValueError("Driver not found for this delivery")
        
        new_rating = self.validate_rating(new_rating)

        if driver.total_deliveries == 0:
            driver.rating = new_rating
        else:
            total_rating = driver.rating * driver.total_deliveries + new_rating
            driver.rating = total_rating / (driver.total_deliveries + 1)
        
        delivery.is_rated = True
        db.session.commit()
        return driver, delivery
        
    def show_completed_deliveries(self, driver_id):
        """List all fulfilled deliveries for the given driver.

        Args:
            driver_id: Driver's user id.

        Returns:
            list[Deliveries]: Fulfilled deliveries.

        Raises:
            ValueError: If the driver has no previous fulfilled deliveries.
        """
        driver = self.validate_driver(driver_id)
        deliveries = Deliveries.query.filter(
            Deliveries.driver_id == driver.user_id,
            Deliveries.delivery_status == 'fulfilled'
        ).all()
        if not deliveries:
            raise ValueError(f"No previous deliveries found for driver {driver.user_id}")
        return deliveries
    
    def get_active_delivery(self, driver_id):
        """Return the driver's active delivery if one exists.

        Active statuses include: 'pending', 'accepted', 'in_progress',
        'ready_for_pickup', 'in_transit'.

        Args:
            driver_id: Driver's user id.

        Returns:
            Deliveries: The active delivery.

        Raises:
            ValueError: If no active delivery is found for the driver.
        """
        driver = self.validate_driver(driver_id)
        active_statuses = ['pending', 'accepted', 'in_progress', 'ready_for_pickup', 'in_transit']
        delivery = Deliveries.query.filter(
            Deliveries.driver_id == driver.user_id,
            Deliveries.delivery_status.in_(active_statuses)
        ).first()
        if not delivery:
            raise ValueError(f"No active delivery found for driver {driver.user_id}") 
        return delivery
