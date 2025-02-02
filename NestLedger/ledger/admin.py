from django.contrib import admin
from .models import UserProfile, Transaction, Loan, LoanRequest, Notification, PayForOthers, PaymentDetail

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Transaction)
admin.site.register(Loan)
admin.site.register(LoanRequest)
admin.site.register(Notification)
admin.site.register(PayForOthers)
admin.site.register(PaymentDetail)