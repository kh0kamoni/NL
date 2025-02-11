from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PaymentDetail, Notification,Transaction, UserProfile, Loan, LoanRequest, User
from django.utils.timezone import now
from datetime import timedelta


@receiver(post_save, sender=PaymentDetail)
def send_payment_notification(sender, instance, created, **kwargs):
    if created:
        # Check if the loan_request is present
        loan_request = instance.loan_request
        if loan_request and loan_request.deadline != None:
            message = f"{instance.payment.payer.first_name} paid {instance.amount} for you. Pay back within {loan_request.deadline}"
        else:
            message = f"{instance.payment.payer.first_name} paid {instance.amount} for you."
        
        # Create the notification for the user
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



@receiver(post_save, sender=Loan)
def update_balance_on_loan(sender, instance, **kwargs):
    lender = instance.lender.userprofile
    borrower = instance.borrower.userprofile

    if instance.status == "approved":
        lender.balance -= instance.amount
        borrower.balance += instance.amount
    elif instance.status == "paid":
        lender.balance += instance.amount
        borrower.balance -= instance.amount
    lender.save()
    borrower.save()











@receiver(post_save, sender=Loan)
def check_overdue_loans(sender, instance, created, **kwargs):
    """ Sends warnings if loan is overdue and restricts borrower if unpaid. """

    borrower = instance.borrower
    deadline = instance.deadline

    if not deadline:
        return  # No deadline, no need for warnings

    today = now().date()

    # First warning (on deadline day)
    if today >= deadline:
        Notification.objects.create(
            user=borrower,
            message=f"Your loan of {instance.amount} to ({instance.lender.first_name}) is due today! Please repay."
        )

    # Second warning (3 days later)
    if today >= deadline + timedelta(days=3):
        Notification.objects.create(
            user=borrower,
            message=f"Reminder: Your loan of {instance.amount} to ({instance.lender.first_name}) is overdue for 3 days. Please pay immediately!"
        )

    # Final warning (1 day after second warning)
    if today >= deadline + timedelta(days=4):
        Notification.objects.create(
            user=borrower,
            message=f"Final Warning: Your loan of {instance.amount} to ({instance.lender.first_name}) is overdue for 4 days. Failure to pay will restrict further loans."
        )

    # Restrict borrower from taking more loans (if 5 days overdue)
    if today >= deadline + timedelta(days=5):
        borrower.is_restricted = True
        borrower.save()
        Notification.objects.create(
            user=borrower,
            message="You have been restricted from taking further loans due to non-payment."
        )



