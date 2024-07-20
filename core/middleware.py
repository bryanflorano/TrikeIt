from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.is_superuser and not request.user.profile.is_complete():
                if request.path not in [reverse('profile_view')]:
                    return redirect(reverse('profile_view'))  # Redirect to profile completion page

        response = self.get_response(request)
        return response
