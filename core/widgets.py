from django import forms
from django.forms.widgets import ClearableFileInput

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'widgets/custom_clearable_file_input.html'