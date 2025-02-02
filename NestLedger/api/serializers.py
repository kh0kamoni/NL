from rest_framework import serializers
from django.contrib.auth.models import User
from ledger.models import UserProfile, Transaction, Loan, LoanRequest, PaymentDetail, PayForOthers, Notification
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequest
        fields = '__all__'




class PaymentDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = PaymentDetail
        fields = ['user', 'amount']


class PayForOthersSerializer(serializers.ModelSerializer):
    payment_details = PaymentDetailSerializer(many=True)

    class Meta:
        model = PayForOthers
        fields = ['payer', 'total_amount', 'description', 'split_equally', 'payment_details']

    def validate(self, data):
        """
        Validate that the total amount matches the sum of individual amounts if not split equally.
        """
        total_amount = data.get('total_amount')
        payment_details = data.get('payment_details')
        split_equally = data.get('split_equally')

        if not split_equally:
            sum_of_amounts = sum(detail['amount'] for detail in payment_details)
            if sum_of_amounts != total_amount:
                raise serializers.ValidationError(
                    "The sum of individual amounts does not match the total amount."
                )
        return data

    def create(self, validated_data):
        """
        Create PayForOthers and PaymentDetail instances.
        Also, create notifications for users who are being paid for.
        """
        payment_details_data = validated_data.pop('payment_details')
        payer = validated_data.pop('payer')
        total_amount = validated_data.get('total_amount')
        split_equally = validated_data.get('split_equally')

        # Create the main payment record
        payment = PayForOthers.objects.create(payer=payer, **validated_data)

        # Calculate amounts for each user
        if split_equally:
            user_count = len(payment_details_data)
            amount_per_user = total_amount / user_count
            for detail_data in payment_details_data:
                user = detail_data['user']
                PaymentDetail.objects.create(payment=payment, user=user, amount=amount_per_user)
                # Create a notification for the user
                Notification.objects.create(
                    user=user,
                    message=f"{payer.username} paid {amount_per_user} for you."
                )
        else:
            for detail_data in payment_details_data:
                user = detail_data['user']
                amount = detail_data['amount']
                PaymentDetail.objects.create(payment=payment, user=user, amount=amount)
                # Create a notification for the user
                Notification.objects.create(
                    user=user,
                    message=f"{payer.username} paid {amount} for you."
                )

        return payment


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"