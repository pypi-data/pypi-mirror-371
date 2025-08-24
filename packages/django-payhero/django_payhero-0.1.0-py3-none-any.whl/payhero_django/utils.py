
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from .exceptions import ConfigurationError

def get_payhero_setting(setting_name):
    """
    Helper function to get a setting from the PAYHERO_SETTINGS dict.
    Raises a clear error if the setting is missing.
    """
    try:
        payhero_settings = settings.PAYHERO_SETTINGS
    except AttributeError:
        raise ImproperlyConfigured("PAYHERO_SETTINGS dictionary is not defined in your settings.py")

    value = payhero_settings.get(setting_name)
    if not value:
        raise ConfigurationError(f"'{setting_name}' is not configured in your PAYHERO_SETTINGS.")
    
    return value