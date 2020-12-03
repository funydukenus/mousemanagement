from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Used for generate random alphanumeric string
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from usermanagement.UserViewer import JsonUserViewer
from mousemanagement.settings import DEBUG, SEND_GRID_API_KEY

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


@api_view(['POST'])
def user_login(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            try:
                user = User.objects.get(id=user.id)
                user.userextend.is_logged_in_verified = True
                user.save()
                user_viewer = JsonUserViewer()

                return Response(user_viewer.transform(user), status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response(data="User not found", status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_logout(request):
    try:
        user_id = request.session['_auth_user_id']
        user = User.objects.get(id=user_id)
        user.userextend.is_logged_in_verified = False
        user.save()
        logout(request)
        return Response(status=status.HTTP_200_OK)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def user_create(request):
    # First check if the user has login into the system
    try:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        try:
            User.objects.get(username=username)
            return Response(status=status.HTTP_302_FOUND)
        except User.DoesNotExist:
            # if user is not exist, we are allow to
            # create the user
            _internal_create_user(
                username=username,
                password=password,
                email=email,
                firstname = firstname,
                lastname = lastname
            )
            return Response(status=status.HTTP_201_CREATED)

    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_change_password(request):
    # First check if the user has login into the system
    try:
        username = request.POST['username']
        password = request.POST['password']

        # if the current session of the connection not belongs to the
        # user of the client currently attempting to change the password
        # return 404 unauthorized back to client
        if request.session['username'] != username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.get(username=request.session['username'])

        # check if the current user is staff and is currently active and login
        if user.is_authenticated and user.is_active and user.is_staff:
            # if authentication passed, change the password for the user
            try:
                # Put the external password function here in case we need it in future
                user.set_password(password)
                user.save()
                return Response(status=status.HTTP_200_OK)
            except KeyError:
                # Key error happened when using hash to set the password
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def is_user_table_empty(request):
    try:
        num = User.objects.all().count()
        if num == 0:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_302_FOUND)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_super_user(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']

        secret_key = request.POST['secret_key']

        if not verify_super_user_email(email, password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if secret_key == 'LAB_AADDGGE':
            _internal_create_user(
                username=username,
                password=password,
                email=email,
                firstname=firstname,
                lastname=lastname,
                is_super_user=True,
                is_active=True,
                is_email_verified=True
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def _internal_create_user(username, password, email, firstname, lastname, is_super_user=False, is_active=False, is_email_verified=False):
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=firstname,
        last_name=lastname
    )
    user.is_staff = True
    user.is_active = is_active
    user.is_admin = is_super_user
    user.is_superuser = is_super_user
    user.userextend.is_email_verified = is_email_verified
    user.save()

    return user


@api_view(['GET'])
def hand_checking(request):
    return Response(status=status.HTTP_200_OK)


def _check_if_user_is_login(username):
    """
    Check if the user has logged in
    """
    try:
        user = User.objects.get(username=username)
        if user.is_active and user.is_authenticated and user.is_staff:
            return True
        else:
            return False
    except User.DoesNotExist:
        return False
    except KeyError:
        return False


@api_view(['POST'])
def is_login(request):
    try:
        user_id = request.session['_auth_user_id']
        user = User.objects.get(id=user_id)
        if user.is_authenticated and user.userextend.is_logged_in_verified:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        key_str = ""
        for k in request.session.keys():
            key_str += " " + k
        return Response(data=key_str, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def is_admin(request):
    try:
        user_id = request.session['_auth_user_id']
        user = User.objects.get(id=user_id)
        if user.is_authenticated and user.is_superuser:
            return Response(data="1", status=status.HTTP_200_OK)
        else:
            return Response(data="0", status=status.HTTP_200_OK)
    except KeyError:
        return Response(data="0", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def clear_all_user(request):
    try:
        User.objects.all().delete()
        return Response(status=status.HTTP_200_OK)
    except TypeError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def get_random_alphanumeric_string(letters_count, digits_count):
    """
    Generate random number based on the letters count and digits count
    """
    sample_str = ''.join((random.choice(string.ascii_letters) for _ in range(letters_count)))
    sample_str += ''.join((random.choice(string.digits) for _ in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string


def verify_super_user_email(email, password):
    # if email failed try the below 2,
    # 1. You need to allow less secure apps, you can do it by click below link
    #    https://www.google.com/settings/security/lesssecureapps
    # 2. https://accounts.google.com/DisplayUnlockCaptcha
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(email, password)  # login with mail_id and password
    session.quit()
    return True


def low_level_send_email(sender_email, receiver_email, title, content):

    # Using SendGrid services as email relay
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=title,
        html_content=content)
    try:
        sg = SendGridAPIClient(SEND_GRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=e.message)
    # We will not using gmail services
    # message = MIMEMultipart()
    # message['From'] = sender_email
    # message['To'] = receiver_email
    # message['Subject'] = title  # The subject line
    # # The body and the attachments for the mail
    # message.attach(MIMEText(content, 'plain'))
    # # Create SMTP session for sending the mail
    # session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    # session.starttls()  # enable security
    # session.login(sender_email, password)  # login with mail_id and password
    # text = message.as_string()
    # session.sendmail(sender_email, receiver_email, text)
    # session.quit()

@api_view(['POST'])
def email_test(request):
    title = request.POST['title']
    content = request.POST['content']
    receiver_email = "chenyuhang01@gmail.com"

    message = Mail(
        from_email='fny.duke.nus@gmail.com',
        to_emails=receiver_email,
        subject=title,
        html_content=content)
    try:
        sg = SendGridAPIClient(SEND_GRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=e.message)

    # return send_email(title, content, password, receiver_email)


def send_invitation_to_user(firstname, lastname, generated_password, receiver_email, username):
    if DEBUG:
        front_end_url = "http://localhost:4200"
    else:
        front_end_url = "https://mousemanagementsite.herokuapp.com"
    title = "Hello from Mouse Management Committee"
    content = 'Hello ' + lastname + ' ' + firstname +\
              '\nYour user account has been created by Admin\n'\
              'Please Click the following link to update the password:\n' +\
              front_end_url + '/update-pwd-new-user?secret_key=' + generated_password + \
              '&username=' + username + \
              '\n\n\nRegards'

    res = send_email(title, content, receiver_email)

    if res.status_code == 200:
        return True
    else:
        return False


def send_email(title, content, receiver_email):
    try:
        superusers = User.objects.get(is_superuser=True)
        return low_level_send_email(superusers.email, receiver_email, title, content)
    except smtplib.SMTPHeloError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except smtplib.SMTPRecipientsRefused:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except smtplib.SMTPSenderRefused:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except smtplib.SMTPDataError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except smtplib.SMTPNotSupportedError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_inactive_user(request):
    try:
        username = request.POST['username']
        # Generate a random default password for the user
        password = get_random_alphanumeric_string(20, 20)
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']

        try:
            User.objects.get(username=username)
            return Response(status=status.HTTP_302_FOUND)
        except User.DoesNotExist:
            if send_invitation_to_user(firstname, lastname, password, email, username):
                # if user is not exist, we are allow to
                # create the user
                _internal_create_user(
                    username=username,
                    password=password,
                    email=email,
                    firstname=firstname,
                    lastname=lastname
                )
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_secret_key(request):
    try:
        username = request.POST['username']
        secret_key = request.POST['secret_key']
        try:
            user = User.objects.get(username=username)
            if not user.check_password(secret_key) or user.is_active:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_reset_new_pwd(request):
    try:
        username = request.POST['username']
        secret_key = request.POST['secret_key']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if not (user.check_password(secret_key) or user.is_active):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.is_active = True
            user.userextend.is_email_verified = True
            user.save()

            return Response(status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_user_info(request):
    try:
        user_id = request.session['_auth_user_id']
        try:
            user = User.objects.get(id=user_id)

            if user.is_superuser and user.is_active and user.is_authenticated:
                user_list = User.objects.all()
                user_viewer = JsonUserViewer()

                return Response(user_viewer.transform(user_list))
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def toggle_activity_user(request):
    try:
        user_id = request.session['_auth_user_id']
        username = request.POST['username']
        is_user_active_aft_change = request.POST['is_active']

        if is_user_active_aft_change == 'false':
            is_user_active_aft_change = False
        else:
            is_user_active_aft_change = True

        try:
            super_user = User.objects.get(id=user_id)

            if super_user.is_superuser and super_user.is_active and super_user.is_authenticated:
                user = User.objects.get(username=username)

                # Only can toggle the user with email verified
                if not(user.id == super_user.id and user.userextend.is_email_verified):
                    user.is_active = is_user_active_aft_change
                    user.save()
                    return Response(data="Success", status=status.HTTP_200_OK)
                else:
                    return Response(data="You cannot change yourself", status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_user(request):
    try:
        user_id = request.session['_auth_user_id']
        username = request.POST['username']

        try:
            super_user = User.objects.get(id=user_id)

            if super_user.is_superuser and super_user.is_active and super_user.is_authenticated:
                user = User.objects.get(username=username)

                # Only can toggle the user with email verified
                if not(user.id == super_user.id):
                    user.delete()
                    return Response(data="Success", status=status.HTTP_200_OK)
                else:
                    return Response(data="You cannot delete yourself", status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_logged_user_info(request):
    try:
        user_id = request.session['_auth_user_id']
        try:
            user = User.objects.get(id=user_id)
            user_viewer = JsonUserViewer()

            return Response(user_viewer.transform(user), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(data="User not found", status=status.HTTP_200_OK)
    except KeyError:
        return Response(data="Not logged",status=status.HTTP_200_OK)