class PayHeroError(Exception):
    """Base exception class for payhero_django."""
    pass

class PayHeroAPIError(PayHeroError):
    """Raised for errors returned by the PayHero API."""
    pass

class ConfigurationError(PayHeroError):
    """Raised for misconfiguration of the app."""
    pass