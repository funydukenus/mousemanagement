from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['POST'])
def user_login(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_logout(request):
    logout(request)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def user_create(request):
    # First check if the user has login into the system
    try:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        user = User.objects.get(username=username)
        return Response(status=status.HTTP_302_FOUND)

    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        # if user is not exist, we are allow to
        # create the user
        _interal_create_user(
            username=username,
            password=password,
            email=email
        )

        return Response(status=status.HTTP_201_CREATED)


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
        secret_key = request.POST['secret_key']
        if secret_key == 'LAB_AADDGGE':
            _interal_create_user(
                username=username,
                password=password,
                email=email,
                is_super_user=True
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def _interal_create_user(username, password, email, is_super_user=False):
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    user.is_staff = True
    user.is_active = True
    user.is_admin = is_super_user
    user.is_superuser = is_super_user
    user.save()

    return user


@api_view(['GET'])
def hand_checking(request):
    return Response(status=status.HTTP_200_OK)
