from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Transaction, Loan, LoanRequest, PayForOthers, PaymentDetail, Notification
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, TransactionForm, PayForOthersForm, UserAmountFormSet, UserAmountForm
from django.forms import formset_factory




# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("profile")
    return render(request, "ledger/home.html")




def user_signup(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        # Validation checks
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')

        # Create user with first_name as full name
        user = User.objects.create_user(
            username=username,
            first_name=full_name,
            email=email,
            password=password
        )
        UserProfile.objects.create(user=user)

        # Auto-login after registration
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  # Replace with your success URL

        return redirect('login')

    return render(request, 'ledger/signup.html')



@login_required
def profile(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    loans_given = Loan.objects.filter(lender=user)
    loans_received = Loan.objects.filter(borrower=user)
    pending_loan_count = LoanRequest.pending_count(user)
    unread_notifications = Notification.unread_count(user)
    
    # Total loan calculations (only for approved loans)
    total_loan_given = sum(loan.amount for loan in loans_given if loan.status == 'approved')
    total_loan_taken = sum(loan.amount for loan in loans_received if loan.status == 'approved')

    # Calculate amount due and to be received (only for approved loans)
    amount_due = sum(loan.amount for loan in loans_received if loan.status == 'approved')
    amount_receive = sum(loan.amount for loan in loans_given if loan.status == 'approved')

    return render(request, 'ledger/profile.html', {
        'user': user,
        'transactions': transactions,
        'loans_given': loans_given,
        'loans_received': loans_received,
        'total_loan_given': total_loan_given,
        'total_loan_taken': total_loan_taken,
        'amount_due': amount_due,
        'amount_receive': amount_receive,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })



# Login View
def user_login(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get("remember_me")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)

            return redirect('profile')
        else:
            messages.error(request, "Invalid Credentials")
    return render(request, 'ledger/login.html')

# Logout View
def user_logout(request):
    request.session.flush()
    logout(request)
    return redirect('home')

@login_required
def send_confirmation(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)

    if request.method == "POST":
        borrower_id = request.POST.get("borrower_id")
        amount = request.POST.get("amount")
        deadline = request.POST.get("deadline")


        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be a positive number.")
                return redirect("send_confirmation")
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect("send_confirmation")

        borrower = get_object_or_404(User, id=borrower_id)

        if borrower == request.user:
            messages.error(request, "You cannot lend money to yourself!")
            return redirect("profile")

        # Create a pending loan request
        LoanRequest.objects.create(
            lender=request.user,
            borrower=borrower,
            amount=amount,
            status="pending",
            deadline = deadline,
        )

        messages.success(request, f"Loan request sent to {borrower.username}!")
        return redirect("profile")

    users = User.objects.exclude(id=request.user.id)  # Exclude self
    return render(request, "ledger/send_confirmation.html", {
        "users": users,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
        })


@login_required
def confirm_loan(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    pending_requests = LoanRequest.objects.filter(borrower=request.user, status="pending")
    return render(request, "ledger/confirm_loan.html", {
        "pending_requests": pending_requests,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
        })



@login_required
def approve_loan(request, loan_confirm_id):
    loan_request = get_object_or_404(LoanRequest, id=loan_confirm_id)

    if loan_request.borrower != request.user:
        messages.error(request, "You are not authorized to approve this loan.")
        return redirect("profile")

    # Create the confirmed Loan object
    loan = Loan.objects.create(
        lender=loan_request.lender,
        borrower=loan_request.borrower,
        amount=loan_request.amount,
        status="approved",
        deadline = loan_request.deadline,
    )
    # loan.save()
    # Update balances
    # loan.update_balance()

    # Delete the loan request
    loan_request.delete()

    messages.success(request, "Loan approved successfully!")
    return redirect("confirm_loan")


@login_required
def reject_loan(request, loan_confirm_id):
    loan_request = get_object_or_404(LoanRequest, id=loan_confirm_id)

    if loan_request.borrower != request.user:
        messages.error(request, "You are not authorized to reject this loan.")
        return redirect("profile")

    loan_request.delete()

    messages.error(request, "Loan request rejected.")
    return redirect("confirm_loan")

@login_required
def edit_profile(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('edit_profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

    return render(request, 'ledger/edit_profile.html', {
        'user_form': user_form, 'profile_form': profile_form,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
        })



@login_required
def transaction(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    if request.method == "POST":
        transaction_form = TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction = transaction_form.save(commit=False)
            transaction.user = request.user  # Assign the logged-in user
            transaction.save() 
            messages.success(request, "Transaction created successfully!")
            return redirect("transaction")
        else:
            messages.error(request, "Something went wrong. Please try again")
    transaction_form = TransactionForm()
    return render(request, "ledger/transaction.html", {
        "transaction_form": transaction_form,
        "request": request,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })




@login_required
def pay_for_others(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    UserAmountFormSet = formset_factory(UserAmountForm, extra=1)  # Allow adding multiple users

    if request.method == 'POST':
        pay_form = PayForOthersForm(request.POST)
        user_amount_formset = UserAmountFormSet(request.POST)

        if pay_form.is_valid() and user_amount_formset.is_valid():
            total_amount = pay_form.cleaned_data['total_amount']
            split_equally = pay_form.cleaned_data['split_equally']
            description = pay_form.cleaned_data['description']

            # Create the main payment record
            payment = PayForOthers.objects.create(
                payer=request.user,
                total_amount=total_amount,
                description=description
            )

            # Calculate amounts for each user
            if split_equally:
                # Split the total amount equally among selected users
                user_count = len(user_amount_formset)  # Number of users
                amount_per_user = total_amount / user_count

                for form in user_amount_formset:
                    user = form.cleaned_data.get('user')
                    payer = request.user
                    deadline = form.cleaned_data.get('deadline')  # ✅ Handle optional deadline
                    if user:  # Ensure a user is selected
                        loan_request = LoanRequest.objects.create(
                            lender=payer,
                            borrower=user,
                            amount=amount_per_user,
                            status="pending",
                            deadline=deadline,  # Can be None if not provided
                        )
                        PaymentDetail.objects.create(
                            payment=payment,
                            user=user,
                            amount=amount_per_user,
                            loan_request = loan_request,
                        )

            else:
                # Use custom amounts for each user
                for form in user_amount_formset:
                    payer = request.user
                    user = form.cleaned_data.get('user')
                    amount = form.cleaned_data.get('amount')
                    deadline = form.cleaned_data.get('deadline')  # ✅ Handle optional deadline
                    if user and amount:  # Ensure both user and amount are provided
                        PaymentDetail.objects.create(
                            payment=payment,
                            user=user,
                            amount=amount
                        )
                        LoanRequest.objects.create(
                            lender=payer,
                            borrower=user,
                            amount=amount,
                            status="pending",
                            deadline=deadline,  # Can be None if not provided
                        )

            return redirect('payment_success')  # Redirect to a success page
    else:
        pay_form = PayForOthersForm()
        user_amount_formset = UserAmountFormSet()

    return render(request, 'ledger/pay_for_others.html', {
        'pay_form': pay_form,
        'user_amount_formset': user_amount_formset,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })




@login_required
def payment_success(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    return render(request, 'ledger/payment_success.html', {
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })



@login_required
def view_notifications(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    notifications = request.user.notifications.order_by('-timestamp')
    return render(request, 'ledger/notifications.html', {
        'notifications': notifications,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
        })


@login_required
def mark_notification_read(request, id):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, "ledger/notification_details.html", {
        "notification": notification,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })



@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('view_notifications')


@login_required
def delete_notification(request, nid):
    notification = get_object_or_404(Notification, id=nid, user=request.user)
    notification.delete()
    return redirect("view_notifications")



@login_required
def view_transactions(request):
    pending_loan_count = LoanRequest.pending_count(request.user)
    unread_notifications = Notification.unread_count(request.user)
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    total_income = sum(transaction.amount for transaction in transactions if transaction.transaction_type == "income")
    total_expense = sum(transaction.amount for transaction in transactions if transaction.transaction_type == "expense")

    return render(request, "ledger/view_transactions.html", {
        "transactions": transactions,
        "total_income": total_income,
        "total_expense": total_expense,
        "pending_loan_count": pending_loan_count,
        "unread_notifications": unread_notifications,
    })





@login_required
def repay(request, lid):
    user = request.user
    loan = get_object_or_404(Loan, id=lid)
    if loan.borrower != user:
        messages.error(request, "You're not authorized for this action.")
    loan.status = "paid"
    loan.save()
    messages.success(request, "Loan paid successfully.")
    return redirect("profile")









