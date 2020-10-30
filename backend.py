# Import the necessary packages
import datetime
import json

from consolemenu import *
from consolemenu.items import *
import requests
import pandas as pd

API_ENDPOINT = 'http://127.0.0.1:8000/harvestedmouse/'
INSERT_API_ENDPOINT = API_ENDPOINT + 'insert'
UPDATE_API_ENDPOINT = API_ENDPOINT + 'update'
LIST_API_ENDPOINT   = API_ENDPOINT + 'list'
DELETE_ALL_API_ENDPOINT = API_ENDPOINT + 'delete/all'


# Start the console gui
def gui_start():
    # Create the menu
    menu = ConsoleMenu('Backend Harvested Mouse Management', 'FNY Lab')

    # Create some items

    # MenuItem is the base class for all items, it doesn't do anything when selected
    menu_item = MenuItem('Menu Item')

    # A FunctionItem runs a Python function when selected
    function_item_list = FunctionItem("Output all harvested mouse list", list_all_mouse_on_screen)

    function_item_insert = FunctionItem("Import csv into db", import_csv_into_db)

    function_item_delete_all = FunctionItem("Delete all from db", delete_all_from_db)

    # Once we're done creating them, we just add the items to the menu
    menu.append_item(menu_item)
    menu.append_item(function_item_list)
    menu.append_item(function_item_insert)
    menu.append_item(function_item_delete_all)

    # Finally, we call show to show the menu and allow the user to interact
    menu.show()


def list_all_mouse_on_screen():
    print('Sending list command')
    # sending post request and saving response as response object
    r = requests.get(url=LIST_API_ENDPOINT)
    if r.status_code == 200:
        with open('output.csv', 'w') as f_open:
            f_open.writelines(r.text)
    print('Finished')


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