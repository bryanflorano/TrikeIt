import requests, random
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.sites.shortcuts import get_current_site
from .models import Booking, Route, PreBooking, PastTrip, FareMatrix
from decimal import Decimal
import cloudinary

def geocode_address(address):
    """
    Function to geocode an address using Google Geocoding API.
    Returns the latitude and longitude of the address.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return {'lat': location['lat'], 'lng': location['lng']}
    # Return None or handle errors appropriately
    return None

def generate_temp_ref():
    return f"{random.randint(1000000000, 9999999999)}"

def create_booking(user, active_prebooking, payment_method):
    booking = Booking(
        user=user,
        profile=user.profile,
        pickup_location=active_prebooking.pickup_location,
        dropoff_location=active_prebooking.dropoff_location,
        pickup_lat=active_prebooking.pickup_lat,
        pickup_lng=active_prebooking.pickup_lng,
        dropoff_lat=active_prebooking.dropoff_lat,
        dropoff_lng=active_prebooking.dropoff_lng,
        distance=active_prebooking.distance,
        estimated_duration=active_prebooking.estimated_duration,
        fare=active_prebooking.fare,
        payment_method=payment_method.title(),
        session_id=active_prebooking.session_id,
        status='finding_driver',
    )
    booking.booking_id = booking.generate_booking_id()
    booking.save()
    return booking

def create_past_trip(completed_trip, rating=None, comment=""):
    past_trip = PastTrip.objects.create(
        booking_id=completed_trip.booking_id,
        user=completed_trip.user,
        profile=completed_trip.profile,
        pickup_location=completed_trip.pickup_location,
        dropoff_location=completed_trip.dropoff_location,
        pickup_lat=completed_trip.pickup_lat,
        pickup_lng=completed_trip.pickup_lng,
        dropoff_lat=completed_trip.dropoff_lat,
        dropoff_lng=completed_trip.dropoff_lng,
        distance=completed_trip.distance,
        fare=completed_trip.fare,
        payment_method=completed_trip.payment_method,
        status='completed',
        driver=completed_trip.driver,
        created_at=completed_trip.created_at,
        rating=rating,
        comment=comment,
    )
    return past_trip

def calculate_fare(distance):
    distance = round(Decimal(distance) / 1000, 1)
    try:
        fare_matrix = FareMatrix.objects.first()  # Fetch the first (or relevant) FareMatrix instance
        if fare_matrix:
            base_fare = fare_matrix.base_fare
            base_distance = fare_matrix.base_distance
            fare_per_km = fare_matrix.fare_per_km

            if distance <= base_distance:
                fare = base_fare
                additional_distance = 0
            else:
                additional_distance = distance - base_distance
                fare = base_fare + (additional_distance * fare_per_km)

            return fare, additional_distance
        else:
            return None  # Handle case where no FareMatrix instance exists
    except FareMatrix.DoesNotExist:
        return None  # Handle case where no FareMatrix instance exists

def logout_and_cleanup(request):
    # Delete active route and prebooking for the user
    active_route = Route.objects.filter(user=request.user).first()
    active_prebooking = PreBooking.objects.filter(user=request.user).first()

    if active_route:
        active_route.delete()
    if active_prebooking:
        active_prebooking.delete()

    logout(request)
    return redirect('login_view')  # Redirect to login view after logout

def get_current_site_url(request):
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    return f'{protocol}://{current_site}'

def extract_public_id(url):
    """
    Extracts the public ID from a Cloudinary URL.
    """
    if url:
        return url.split('/')[-2] + '/' + url.split('/')[-1].split('.')[0]
    return None

def delete_old_profile(public_id):
    """
    Deletes the old profile picture from Cloudinary.
    """
    # Configure Cloudinary with credentials from Django settings
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
        api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
    )
    try:
        print(f"Attempting to delete picture with Public ID: {public_id}")
        cloudinary.uploader.destroy(public_id, invalidate=True)
        print(f"Deleted {public_id} successfully.")
    except Exception as e:
        print(f"Error deleting {public_id}: {e}")