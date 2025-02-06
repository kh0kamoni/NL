from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Transaction
from django.forms import formset_factory

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['balance']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'payment_method', 'transaction_type']





class PayForOthersForm(forms.Form):
    total_amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Total Amount")
    description = forms.CharField(required=False, widget=forms.Textarea, label="Description")
    split_equally = forms.BooleanField(required=False, label="Split equally among users")

class UserAmountForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount", required=False)
    deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

UserAmountFormSet = formset_factory(UserAmountForm, extra=1)