from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.user_signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path('send_confirmation/', views.send_confirmation, name='send_confirmation'),
    path('confirm_loan/', views.confirm_loan, name='confirm_loan'),
    path('approve-loan/<int:loan_confirm_id>/', views.approve_loan, name='approve_loan'),
    path('reject-loan/<int:loan_confirm_id>/', views.reject_loan, name='reject_loan'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path("transaction/", views.transaction, name="transaction"),
    path("transactions_list/", views.view_transactions, name="transactions_list"),


    # URL for the "Pay for Others" form
    path('pay/', views.pay_for_others, name='pay_for_others'),
    path("repay/<int:lid>/", views.repay, name="repay"),

    # URL for the payment success page
    path('payment-success/', views.payment_success, name='payment_success'),

    # URL for viewing notifications
    path('notifications/', views.view_notifications, name='view_notifications'),
    path("notification_mark_as_read/", views.mark_all_notifications_read, name="mark_read"),
    path("mark_as_read/<int:id>/", views.mark_notification_read, name="mark_as_read"),
    # path("notification_details/", views.notification_details, name="notification_details"),
    path("delete_notification/<int:nid>/", views.delete_notification, name="delete"),


     # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]


