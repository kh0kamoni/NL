from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username
    



class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('utility', 'Utility Bill'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile', 'Mobile Banking'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
    ]
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, default='expense')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.amount} by {self.payment_method} for {self.category}"
    


class Loan(models.Model):
    lender = models.ForeignKey(User, related_name='loans_given', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, related_name='loans_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.borrower} took loan of {self.amount} from {self.lender}"

    def update_balance(self):
        if self.status == 'approved':
            lender_profile = self.lender.userprofile
            borrower_profile = self.borrower.userprofile

            # Lender gives money, so their balance decreases
            lender_profile.balance += self.amount
            # Borrower receives money, so their balance increases
            borrower_profile.balance -= self.amount

            lender_profile.save()
            borrower_profile.save()

    def mark_paid(self):
        if self.status == 'approved':
            lender_profile = self.lender.userprofile
            borrower_profile = self.borrower.userprofile

            # Borrower repays money, so their balance decreases
            borrower_profile.balance -= self.amount
            # Lender receives money, so their balance increases
            lender_profile.balance += self.amount

            lender_profile.save()
            borrower_profile.save()

            self.status = 'paid'
            self.save()




class LoanRequest(models.Model):
    lender = models.ForeignKey(User, related_name='loan_requests_sent', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, related_name='loan_requests_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan Request: {self.lender} → {self.borrower} ({self.amount})"

    @staticmethod
    def pending_count(user):
        return LoanRequest.objects.filter(borrower=user, status='pending').count()
    


class PayForOthers(models.Model):
    payer = models.ForeignKey(User, related_name="paid_by", on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
    description = models.TextField(blank=True, null=True)  # Optional description
    timestamp = models.DateTimeField(auto_now_add=True)  # When the payment was made

    def __str__(self):
        return f"{self.payer.username} paid {self.total_amount} for others"
    


class PaymentDetail(models.Model):
    payment = models.ForeignKey('PayForOthers', related_name='details', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='payment_details', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid for this user

    def __str__(self):
        return f"{self.payment.payer.username} paid {self.amount} for {self.user.username}"
    


class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    @staticmethod
    def unread_count(user):
        return Notification.objects.filter(user=user, is_read=False).count()
    

    




# class Payments(models.Model):
#     payer = models.ForeignKey(User, related_name="paidd_by", on_delete=models.CASCADE)
#     paid_for = models.ForeignKey(User, related_name="paid_for", on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
    

