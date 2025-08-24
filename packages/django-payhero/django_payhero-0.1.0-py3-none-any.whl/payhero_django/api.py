
import requests
import base64
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
from .utils import get_payhero_setting
from .exceptions import PayHeroAPIError
from .models import PayHeroTransaction

class PayHeroClient:
    """
    A client for interacting with the PayHero v2 API.
    """
    BASE_URL = "https://backend.payhero.co.ke/api/v2"

    def __init__(self):
        self.api_key = get_payhero_setting("API_KEY")
        self.channel_id = get_payhero_setting("CHANNEL_ID")
        self.callback_url_name = get_payhero_setting("CALLBACK_URL_NAME")
        
    def _get_headers(self):
        """Encodes the API key and returns the authorization headers."""
        # PayHero expects the API key to be Basic Auth encoded.
        # The key itself is used as the username with a blank password.
        encoded_key = base64.b64encode(f"{self.api_key}:".encode('utf-8')).decode('utf-8')
        return {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get_full_callback_url(self):
        """Constructs the full, absolute URL for the callback."""
        try:
            # Note: This requires you to have a Site configured for absolute URLs
            # For development, you can use ngrok.
            from django.contrib.sites.models import Site
            domain = Site.objects.get_current().domain
            protocol = 'https' # Assume https for production
            base_url = f"{protocol}://{domain}"
            return base_url + reverse(self.callback_url_name)
        except (ImportError, ImproperlyConfigured):
            # Fallback for simpler setups. You must provide the full URL in settings.
            print("Warning: For absolute callback URLs, it's recommended to use django.contrib.sites.")
            print("Falling back to reversing the URL name. Ensure your webserver provides the host.")
            return reverse(self.callback_url_name)


    def initiate_stk_push(self, amount: int, phone_number: str, external_reference: str, customer_name: str = "Customer"):
        """
        Initiates an M-Pesa STK Push request.

        Args:
            amount (int): The amount to be paid.
            phone_number (str): The customer's phone number in 254... format.
            external_reference (str): A unique string to identify this transaction.
            customer_name (str): The customer's name.

        Returns:
            dict: The JSON response from the PayHero API.
        
        Raises:
            PayHeroAPIError: If the API call fails.
        """
        endpoint = f"{self.BASE_URL}/payments"
        
        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": self.channel_id,
            "provider": "m-pesa",
            "external_reference": external_reference,
            "customer_name": customer_name,
            "callback_url": self._get_full_callback_url(),
        }

        # Create a record in the database before making the API call
        PayHeroTransaction.objects.create(
            external_reference=external_reference,
            phone_number=phone_number,
            amount=amount,
            status=PayHeroTransaction.TransactionStatus.PENDING
        )

        try:
            response = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            
            return response.json()

        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            # You might want to update the transaction status to FAILED here
            transaction = PayHeroTransaction.objects.get(external_reference=external_reference)
            transaction.status = PayHeroTransaction.TransactionStatus.FAILED
            transaction.save()
            raise PayHeroAPIError(f"Network error while contacting PayHero: {e}")
        except Exception as e:
            transaction = PayHeroTransaction.objects.get(external_reference=external_reference)
            transaction.status = PayHeroTransaction.TransactionStatus.FAILED
            transaction.save()
            raise PayHeroAPIError(f"An unexpected error occurred: {e}")
