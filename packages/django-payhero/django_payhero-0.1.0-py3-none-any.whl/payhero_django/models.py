
from django.db import models
import uuid

class PayHeroTransaction(models.Model):
    """
    Model to store details of a transaction initiated with PayHero.
    """
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    # Our internal unique ID for the transaction
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The unique reference we send to PayHero
    external_reference = models.CharField(max_length=255, unique=True, db_index=True)
    
    # The reference ID returned by PayHero
    provider_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=10,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        db_index=True
    )
    
    # Full callback payload from PayHero for auditing
    callback_payload = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.external_reference} for {self.amount} KES [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "PayHero Transaction"
        verbose_name_plural = "PayHero Transactions"