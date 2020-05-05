# importing the requests library
from datetime import datetime

import requests

API_ENDPOINT = 'https://mousemanagement.herokuapp.com/harvestedmouse/'
INSERT_API_ENDPOINT = API_ENDPOINT + 'insert'
UPDATE_API_ENDPOINT = API_ENDPOINT + 'update'
LIST_API_ENDPOINT   = API_ENDPOINT + 'list'

def main():
    data = {
        'handler': 'ShihHan',
        'physicalId': '12345679',
        'gender': 'M',
        'mouseLine': 'mouseLine1',
        'genoType': 'genoType1',
        'birthDate': str(datetime.now().date()),
        'endDate': str(datetime.now().date()),
        'confirmationOfGenoType': 'True',
        'phenoType': 'phenoType1',
        'projectTitle': 'projectTitle1',
        'experiment': 'experiement1',
        'comment': 'comment1'
    }

    # sending post request and saving response as response object
    r = requests.post(url=INSERT_API_ENDPOINT, data=data)

    if r.status_code == 201:
        print('Mouse created')
        print('Sending list command')
        # sending post request and saving response as response object
        r = requests.get(url=LIST_API_ENDPOINT)
        if r.status_code == 200:
            print(r.text)
    else:
        print('Mouse not created')


if __name__ == '__main__':
    main()