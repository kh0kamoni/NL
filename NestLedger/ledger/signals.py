from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PaymentDetail, Notification,Transaction, UserProfile

@receiver(post_save, sender=PaymentDetail)
def send_payment_notification(sender, instance, created, **kwargs):
    if created:
        message = f"{instance.payment.payer.username} paid {instance.amount} for you."
        Notification.objects.create(user=instance.user, message=message)


@receiver(post_save, sender=Transaction)
def update_balance_on_transaction(sender, instance, created, **kwargs):
    """Update user balance when a transaction is created."""
    if created:
        profile = instance.user.userprofile
        if instance.transaction_type == 'expense':
            profile.balance -= instance.amount
        else:  # 'income'
            profile.balance += instance.amount
        profile.save()

@receiver(post_delete, sender=Transaction)
def adjust_balance_on_transaction_delete(sender, instance, **kwargs):
    """Recalculate balance if a transaction is deleted."""
    profile = instance.user.userprofile
    if instance.transaction_type == 'expense':
        profile.balance += instance.amount
    else:  # 'income'
        profile.balance -= instance.amount
    profile.save()
