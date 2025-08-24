
from django.urls import path
from .views import payhero_callback_view

urlpatterns = [
    path(
        'payhero/callback/', 
        payhero_callback_view, 
        name='payhero_callback' # This name is used in settings
    ),
]