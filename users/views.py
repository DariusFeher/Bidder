from lib2to3.pgen2.tokenize import generate_tokens

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_str, force_text)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from sqlparse import tokens

from .forms import (CreateUserForm, LoginUserForm,
                    RequestActivationLinkOrPassword, ResetPasswordForm)
from .models import Account
from .utils import generate_token


def send_activation_email(request, user):
    current_site = get_current_site(request)
    email_subject = _('Please activate your account!')
    email_body = render_to_string('accounts/activate.html', {
        'user': user.username,
        'domain': str(current_site).rstrip("/"),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    email = EmailMessage(subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_FROM_USER,
                to=[user.email])
    email.send()

def send_reset_password_email(request, user):
    current_site = get_current_site(request)
    email_subject = _('Password reset for user ') + user.username
    email_body = render_to_string('accounts/password_reset_email.html', {
        'user': user.username,
        'domain': str(current_site).rstrip("/"),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    email = EmailMessage(subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_FROM_USER,
                to=[user.email])
    email.send()

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            form.save()
            user = Account.objects.get(username=username)
            send_activation_email(request, user)
            messages.success(request, username + _(', please verify your email and activate your account!'))
            return redirect('login')
        else:
            form.add_error(NON_FIELD_ERRORS, _("Something went wrong..."))
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = LoginUserForm()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password1')
        user = authenticate(request, username=username, password=password)
        if user and not user.is_email_verified:
            messages.error(request, _('Email is not verified. Please verify your email. Email not received? Check spam or '))
            context = {'form': form}
            return render(request, 'accounts/login.html', context)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, _('Incorrect Username or Password!'))
    context = {'form': form}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, _("You have successfully signed out!"))
    return redirect('login')

def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except Exception as e:
        user = None
    
    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, _('Email verified, you can now login!'))
        return redirect('login')
    if user and user.is_email_verified:
        messages.success(request, _('Email is already verified!'))
    else:
        messages.error(request, _('Something unexpected happened.\n'))
    return redirect('login')

def get_new_activation_link(request):
    form = RequestActivationLinkOrPassword()
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
        except Exception as e:
            user = None
        if user is not None:
            send_activation_email(request, user)
        messages.success(request, _('You will receive a new activation link if there is an account associated with this email.'))
        return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/resend_activation.html', context)

def request_reset_password(request):
    form = RequestActivationLinkOrPassword()
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
        except Exception as e:
            user = None
        if user is not None:
            send_reset_password_email(request, user)
        messages.success(request, _('You will receive a link to reset your password if there is an account associated with this email.'))
        return redirect('request_new_password')
    context = {'form': form}
    return render(request, 'accounts/reset_password_request.html', context)

def reset_password(request, uidb64, token):
    if request.method == "POST":
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user and generate_token.check_token(user, token):
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            form = ResetPasswordForm(data=request.POST, user=user)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Password changed, you can now login!'))
                return redirect('login')
            else:
                messages.error(request, _('Something went wrong.'))
        else:
            messages.error(request, _('Something unexpected happened.'))
    else:
        form = ResetPasswordForm(user=request.user)
    context = {'form': form}
    return render(request, 'accounts/reset_password_confirm.html', context)
    