from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
from .models import Loan, Notification, User

@shared_task
def check_approved_loans():
    """Check all approved loans and send notifications if overdue."""
    today = now().date()
    
    # Fetch all loans that are approved and overdue
    overdue_loans = Loan.objects.filter(deadline__isnull=False, deadline__lte=today, status="approved")

    for loan in overdue_loans:
        borrower = loan.borrower
        days_overdue = (today - loan.deadline).days

        if days_overdue == 0:
            Notification.objects.create(
                user=borrower,
                message=f"Your loan of {loan.amount} to ({loan.lender.first_name}) is due today! Please repay."
            )
        elif days_overdue == 3:
            Notification.objects.create(
                user=borrower,
                message=f"Reminder: Your loan of {loan.amount} to ({loan.lender.first_name}) is overdue for 3 days. Please pay immediately!"
            )
        elif days_overdue == 4:
            Notification.objects.create(
                user=borrower,
                message=f"Final Warning: Your loan of {loan.amount} to ({loan.lender.first_name}) is overdue for 4 days. Failure to pay will restrict further loans."
            )
        elif days_overdue >= 5:
            borrower.is_restricted = True
            borrower.save()
            Notification.objects.create(
                user=borrower,
                message="You have been restricted from taking further loans due to non-payment."
            )
