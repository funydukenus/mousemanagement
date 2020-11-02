from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class LocalBackends(BaseBackend):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'funyRA12345'
    if a future user database is used, modify the authentication method to have external authentication
    """
    def authenticate(self, request, username=None, password=None):

        user = local_user_check(
            username, password
        )

        if user is not None:
            user = User.objects.get(username=username)
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def local_user_check(username, password):
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None

