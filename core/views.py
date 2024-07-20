from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from urllib.parse import urljoin
from .forms import SignUpForm, ProfileForm, UserUpdateForm
from .models import Profile, Route, PreBooking, Booking, PastTrip, FareMatrix
from .utils import (
    geocode_address, generate_temp_ref, create_booking, logout_and_cleanup,
    create_past_trip, calculate_fare, get_current_site_url, extract_public_id, delete_old_profile
)
import requests
import cloudinary

def login_view(request):
    if request.method == 'POST':
        submitted_username = request.POST['username']
        submitted_password = request.POST['password']
        user_object = authenticate(
            username=submitted_username,
            password=submitted_password
        )
        if user_object is None:
            messages.add_message(request, messages.INFO, 'Invalid login.')
            return redirect(request.path_info)
        login(request, user_object)
        return redirect('index')
    else:
        return render(request, 'core/login_view.html')
    
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save the form data but don't commit yet
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            # Ensure only one of is_passenger or is_driver is selected
            is_passenger = form.cleaned_data.get('is_passenger')
            is_driver = form.cleaned_data.get('is_driver')
            if is_passenger and is_driver:
                messages.error(request, 'Please select only one option: Passenger or Driver.')
                return redirect('signup_view')
            if not is_passenger and not is_driver:
                messages.error(request, 'Please select at least one option: Passenger or Driver.')
                return redirect('signup_view')
            # Save the user with updated fields
            user.save()
            # Now save the profile information
            profile = user.profile
            profile.is_passenger = is_passenger
            profile.is_driver = is_driver
            profile.save()
            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Authentication failed. Please try logging in.')
                return redirect('login_view')
    else:
        form = SignUpForm()
    return render(request, 'core/signup_view.html', {'form': form})

@login_required
def index(request):
    # Check if there is an active route, prebooking, and booking for the current user
    active_booking = Booking.objects.filter(user=request.user).first()
    active_route = Route.objects.filter(user=request.user).first()
    active_prebooking = PreBooking.objects.filter(user=request.user).first()

    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)

        elif active_booking and 'payment' in request.POST:
            # Delete active route
            if active_route:
                active_route.delete()
            messages.error(request, 'Please complete your current booking before creating a new one.')
            return redirect('index')

        elif 'payment' in request.POST:
            # Delete old prebooking
            if active_prebooking:
                active_prebooking.delete()

            try:
                # Create an instance of Prebooking with the data from Route if exists
                if active_route:

                    create_prebooking = PreBooking.objects.create(
                        user=request.user,
                        profile=request.user.profile,
                        pickup_location=active_route.pickup_location,
                        dropoff_location=active_route.dropoff_location,
                        pickup_lat=active_route.pickup_lat,
                        pickup_lng=active_route.pickup_lng,
                        dropoff_lat=active_route.dropoff_lat,
                        dropoff_lng=active_route.dropoff_lng,
                        distance=active_route.distance,
                        estimated_duration=active_route.estimated_duration,
                        fare=active_route.fare,
                    )
                    create_prebooking.save()
                    
                    # Redirect to payment view
                    return redirect('payment_view')

                else:
                    messages.error(request, 'No route found for booking.')
                    return redirect('index')

            except Route.DoesNotExist:
                messages.error(request, 'No route found for booking.')
                return redirect('index')
            
        elif 'calculate_fare' in request.POST:
            pickup_location = request.POST['pickup_location']
            dropoff_location = request.POST['dropoff_location']
            
            # Delete old route and other logic
            if active_route:
                if pickup_location == active_route.pickup_location and dropoff_location == active_route.dropoff_location:
                    messages.error(request, 'Please adjust any location before recalculating the fare.')
                    return redirect('index')
                active_route.delete()

            if not pickup_location or not dropoff_location:
                messages.error(request, 'Please enter both pickup and drop-off locations.')
                return redirect('index')
            
            else:
                # Geocode pick-up and drop-off locations
                pickup_geo = geocode_address(pickup_location)
                dropoff_geo = geocode_address(dropoff_location)

                # Compute for the fare
                distance = request.POST['distance_value']
                fare, additional_distance = calculate_fare( distance)

                # Store route details 
                active_route = Route.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'pickup_location': pickup_location,
                        'dropoff_location': dropoff_location,
                        'pickup_lat': pickup_geo['lat'],
                        'pickup_lng': pickup_geo['lng'],
                        'dropoff_lat': dropoff_geo['lat'],
                        'dropoff_lng': dropoff_geo['lng'],
                        'distance': request.POST['distance'],
                        'estimated_duration': request.POST['estimated_duration'],
                        'fare': fare,
                        'additional_distance': additional_distance,
                    }
                )

                # Redirect to prevent form resubmission on refresh
                return redirect('index')  # Redirect to GET request to display the updated active_route
            
    # Fetch the active_route again if redirected from a POST request
    active_route = Route.objects.filter(user=request.user).first()

    # Retrieve driver's active booking
    driver_active_booking = Booking.objects.filter(driver__user=request.user).first()

    # Default rendering for GET request or no form submission
    bookings = Booking.objects.filter(driver=None).order_by('created_at')  # Order by 'created_at' ascending

    # Handle refresh request for available bookings
    if request.GET.get('refresh') == 'true':
        bookings = Booking.objects.filter(driver=None).order_by('created_at')  # Order by 'created_at' ascending
        context = {
            'bookings': bookings,
            'driver_active_booking': Booking.objects.filter(driver__user=request.user).first(),
        }
        return render(request, 'core/_bookings.html', context)
    
    fare_matrix = FareMatrix.objects.first()  # Retrieves the first FareMatrix instance found in the database

    context = {
        'user': request.user,
        'profile': request.user.profile,
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'bookings': bookings,
        'active_booking': active_booking,
        'active_route': active_route,
        'driver_active_booking': driver_active_booking,
        'fare_matrix': fare_matrix,
    }
    return render(request, 'core/index.html', context)

@login_required
def payment_view(request):
    active_prebooking = PreBooking.objects.filter(user=request.user).first()

    if not active_prebooking:
        return redirect('index')

    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)

        if 'confirm_payment' in request.POST:
            payment_method = request.POST.get('payment_method')

            if payment_method == 'cash':
                if active_prebooking.session_id:
                    # Expire existing session if it exists
                    url = f'https://api.paymongo.com/v1/checkout_sessions/{active_prebooking.session_id}/expire'
                    headers = {
                        "accept": "application/json",
                        "authorization": f'Basic {settings.PAYMONGO_ENCODED_AUTH}'
                    }
                    response = requests.post(url, headers=headers)

                # Create booking with cash payment
                create_booking(request.user, active_prebooking, 'Cash')
                active_prebooking.delete()
                booking = Booking.objects.filter(user=request.user).first()
                return redirect('waiting_view', booking_id=booking.booking_id)

            elif payment_method == 'e_wallet_bank':
                if active_prebooking.session_id:
                    # Retrieve checkout session URL if session already exists
                    url = f'https://api.paymongo.com/v1/checkout_sessions/{active_prebooking.session_id}'
                    headers = {
                        "accept": "application/json",
                        'Authorization': f'Basic {settings.PAYMONGO_ENCODED_AUTH}'
                    }
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        checkout_url = response.json()['data']['attributes']['checkout_url']
                        return redirect(checkout_url)

                # Create new checkout session for e-wallet/bank payment
                temp_ref = generate_temp_ref()
                fare = int(active_prebooking.fare * 100)

                current_site_url = get_current_site_url(request)
                cancel_url = urljoin(current_site_url, '/payment/')
                sucess_url = urljoin(current_site_url, '/payment/')

                url = 'https://api.paymongo.com/v1/checkout_sessions'

                headers = {
                    "accept": "application/json",
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {settings.PAYMONGO_ENCODED_AUTH}'
                }

                payload = {
                    "data": {
                        "attributes": {
                            "send_email_receipt": False,
                            "show_description": True,
                            "show_line_items": False,
                            "cancel_url": cancel_url,
                            "description": f"Trip from {active_prebooking.pickup_location.split(',')[0].strip()} to {active_prebooking.dropoff_location.split(',')[0].strip()}",
                            "line_items": [
                                {
                                    "currency": "PHP",
                                    "amount": fare,
                                    "name": "TrikeIt Ride",
                                    "quantity": 1
                                }
                            ],
                            "payment_method_types": ["qrph", "card", "dob", "dob_ubp", "brankas_bdo", "brankas_landbank", "brankas_metrobank", "gcash", "grab_pay", "paymaya"],
                            "reference_number": temp_ref,
                            "success_url": sucess_url,
                            "metadata": {
                                "temp_ref": temp_ref
                            }
                        }
                    }
                }

                try:
                    response = requests.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        active_prebooking.session_id = response.json()['data']['id']
                        active_prebooking.save()
                        checkout_url = response.json()['data']['attributes']['checkout_url']
                        return redirect(checkout_url)
                    else:
                        messages.error(request, 'Failed to initiate payment. Please try again.')
                        return redirect('payment_view')

                except requests.RequestException as e:
                    messages.error(request, f'Error occurred during payment initiation: {str(e)}')
                    return redirect('payment_view')

            else:
                messages.error(request, 'Invalid payment method selected.')
                return redirect('payment_view')

        elif 'edit_booking' in request.POST:
            # Expire session and delete pre-booking
            if active_prebooking.session_id:
                url = f'https://api.paymongo.com/v1/checkout_sessions/{active_prebooking.session_id}/expire'
                headers = {
                    "accept": "application/json",
                    "authorization": f'Basic {settings.PAYMONGO_ENCODED_AUTH}'
                }
                response = requests.post(url, headers=headers)
            active_prebooking.delete()
            return redirect('index')

    else:  # Handle GET request
        if active_prebooking and active_prebooking.session_id:
            # Check status of existing session
            url = f'https://api.paymongo.com/v1/checkout_sessions/{active_prebooking.session_id}'
            headers = {
                "accept": "application/json",
                'Authorization': f'Basic {settings.PAYMONGO_ENCODED_AUTH}'
            }
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    session_data = response.json()['data']['attributes']
                    if 'payments' in session_data and session_data['payments']:
                        status = session_data['payments'][0]['attributes']['status']
                        if status == 'paid':
                            payment_method_used = session_data['payment_method_used']
                            create_booking(request.user, active_prebooking, payment_method_used)
                            active_prebooking.delete()
                            booking = Booking.objects.filter(user=request.user).first()
                            return redirect('waiting_view', booking_id=booking.booking_id)

                    elif 'data' in session_data and 'attributes' in session_data['data']:
                        status = session_data['data']['attributes']['status']
                        if status == 'expired':
                            active_prebooking.session_id = None
                            active_prebooking.save()
                            messages.error(request, 'Payment session has expired. Please attempt the payment again.')

                else:
                    messages.error(request, 'Failed to retrieve payment status. Please try again.')

            except requests.RequestException as e:
                messages.error(request, f'Error occurred during payment status check: {str(e)}')

        context = {
            'user': request.user,
            'active_prebooking': active_prebooking
        }
        return render(request, 'core/payment_view.html', context)

@login_required
def waiting_view(request, booking_id):
    active_booking = Booking.objects.filter(booking_id=booking_id, user=request.user).first()

    # Check if the driver field in the booking is filled
    if active_booking: 
        if active_booking.driver:
            return redirect('confirmed_view', booking_id=active_booking.booking_id)

    # Delete active route and prebooking
    Route.objects.filter(user=request.user).delete()
    PreBooking.objects.filter(user=request.user).delete()

    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)
        
        elif 'cancel_booking' in request.POST:
            payment_method = active_booking.payment_method

            if payment_method == 'Cash':
                active_booking.delete()
                messages.success(request, 'Booking cancelled successfully.')
            else:
                active_booking.delete()
                messages.success(request, 'Booking cancelled successfully. Refund is unavailable for test transactions.')

            return redirect('index')  # Redirect after POST to avoid resubmission
        
    completed_trip = PastTrip.objects.filter(booking_id=booking_id).first()
    if completed_trip:
        return redirect('review_trip_view', booking_id=booking_id)

    context = {
        'user': request.user,
        'profile': request.user.profile,
        'booking': active_booking,
        'api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'core/waiting_view.html', context)

@login_required
def confirmed_view(request, booking_id):
    confirmed_booking = Booking.objects.filter(booking_id=booking_id).first()
    
    past_trip = PastTrip.objects.filter(booking_id=booking_id).first()
    if past_trip:
        return redirect('review_trip_view', booking_id=past_trip.booking_id)

    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)
        
        if not confirmed_booking.driver:
            # Handle the case where driver is not assigned
            if 'accept' in request.POST:
                driver_profile = get_object_or_404(Profile, user=request.user)

                # Assign the driver to the booking
                confirmed_booking.driver = driver_profile
                confirmed_booking.status = 'driver_enroute'
                confirmed_booking.save()

                # Redirect using PRG pattern
                return HttpResponseRedirect(request.path_info)  # Redirect to the same page to refresh context
        
        else:
            # Handle actions when driver is already assigned
            if 'picked_up' in request.POST:
                confirmed_booking.status = 'enroute_to_dest'
                confirmed_booking.save()

                # Redirect using PRG pattern
                return HttpResponseRedirect(request.path_info)  # Redirect to the same page to refresh context

    # Render the template with appropriate context
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'confirmed_booking': confirmed_booking,
    }
    return render(request, 'core/confirmed_view.html', context)

@login_required
def review_trip_view(request, booking_id):
    # Retrieve completed trip
    completed_trip = Booking.objects.filter(booking_id=booking_id).first()
    past_trip = PastTrip.objects.filter(booking_id=booking_id).first()


    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)
        
        if 'dropped_off' in request.POST:
            create_past_trip(completed_trip)
            completed_trip.delete()
            # Redirect to the same view for rating and comment
            return redirect('review_trip_view', booking_id=booking_id)
        
        if 'submit_review' in request.POST:
            past_trip.rating = float(request.POST.get('rating'))
            past_trip.comment = request.POST.get('comment', "")
            past_trip.save()
            messages.info(request, 'Review submitted successfully.')
            return redirect('index')

    # Render the template with appropriate context
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'booking_id': booking_id,
        'past_trip': past_trip,
    }
    return render(request, 'core/review_trip_view.html', context)


def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        if 'logout' in request.POST:
            return logout_and_cleanup(request)
    
        if 'reset_picture' in request.POST:
            profile.reset_profile_picture()
            messages.success(request, 'Profile picture reset to default.')
            return redirect('profile_view')

        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        # Get the old profile picture URL and extract its public ID
        old_picture_url = profile.profile_picture
        old_picture_public_id = extract_public_id(old_picture_url)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the new profile picture
            profile = profile_form.save(commit=False)

            # Get the new profile picture URL after saving and extract its public ID
            new_picture_url = profile.profile_picture
            new_picture_public_id = extract_public_id(new_picture_url)

            # Check if the new picture is different from the old one
            if old_picture_public_id and old_picture_public_id != new_picture_public_id:
                delete_old_profile(old_picture_public_id)

            # Save the profile with the new picture
            profile.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'is_passenger': profile.is_passenger,
        'is_driver': profile.is_driver,
        'cloud_name': cloudinary.config().cloud_name
    }
    return render(request, 'core/profile_view.html', context)

def extract_public_id(url):
    # Assuming the URL is in the format 'https://res.cloudinary.com/your_cloud_name/image/upload/v.../public_id'
    if url:
        return url.split('/')[-2] + '/' + url.split('/')[-1].split('.')[0]
    return None

def delete_old_profile(public_id):
    cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
    cloudinary.uploader.destroy(public_id, invalidate=True)

@login_required
def history_view(request):
    trip_history = PastTrip.objects.filter(user=request.user).order_by('-created_at')
    driver_trip_history = PastTrip.objects.filter(driver=request.user.profile).order_by('-created_at')

    if request.method == 'POST':
        if 'logout' in request.POST:
                return logout_and_cleanup(request)
        
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'driver_trip_history': driver_trip_history,
        'trip_history': trip_history,
    }
    return render(request, 'core/history_view.html', context)
