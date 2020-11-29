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
    dict_m = {
        'username': user_data.username,
        'email': user_data.email,
        'is_active': user_data.is_active,
        'created_date': user_data.date_joined.strftime("%m-%d-%Y,%H:%M:%S"),
        'last_login_date': user_data.last_login.strftime("%m-%d-%Y,%H:%M:%S"),
        'is_login': user_data.is_authenticated,
        'is_admin': user_data.is_superuser
    }
    return dict_m


def _convert_user_to_dict(user_data):
    """
    This is the function restricte to this module which converts the UserList data
    into Json formmated string
    """
    dict_m = {'user_list': []}
    arr_m = dict_m['user_list']
    for user in user_data:
        arr_m.append(
            _distribute_data_to_user(user)
        )
    return dict_m
