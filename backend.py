# Import the necessary packages
import datetime
import json

from consolemenu import *
from consolemenu.items import *
import requests
import pandas as pd

# API_ENDPOINT = 'https://mousemanagement.herokuapp.com/'
API_ENDPOINT = 'http://127.0.0.1:8000/'
HARVESTED_MOUSE_API_ENDPOINT = API_ENDPOINT + 'harvestedmouse/'
INSERT_API_ENDPOINT = HARVESTED_MOUSE_API_ENDPOINT + 'insert'
UPDATE_API_ENDPOINT = HARVESTED_MOUSE_API_ENDPOINT + 'update'
LIST_API_ENDPOINT = HARVESTED_MOUSE_API_ENDPOINT + 'list'
DELETE_ALL_API_ENDPOINT = HARVESTED_MOUSE_API_ENDPOINT + 'delete/all'

USER_API_ENDPOINT = API_ENDPOINT + 'accounts/'
CREATE_USER_API_ENDPOINT = USER_API_ENDPOINT + 'create'
LOGIN_USER_API_ENDPOINT = USER_API_ENDPOINT + 'login'
LOGOUT_USER_API_ENDPOINT = USER_API_ENDPOINT + 'logout'
CHANGE_PASSWORD_USER_API_ENDPOINT = USER_API_ENDPOINT + 'change_password'
CREATE_SUPER_USER_USER_API_ENDPOINT = USER_API_ENDPOINT + 'create_super_user'
IS_USER_API_ENDPOINT = USER_API_ENDPOINT + 'is_user_empty'
SEND_EMAIL_API_ENDPOINT = USER_API_ENDPOINT + 'sendemail'
DELETE_ALL_USER_API_ENDPOINT = USER_API_ENDPOINT + 'deletealluser'

HAND_SHAKE_API_ENDPOINT = API_ENDPOINT + 'hc'

menu = ConsoleMenu('Backend Harvested Mouse Management', 'FNY Lab', show_exit_option=False)


# Start the console gui
def gui_start():
    # Create some items

    # MenuItem is the base class for all items, it doesn't do anything when selected
    menu_item = MenuItem('Menu Item')

    function_handshake = FunctionItem("HandShake", hand_shake)

    # A FunctionItem runs a Python function when selected
    function_item_list = FunctionItem("Output all harvested mouse list", list_all_mouse_on_screen)

    function_item_insert = FunctionItem("Import csv into db", import_csv_into_db)

    function_item_delete_all = FunctionItem("Delete all from db", delete_all_from_db)

    function_user_create = FunctionItem("Create user", create_user)

    function_super_user_create = FunctionItem("Create super user", create_super_user)

    function_user_login = FunctionItem("User login", user_login)

    function_user_logout = FunctionItem("User loggout", user_logout)

    function_user_delete_all = FunctionItem("Delete All User", user_delete_all)

    function_send_email = FunctionItem("Send Email", send_email)

    function_exit = FunctionItem("Exit", exit_console)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(menu_item)
    menu.append_item(function_handshake)
    menu.append_item(function_item_list)
    menu.append_item(function_item_insert)
    menu.append_item(function_item_delete_all)
    menu.append_item(function_user_create)
    menu.append_item(function_super_user_create)
    menu.append_item(function_user_login)
    menu.append_item(function_user_logout)
    menu.append_item(function_user_delete_all)
    menu.append_item(function_send_email)
    menu.append_item(function_exit)
    # Finally, we call show to show the menu and allow the user to interact
    menu.show()


def hand_shake():
    r = requests.get(url=HAND_SHAKE_API_ENDPOINT)
    if r.status_code == 200:
        print('OK')
    else:
        print('FAIL')


def user_delete_all():
    r = requests.get(url=DELETE_ALL_USER_API_ENDPOINT)
    if r.status_code == 200:
        print('OK')
    else:
        print('FAIL')


def send_email():
    title = input("Enter title: ")
    content = input("Enter Content: ")
    password = input("Enter Super User password: ")

    post_data = {
        'title': title,
        'content': content,
        'password': password
    }

    r = requests.post(url=SEND_EMAIL_API_ENDPOINT, data=post_data)
    if r.status_code == 200:
        print('OK')
    else:
        print('FAIL')


def create_user():
    username = input("Enter your username: ")
    superuser_password = input("Enter superuser_password: ")
    email = input("Enter your email: ")

    post_data = {
        'username': username,
        'superuser_password': superuser_password,
        'email': email
    }

    r = requests.post(url=CREATE_USER_API_ENDPOINT, data=post_data)
    if r.status_code == 201:
        print('OK')
    else:
        print('FAIL')


def create_super_user():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    email = input("Enter your email: ")
    secret_key = 'LAB_AADDGGE'

    post_data = {
        'username': username,
        'password': password,
        'email': email,
        'secret_key': secret_key
    }

    r = requests.post(url=CREATE_SUPER_USER_USER_API_ENDPOINT, data=post_data)
    if r.status_code == 201:
        print('OK')
    else:
        print('FAIL')


def user_logout():
    r = requests.get(url=LOGOUT_USER_API_ENDPOINT)
    if r.status_code == 200:
        print('OK')
    else:
        print('FAIL')


def user_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    post_data = {
        'username': username,
        'password': password
    }

    r = requests.post(url=LOGIN_USER_API_ENDPOINT, data=post_data)
    if r.status_code == 200:
        print('OK')
    else:
        print('FAIL')


def exit_console():
    user_logout()
    menu.exit()


def list_all_mouse_on_screen():
    print('Sending list command')
    # sending post request and saving response as response object
    r = requests.get(url=LIST_API_ENDPOINT)
    if r.status_code == 200:
        with open('output.csv', 'w') as f_open:
            f_open.writelines(r.text)
            print('Finished')
    elif r.status_code == 401:
        print('Not allowed')
    else:
        print('Something wrong')


def import_csv_into_db():
    input_file = 'input.csv'

    if '.csv' in input_file:
        csv_file = pd.read_csv(input_file)

        csv_file = csv_file.fillna('No Data')

        dict = {'mouse_list': []}

        arr = dict['mouse_list']

        for index, row in csv_file.iterrows():
            gender = row['gender']
            if gender == 'Male':
                gender = 'M'
            else:
                gender = 'F'
            try:
                birthdate = datetime.datetime.strptime(row['birthdate'], '%m-%d-%Y')
                endDate = datetime.datetime.strptime(row['End date'], '%m-%d-%Y')
            except ValueError:
                continue
            data = {
                'handler': row['Handled by'],
                'physical_id': row['physical_id'],
                'gender': gender,
                'mouseline': row['mouseline'],
                'genotype': row['Genotype'],
                'birth_date': str(birthdate.date()),
                'end_date': str(endDate.date()),
                'cog': row['Confirmation of genotype'],
                'phenotype': row['phenotype'],
                'project_title': row['project_title'],
                'experiment': row['Experiment'],
                'comment': row['comment'],
                'freeze_record': {
                    'liver': row['Freeze Liver'],
                    'liver_tumor': row['Freeze Liver tumour'],
                    'others': row['Freeze Others']
                },
                'pfa_record': {
                    'liver': row['PFA Liver'],
                    'liver_tumor': row['PFA Liver tumour'],
                    'small_intenstine': row['PFA Small intestine'],
                    'small_intenstine_tumor': row['PFA SI tumour'],
                    'skin': row['PFA Skin'],
                    'skin_tumor': row['PFA Skin_Hair'],
                    'others': row['PFA Others']
                }
            }
            arr.append(data)
        arr = json.dumps(dict)
    else:
        json_str_arr = []
        with open(input_file, 'r') as f_open:
            json_str_arr = f_open.readline()
        arr = json.loads(json_str_arr)

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url=INSERT_API_ENDPOINT, json=arr, headers=headers)
    if r.status_code == 201:
        print('OK')
    else:
        print('FAIL')


def delete_all_from_db():
    print('Deleting all entries from db')
    # sending post request and saving response as response object
    r = requests.delete(url=DELETE_ALL_API_ENDPOINT)
    if r.status_code == 200:
        print('OKAY')
    else:
        print('FAIL')


if __name__ == '__main__':
    gui_start()