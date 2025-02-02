from django.urls import path
from .views import (
    HomeAPI, UserSignupAPI, UserLoginAPI, UserLogoutAPI, ProfileAPI,
    SendConfirmationAPI, ConfirmLoanAPI, ApproveLoanAPI, RejectLoanAPI,
    EditProfileAPI, TransactionAPI, PayForOthersAPIView, 
)

urlpatterns = [
    path('home/', HomeAPI.as_view(), name='home_api'),
    path('signup/', UserSignupAPI.as_view(), name='signup_api'),
    path('login/', UserLoginAPI.as_view(), name='login_api'),
    path('logout/', UserLogoutAPI.as_view(), name='logout_api'),
    path('profile/', ProfileAPI.as_view(), name='profile_api'),
    path('send_confirmation/', SendConfirmationAPI.as_view(), name='send_confirmation_api'),
    path('confirm_loan/', ConfirmLoanAPI.as_view(), name='confirm_loan_api'),
    path('approve_loan/<int:loan_confirm_id>/', ApproveLoanAPI.as_view(), name='approve_loan_api'),
    path('reject_loan/<int:loan_confirm_id>/', RejectLoanAPI.as_view(), name='reject_loan_api'),
    path('edit_profile/', EditProfileAPI.as_view(), name='edit_profile_api'),
    path('transaction/', TransactionAPI.as_view(), name='transaction_api'),
    path("pay/", PayForOthersAPIView.as_view(), name="pay_for_others_api"),
]