from django.urls import path

from usermanagement.views import user_login, user_logout, user_change_password, create_inactive_user, create_super_user, \
    clear_all_user, check_secret_key, user_reset_new_pwd, get_all_user_info, \
    hand_checking, toggle_activity_user, delete_user, get_logged_user_info, get_num_user

urlpatterns = [
    path('login', user_login),
    path('logout', user_logout),
    path('change_password', user_change_password),
    path('create', create_inactive_user),
    path('create_super_user', create_super_user),
    path('deletealluser', clear_all_user),
    path('checksecretuser', check_secret_key),
    path('newuserpwdchange', user_reset_new_pwd),
    path('getalluserinfo', get_all_user_info),
    path('toggle-activity-user', toggle_activity_user),
    path('delete-user', delete_user),
    path('get-logged-user-info', get_logged_user_info),
    path('get_num_user', get_num_user),
    path('hc', hand_checking)
]