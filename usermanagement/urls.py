from django.urls import path

from usermanagement.views import user_login, user_logout, user_change_password, create_inactive_user, create_super_user, \
    is_user_table_empty, is_login, email_test, clear_all_user, check_secret_key, user_reset_new_pwd, get_all_user_info, \
    hand_checking, toggle_activity_user, is_admin, delete_user

urlpatterns = [
    path('login', user_login),
    path('logout', user_logout),
    path('change_password', user_change_password),
    path('create', create_inactive_user),
    path('create_super_user', create_super_user),
    path('is_user_empty', is_user_table_empty),
    path('islogin', is_login),
    path('sendemail', email_test),
    path('deletealluser', clear_all_user),
    path('checksecretuser', check_secret_key),
    path('newuserpwdchange', user_reset_new_pwd),
    path('getalluserinfo', get_all_user_info),
    path('toggle-activity-user', toggle_activity_user),
    path('delete-user', delete_user),
    path('is-admin', is_admin),
    path('hc', hand_checking)
]