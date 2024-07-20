from django.contrib import admin
from .models import Profile, PreBooking, Route, Booking, PastTrip, FareMatrix

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'contact_number', 'TODA', 'TODA_number', 'license_plate_number', 'is_passenger', 'is_driver', 'average_rating', 'profile_picture')
    search_fields = ('user__username', 'first_name', 'last_name', 'email', 'contact_number', 'TODA')

class RouteAdmin(admin.ModelAdmin):
    list_display = ('user', 'pickup_location', 'dropoff_location', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng', 'distance', 'estimated_duration', 'additional_distance', 'fare')
    search_fields = ('user__username', 'pickup_location', 'dropoff_location')

class PreBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile', 'pickup_location', 'dropoff_location', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng', 'distance', 'estimated_duration', 'fare', 'session_id')
    search_fields = ('user__username', 'pickup_location', 'dropoff_location', 'session_id')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'profile', 'pickup_location', 'dropoff_location', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng', 'distance', 'estimated_duration', 'fare', 'status', 'payment_method', 'driver', 'created_at')
    search_fields = ('booking_id', 'user__username', 'pickup_location', 'dropoff_location', 'status')

class PastTripAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'profile', 'pickup_location', 'dropoff_location', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng', 'distance', 'duration', 'fare', 'status', 'payment_method', 'driver', 'rating', 'comment', 'created_at', 'completed_at')
    search_fields = ('booking_id', 'user__username', 'pickup_location', 'dropoff_location', 'status')

class FareMatrixAdmin(admin.ModelAdmin):
    list_display = ('base_fare', 'base_distance', 'fare_per_km')
    search_fields = ('base_fare', 'base_distance', 'fare_per_km')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(PreBooking, PreBookingAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(PastTrip, PastTripAdmin)
admin.site.register(FareMatrix, FareMatrixAdmin)
