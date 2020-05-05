# Import the necessary packages
import datetime
import json

from consolemenu import *
from consolemenu.items import *
import requests
import pandas as pd

API_ENDPOINT = 'https://mousemanagement.herokuapp.com/harvestedmouse/'
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
        with open('input.json', 'w') as f_open:
            f_open.writelines(r.text)
    print('Finished')

def import_csv_into_db():
    input_file = 'input.csv'

    if '.csv' in input_file:
        csv_file = pd.read_csv(input_file)

        csv_file = csv_file.fillna('No Data')

        arr = []

        for index, row in csv_file.iterrows():
            gender = row['gender']
            if gender == 'Male':
                gender = 'M'
            else:
                gender = 'F'

            birthdate = datetime.datetime.strptime(row['birthdate'], '%m-%d-%Y')
            endDate = datetime.datetime.strptime(row['End date'], '%m-%d-%Y')

            data = {
                'handler': row['Handled by'],
                'physicalId': row['physical_id'],
                'gender': gender,
                'mouseLine': row['physical_id'],
                'genoType': row['Genotype'],
                'birthDate': str(birthdate.date()),
                'endDate': str(endDate.date()),
                'confirmationOfGenoType': row['Confirmation of genotype'],
                'phenoType': row['phenotype'],
                'projectTitle': row['project_title'],
                'experiment': row['Experiment'],
                'comment': row['comment']
            }
            arr.append(data)

        jsonStr = json.dumps(arr)
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