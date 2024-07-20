from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from cloudinary.models import CloudinaryField
import cloudinary, uuid

TODA_choices = (
    ('Loyola Heights (White)', 'Loyola Heights (White)'),
    ('Loyola Pansol (Green)', 'Loyola Pansol (Green)'),
)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(max_length=150)
    contact_number = models.CharField(max_length=11, blank=True)
    TODA = models.CharField(max_length=22, blank=True, choices=TODA_choices)
    TODA_number = models.CharField(max_length=5, blank=True)
    license_plate_number = models.CharField(max_length=30, blank=True)
    is_passenger = models.BooleanField(default=False)  # New field for Passenger classification
    is_driver = models.BooleanField(default=False)   # New field for driver classification
    average_rating = models.FloatField(default=0.0)
    profile_picture = models.URLField(blank=True, null=True)  # Changed to URLField

    def extract_public_id(self, url):
        if url:
            return url.split('/')[-2] + '/' + url.split('/')[-1].split('.')[0]
        return None

    def delete_old_profile(self, public_id):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
        cloudinary.uploader.destroy(public_id, invalidate=True)

    def reset_profile_picture(self):
        old_picture_url = self.profile_picture
        old_picture_public_id = self.extract_public_id(old_picture_url)
        
        if old_picture_public_id:
            self.delete_old_profile(old_picture_public_id)
        
        self.profile_picture = 'https://res.cloudinary.com/dtnlvvfkr/image/upload/v1721434731/default_profile_gi3dz6.png'
        self.save()

    def is_complete(self):
        if self.is_driver:
            # Driver profile completion requires all fields
            return all([
                self.user.first_name,
                self.user.last_name,
                self.user.email,
                self.contact_number,
                self.TODA,
                self.TODA_number,
                self.license_plate_number
            ])
        elif self.is_passenger:
            # Passenger profile completion might have fewer required fields
            return all([
                self.user.first_name,
                self.user.last_name,
                self.user.email,
                self.contact_number,
            ])
        else:
            # Handle case where neither is_driver nor is_passenger is True
            return False
        
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Route generation in homepage
class Route(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    distance = models.CharField(max_length=5)
    estimated_duration = models.CharField(max_length=5)
    additional_distance = models.DecimalField(max_digits=10, decimal_places=1, default=0.00, null=True, blank=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)

# Route for payment
class PreBooking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    distance = models.CharField(max_length=5)
    estimated_duration = models.CharField(max_length=5)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    session_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.pickup_location} to {self.dropoff_location}'

# Active booking
class Booking(models.Model):
    booking_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.OneToOneField(Profile, related_name='booking_as_passenger', on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    distance = models.CharField(max_length=5)
    estimated_duration = models.CharField(max_length=5)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=10)
    driver = models.OneToOneField(Profile, related_name='booking_as_driver', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = self.generate_booking_id()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.profile and not self.profile.is_passenger:
            raise ValidationError("The selected profile is not marked as a passenger.")
        if self.driver and not self.driver.is_driver:
            raise ValidationError("The selected profile is not marked as a driver.")

    def generate_booking_id(self):
        while True:
            new_id = uuid.uuid4().hex[:10].upper()
            if not Booking.objects.filter(booking_id=new_id).exists() and not PastTrip.objects.filter(booking_id=new_id).exists():
                return new_id

    def __str__(self):
        return f'{self.booking_id} - {self.user.username} - {self.pickup_location} to {self.dropoff_location}'
    
# Completed trips
class PastTrip(models.Model):
    booking_id = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, related_name='past_bookings_as_passenger', on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()
    distance = models.CharField(max_length=10)
    duration = models.DurationField(null=True, blank=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=10)
    driver = models.ForeignKey(Profile, related_name='past_bookings_as_driver', on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True)
    comment = models.TextField(default="", blank=True)
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.created_at and self.completed_at:
            self.duration = self.completed_at - self.created_at
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.booking_id} - {self.user.username} - {self.pickup_location} to {self.dropoff_location}'

@receiver(post_save, sender=PastTrip)
@receiver(post_delete, sender=PastTrip)
def update_driver_average_rating(sender, instance, **kwargs):
    update_driver_average_rating(instance.driver)

def update_driver_average_rating(driver_profile):
    past_bookings = PastTrip.objects.filter(driver=driver_profile)
    average_rating = past_bookings.aggregate(Avg('rating'))['rating__avg']
    if average_rating is not None:
        driver_profile.average_rating = round(average_rating, 2)
    else:
        driver_profile.average_rating = 0.0  # Set default value if no ratings
    driver_profile.save()

class FareMatrix(models.Model):
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    base_distance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fare_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Fare Matrix: Base Fare - PHP {self.base_fare}, Base Distance - {self.base_distance} km, Fare per km - PHP {self.fare_per_km}"


