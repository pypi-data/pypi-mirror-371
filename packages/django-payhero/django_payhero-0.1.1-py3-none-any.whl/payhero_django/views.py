
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import PayHeroTransaction

@csrf_exempt
@require_POST
def payhero_callback_view(request):
    """
    Handles the callback POST request from PayHero.
    Updates the status of the corresponding transaction.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload.'}, status=400)

    external_ref = data.get('reference') or data.get('user_reference')
    is_success = data.get('paymentSuccess', False)
    provider_ref = data.get('providerReference')

    if not external_ref:
        return JsonResponse({'status': 'error', 'message': 'Reference not found in payload.'}, status=400)

    try:
        # Find the transaction in our database
        transaction = PayHeroTransaction.objects.get(external_reference=external_ref)

        # Update transaction details
        transaction.provider_reference = provider_ref
        transaction.callback_payload = data
        
        if is_success:
            transaction.status = PayHeroTransaction.TransactionStatus.SUCCESS
        else:
            transaction.status = PayHeroTransaction.TransactionStatus.FAILED
        
        transaction.save()

        # You can add post-payment logic here, like sending a signal or a task
        # e.g., fulfill_order(transaction.id)

        return JsonResponse({'status': 'success', 'message': 'Callback processed.'})

    except PayHeroTransaction.DoesNotExist:
        # This might happen if PayHero sends a callback for a transaction we don't know about
        return JsonResponse({'status': 'error', 'message': 'Transaction not found.'}, status=404)
    except Exception as e:
        # Catch other potential errors during processing
        return JsonResponse({'status': 'error', 'message': f'An internal error occurred: {str(e)}'}, status=500)
