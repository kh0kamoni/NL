from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentDetail, Notification

@receiver(post_save, sender=PaymentDetail)
def send_payment_notification(sender, instance, created, **kwargs):
    if created:
        message = f"{instance.payment.payer.username} paid {instance.amount} for you."
        Notification.objects.create(user=instance.user, message=message)