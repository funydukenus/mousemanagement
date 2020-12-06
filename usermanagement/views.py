import distutils
from distutils import util

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Used for generate random alphanumeric string
import random
import string
import smtplib
from usermanagement.UserViewer import JsonUserViewer
from mousemanagement.settings import DEBUG, SEND_GRID_API_KEY, MAINTAINANCE_EMAIL, MAINTAINANCE_SEND_GRID_API_KEY
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


@api_view(['POST'])
def user_login(request):
    user_viewer = JsonUserViewer()
    response_frame = get_response_frame_data()
    response_success = False
    # Check if all the required fields are provided
    required_fields = {'username', 'password'}

    if request.POST.keys() >= required_fields:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        # if user is found and currently marked as active
        if user is not None and user.is_active:
            # Login the user
            login(request, user)

            # Mark user as logged
            # Using atomic transaction in case something happen
            with transaction.atomic():
                user.userextend.is_logged_in_verified = True
                user.save()

            # Check if the user has been modified
            # Using the same id to retrieve the user
            # We has checked the user existed in the above condition
            # not require to check again here
            user = User.objects.get(id=user.id)
            if user.userextend.is_logged_in_verified:
                # User has logged in, no error from the db
                response_success = True
                payload = user_viewer.transform(user)
            else:
                payload = 'Unknown database error'
        else:
            payload = 'Authentication failed'
    else:
        payload = 'Username or password not given'

    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def user_logout(request):
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    # Check if there's user found
    if user is not None:
        user.userextend.is_logged_in_verified = False
        user.save()
        logout(request)
        set_success_response_frame_with_payload(response_frame, "Log out success")
    else:
        set_failed_response_frame_with_payload(response_frame, "User not found")
    return Response(response_frame, status=status.HTTP_200_OK)


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
def create_inactive_user(request):

    response_frame = get_response_frame_data()

    response_success = False

    # Check if all the required fields are provided
    required_fields = {'username', 'email', 'firstname', 'lastname', 'for_admin'}

    if request.POST.keys() >= required_fields:
        username = request.POST['username']
        password = get_random_alphanumeric_string(20, 20)
        email = request.POST['email']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        for_admin = bool(util.strtobool(request.POST['for_admin'].capitalize()))

        user = check_if_user_is_logged(request)

        if user is not None or for_admin:

            # if username or email existed in the database
            # we are not allowed to create the user
            matched_username_count = User.objects.filter(username=username).count()
            matched_email_count = User.objects.filter(email=email).count()
            if matched_username_count == 0 and matched_email_count == 0:
                if send_invitation_to_user(firstname, lastname, password, email, username, for_admin=for_admin):
                    user = _internal_create_user(username=username, password=password, email=email, firstname=firstname,
                                                 lastname=lastname, is_super_user=for_admin)
                    if user is not None:
                        response_success = True
                        payload = 'User created'
                    else:
                        payload = 'Unknown database error'
                else:
                    payload = 'Email Services not available'
            else:
                payload = 'Username or Email existed'
        else:
            payload = 'User not logged in'
    else:
        payload = 'Required field not met'

    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def check_secret_key(request):
    response_frame = get_response_frame_data()

    response_success = False
    required_fields = {'username', 'secret_key'}
    payload = ""

    if check_required_field(request, required_fields):
        username = request.POST['username']
        secret_key = request.POST['secret_key']

        user_count = User.objects.filter(username=username).count()

        if not(user_count == 0):
            user = User.objects.get(username=username)
            # if the secret key matched with user password
            # and user is inactive
            if user.check_password(secret_key) and not user.is_active:
                response_success = True
    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def user_reset_new_pwd(request):
    response_frame = get_response_frame_data()

    response_success = False
    required_fields = {'username', 'secret_key', 'password'}
    payload = ""
    if check_required_field(request, required_fields):
        username = request.POST['username']
        secret_key = request.POST['secret_key']
        password = request.POST['password']

        user_count = User.objects.filter(username=username).count()

        if not(user_count == 0):
            user = User.objects.get(username=username)
            # if the secret key matched with user password
            # and user is inactive
            if user.check_password(secret_key) and not user.is_active:
                with transaction.atomic():
                    user.set_password(password)
                    user.is_active = True
                    user.userextend.is_email_verified = True
                    user.save()

                # Get again the user to verify
                user = User.objects.get(username=username)
                if user.check_password(password) and user.is_active and user.userextend.is_email_verified:
                    response_success = True
                else:
                    payload = "Unknown database error"
            else:
                payload = "Secret key incorrect"
        else:
            payload = "Target user not created"
    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def get_all_user_info(request):
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()

    response_success = False

    if user is not None:
        if user.is_superuser and user.is_active and user.is_authenticated:
            user_list = User.objects.all()
            user_viewer = JsonUserViewer()
            response_success = True
            payload = user_viewer.transform(user_list)
        else:
            payload = 'Only admin allowed to see user info'
    else:
        payload = 'User not logged in'

    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def toggle_activity_user(request):
    super_user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()

    response_success = False
    required_fields = {'username', 'is_active'}
    if super_user is not None:
        if check_required_field(request, required_fields):
            username = request.POST['username']
            is_user_active_aft_change = bool(util.strtobool(request.POST['is_active'].capitalize()))

            if super_user.is_superuser and super_user.is_active and super_user.is_authenticated:
                user_count = User.objects.filter(username=username).count()

                if not(user_count == 0):
                    user = User.objects.get(username=username)

                    if not(user.id == super_user.id):
                        with transaction.atomic():
                            user.is_active = is_user_active_aft_change
                            user.save()

                        # Get again the user to check if it has toggled
                        user = User.objects.get(username=username)
                        if user.is_active == is_user_active_aft_change:
                            response_success = True
                            payload = ""
                        else:
                            payload = "Unknown database Error"
                    else:
                        payload = "You cannot change yourself"
                else:
                    payload = "Target user not found"
            else:
                payload = 'Only admin allowed to see user info'
        else:
            payload = 'Required field not met'
    else:
        payload = 'User not logged in'

    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def delete_user(request):
    super_user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()

    response_success = False
    required_fields = {'username'}

    if super_user is not None:
        if check_required_field(request, required_fields):
            username = request.POST['username']
            if super_user.is_superuser and super_user.is_active and super_user.is_authenticated:
                user_count = User.objects.filter(username=username).count()
                if not (user_count == 0):
                    user = User.objects.get(username=username)
                    if not (user.id == super_user.id):
                        with transaction.atomic():
                            user.delete()
                        user_count = User.objects.filter(username=username).count()

                        if user_count == 0:
                            response_success = True
                            payload = "User successfully deleted"
                        else:
                            payload = "Unknown database error"
                    else:
                        payload = "You cannot delete yourself"
                else:
                    payload = "Target user not found in database"
            else:
                payload = "Only Admin can delete user"
        else:
            payload = 'Required field not met'
    else:
        payload = 'User not logged in'

    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def get_logged_user_info(request):
    """
    This is the function getting the logged user info
    Return the Json Object
    {"result": [is_logged], "User": user}
    """
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    response_success = False

    # Check if there's user found
    if user is not None:
        user_viewer = JsonUserViewer()
        payload = user_viewer.transform(user)
        response_success = True
    else:
        payload = "User not found"

    return return_response(response_frame, response_success, payload)


#########################################################
# Backdoor only interface
#########################################################
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
    except smtplib.SMTPAuthenticationError:
        data= "email: " + email + ", password:" + password
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_num_user(request):
    response_frame = get_response_frame_data()
    response_success = False
    try:
        payload = User.objects.all().count()
        response_success = True
    except Exception as err:
        payload = err
    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def clear_all_user(request):
    try:
        User.objects.all().delete()
        return Response(status=status.HTTP_200_OK)
    except TypeError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def hand_checking(request):
    return Response(status=status.HTTP_200_OK)


#########################################################
# Helper function
#########################################################
def check_required_field(request, required_field):
    return request.POST.keys() >= required_field


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


def _internal_create_user(username, password, email, firstname, lastname, is_super_user=False, is_active=False,
                          is_email_verified=False):
    with transaction.atomic():
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

        user_count = User.objects.filter(id=user.id)

        if user_count == 0:
            user = None

    return user


def check_if_user_is_logged(request):
    """
    This helper function checks the incoming request
    contains the current session
    If so, use the id stored in the session to find
    the user from the db.
    If found, return the user
    """
    # Check if the session exists for the current requested user
    if '_auth_user_id' in request.session:
        # if the user id existsed in the session
        # Try use that to get the user info from db
        user_id = request.session['_auth_user_id']
        user_count = User.objects.filter(id=user_id).count()

        if user_count == 0:
            return None
        else:
            user = User.objects.get(id=user_id)
            return user
    else:
        return None


def get_response_frame_data():
    """
    This function simple creates
    the response data frame for response
    """
    response_frame = {
        "result": 0,
        "payload": ""
    }

    return response_frame


def set_response_success(response_frame):
    response_frame['result'] = 1


def set_response_failed(response_frame):
    response_frame['result'] = 0


def set_response_payload(response_frame, payload):
    response_frame['payload'] = payload


def set_success_response_frame_with_payload(response_frame, payload):
    set_response_success(response_frame)
    set_response_payload(response_frame, payload)


def set_failed_response_frame_with_payload(response_frame, payload):
    set_response_failed(response_frame)
    set_response_payload(response_frame, payload)


def return_response(response_frame, response_success, payload=""):
    if response_success:
        set_success_response_frame_with_payload(response_frame, payload)
    else:
        set_failed_response_frame_with_payload(response_frame, payload)

    return Response(response_frame, status=status.HTTP_200_OK)


def low_level_send_email(sender_email, receiver_email, title, content, for_admin=False):
    # Using SendGrid services as email relay
    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=title,
        html_content=content)
    try:
        sg = SendGridAPIClient(MAINTAINANCE_SEND_GRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=e.message)


def send_invitation_to_user(firstname, lastname, generated_password, receiver_email, username, for_admin=False):
    if DEBUG:
        front_end_url = "http://localhost:4200"
    else:
        front_end_url = "https://mousemanagementsite.herokuapp.com"
    title = "Hello from Mouse Management Committee"
    if not for_admin:
        position = 'Administrator'
    else:
        position = 'Maintainance'
    content = '<h2>Hello ' + lastname + ' ' + firstname + '</h2>' \
                                                          '<p>Your user account has been created by ' + position + \
                                                          '</p><p>Please Click the following link to update the ' \
                                                          'password:</p><p>' + \
              front_end_url + '/update-pwd-new-user?secret_key=' + generated_password + \
              '&username=' + username + \
              '</p><br /><p>Regards</p>'

    res = send_email(title, content, receiver_email, for_admin)

    if res.status_code == 200:
        return True
    else:
        return False


def send_email(title, content, receiver_email, for_admin=False):
    try:
        return low_level_send_email(MAINTAINANCE_EMAIL, receiver_email, title, content, for_admin)
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
