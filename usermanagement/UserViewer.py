import json
from abc import ABC, abstractmethod


class GenericUserViewer(ABC):
    """
    This is the User Model Adapter Class.
    Subclass must implement the transform which converts either User Django Query Set to Json formatted string
    """
    @abstractmethod
    def transform(self, user_data):
        pass


class JsonUserViewer(GenericUserViewer):
    def transform(self, user_data):
        if user_data is not None:
            data = _convert_user_to_dict(user_data)
            return json.dumps(data)
        else:
            json_obj = {
                'user_list': []
            }
            return json.dumps(json_obj)


def _distribute_data_to_user(user_data):
    """
    This function distributed the user object information into the python dictionary object for easier json
    parsing process
    """

    # Different from mouse list, treats all resulst as if it's list
    if user_data.last_login:
        last_login_date = user_data.last_login.strftime("%m-%d-%Y,%H:%M:%S")
    else:
        last_login_date = 'None'
    dict_m = {
        'firstname': user_data.first_name,
        'lastname': user_data.last_name,
        'username': user_data.username,
        'email': user_data.email,
        'is_active': user_data.is_active,
        'created_date': user_data.date_joined.strftime("%m-%d-%Y,%H:%M:%S"),
        'last_login_date': last_login_date,
        'is_admin': user_data.is_superuser,
        'is_cur_login': user_data.userextend.is_logged_in_verified,
        'is_email_verified': user_data.userextend.is_email_verified
    }
    return dict_m


def _convert_user_to_dict(user_data):
    """
    This is the function restricte to this module which converts the UserList data
    into Json formmated string
    """
    dict_m = {'user_list': []}
    arr_m = dict_m['user_list']
    try:
        for user in user_data:
            arr_m.append(
                _distribute_data_to_user(user)
            )
        return dict_m
    except TypeError:
        return _distribute_data_to_user(user_data)

