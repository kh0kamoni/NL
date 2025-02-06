from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from ledger.models import UserProfile, Transaction, Loan, LoanRequest, Notification
from .serializers import UserSerializer, UserProfileSerializer, TransactionSerializer, LoanSerializer, LoanRequestSerializer, PayForOthersSerializer, PaymentDetailSerializer, NotificationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication


class HomeAPI(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({"message": "User is authenticated"}, status=status.HTTP_200_OK)
        return Response({"message": "Welcome to the home page"}, status=status.HTTP_200_OK)

class UserSignupAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        full_name = request.data.get('fullName')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirmPassword')

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            first_name=full_name,
            email=email,
            password=password
        )
        UserProfile.objects.create(user=user)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "User registered and logged in successfully", "token": token.key}, status=status.HTTP_201_CREATED)

        return Response({"error": "Unable to register user"}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPI(APIView):
    def post(self, request):
        # Get username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in (this creates a session)
            login(request, user)
            
            # Generate or retrieve the token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # Return the token to the client
            return Response({
                "message": "User logged in successfully",
                "token": token.key  # Return the token key
            }, status=status.HTTP_200_OK)
        
        # If authentication fails, return an error response
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutAPI(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "User logged out successfully"}, status=status.HTTP_200_OK)

class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user)
        loans_given = Loan.objects.filter(lender=user)
        loans_received = Loan.objects.filter(borrower=user)
        pending_loan_count = LoanRequest.pending_count(user)
        unread_notifications = Notification.unread_count(user)

        total_loan_given = sum(loan.amount for loan in loans_given if loan.status == 'approved')
        total_loan_taken = sum(loan.amount for loan in loans_received if loan.status == 'approved')
        amount_due = sum(loan.amount for loan in loans_received if loan.status == 'approved')
        amount_receive = sum(loan.amount for loan in loans_given if loan.status == 'approved')

        user_serializer = UserSerializer(user)
        transactions_serializer = TransactionSerializer(transactions, many=True)
        loans_given_serializer = LoanSerializer(loans_given, many=True)
        loans_received_serializer = LoanSerializer(loans_received, many=True)

        return Response({
            'user': user_serializer.data,
            'transactions': transactions_serializer.data,
            'loans_given': loans_given_serializer.data,
            'loans_received': loans_received_serializer.data,
            'total_loan_given': total_loan_given,
            'total_loan_taken': total_loan_taken,
            'amount_due': amount_due,
            'amount_receive': amount_receive,
            'pending_loan_count': pending_loan_count,
            'unread_notifications': unread_notifications,
        }, status=status.HTTP_200_OK)

class SendConfirmationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        borrower_id = request.data.get("borrower_id")
        amount = request.data.get("amount")

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"error": "Amount must be a positive number"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        borrower = User.objects.filter(id=borrower_id).first()
        if not borrower:
            return Response({"error": "Borrower not found"}, status=status.HTTP_404_NOT_FOUND)

        if borrower == request.user:
            return Response({"error": "You cannot lend money to yourself"}, status=status.HTTP_400_BAD_REQUEST)

        LoanRequest.objects.create(
            lender=request.user,
            borrower=borrower,
            amount=amount,
            status="pending"
        )

        return Response({"message": f"Loan request sent to {borrower.username}"}, status=status.HTTP_201_CREATED)

class ConfirmLoanAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_requests = LoanRequest.objects.filter(borrower=request.user, status="pending")
        serializer = LoanRequestSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApproveLoanAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, loan_confirm_id):
        loan_request = LoanRequest.objects.filter(id=loan_confirm_id).first()
        if not loan_request:
            return Response({"error": "Loan request not found"}, status=status.HTTP_404_NOT_FOUND)

        if loan_request.borrower != request.user:
            return Response({"error": "You are not authorized to approve this loan"}, status=status.HTTP_403_FORBIDDEN)

        loan = Loan.objects.create(
            lender=loan_request.lender,
            borrower=loan_request.borrower,
            amount=loan_request.amount,
            status="approved",
        )
        loan.update_balance()
        loan_request.delete()

        return Response({"message": "Loan approved successfully"}, status=status.HTTP_200_OK)

class RejectLoanAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, loan_confirm_id):
        loan_request = LoanRequest.objects.filter(id=loan_confirm_id).first()
        if not loan_request:
            return Response({"error": "Loan request not found"}, status=status.HTTP_404_NOT_FOUND)

        if loan_request.borrower != request.user:
            return Response({"error": "You are not authorized to reject this loan"}, status=status.HTTP_403_FORBIDDEN)

        loan_request.delete()
        return Response({"message": "Loan request rejected"}, status=status.HTTP_200_OK)

class EditProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        profile_serializer = UserProfileSerializer(user.userprofile, data=request.data, partial=True)

        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

class TransactionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Transaction created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    



class PayForOthersAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    parser_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        """
        Handle the creation of a PayForOthers record.
        """
        serializer = PayForOthersSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

