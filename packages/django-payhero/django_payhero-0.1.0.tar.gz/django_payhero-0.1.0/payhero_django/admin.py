from django.contrib import admin
from .models import PayHeroTransaction

@admin.register(PayHeroTransaction)
class PayHeroTransactionAdmin(admin.ModelAdmin):
    list_display = ('external_reference', 'phone_number', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('external_reference', 'provider_reference', 'phone_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('external_reference', 'provider_reference', 'phone_number', 'amount', 'status')
        }),
        ('Audit Information', {
            'fields': ('callback_payload', 'created_at', 'updated_at'),
            'classes': ('collapse',)  
        }),
    )