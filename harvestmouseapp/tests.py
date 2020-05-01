from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .views import harvested_mouse_list
from .views import harvested_mouse_insertion
from .models import HarvestedMouse
from datetime import datetime

############################################
# Function name: is_match_data
# Description:
#              This function provide the functionality to which to match the provided target value with the data in the
#              given response data
############################################
def is_match_data(response, keyword, target):
    for raw_data in response.data:
        if raw_data[keyword] == target:
            return True
    return False


############################################
# Function name: remove_if_matched
# Description: This function provide the functionality
#              to delete a list of objects in the listToMatched
#              with corresponding objects in the data of the response
############################################
def remove_if_matched(response, keyword, list_to_matched):
    for raw_data in response.data:
        target_value = raw_data[keyword]
        if target_value in list_to_matched:
            list_to_matched.remove(target_value)


############################################
# Function name: make_request_and_check
# Description: This function provides the different type request
#              to the target Url based on the type of request, url and
#              it will check the correct status code with the provided
#              status code
############################################
def make_request_and_check(test_cases, data, url, request_object, expected_status_code, view_class, is_view_class=False):
    request = request_object(
                path=url,
                data=data,
                format='json'
              )
    if is_view_class:
        response = view_class.as_view()(request, *[], **{})
    else:
        response = view_class(request)

    # Request is failed
    if response.status_code != expected_status_code:
        test_cases.assertTrue(False, 'Returned: ' + str(response.status_code))

    return response


############################################
# Function name: check_model_view_objects
# Description: This function checks the data in the response data
#              of matched with the given number
############################################
def check_model_view_objects(test_cases, view_list_class, view_url, expect_num_of_return, list_to_matched,
                             expect_num_of_remain, keyword, remove_involved=True, target=None, find_matched=False,
                             is_view_class=False):
    # Check if the return of list of users matched with the listToMatched

    # Create an instance of GET requests
    request = test_cases.factory.get(
        path=view_url
    )

    if is_view_class:
        response = view_list_class().as_view()(request, *[], **{})
    else:
        response = view_list_class(request)

    if len(response.data) == expect_num_of_return:
        # Remove all the user in the listToMatched if it exists in the data of the response
        if remove_involved:
            remove_if_matched(response, keyword, list_to_matched)
            # If the list is not empty,
            # it means the list getting from the
            # view is incorrect
            if len(list_to_matched) != expect_num_of_remain:
                test_cases.assertTrue(False)
        else:
            if find_matched:
                if not(is_match_data(response, keyword, target)):
                    test_cases.assertTrue(False)
            else:
                if is_match_data(response, keyword, target):
                    test_cases.assertTrue(False)

    else:
        # Number of items retrieve was wrong
        test_cases.assertTrue(False)


##############################################################################################################
# Unit Test name: Harvested Mouse test case
# Target: HarvestedMouse Object
# Description:
#              1. With predefined inserted mouse the function successfully retrieve the correct information
#              2. The API able to create new mouse entry based on the provided information
##############################################################################################################
class HarvestedMouseTestCase(TestCase):
    # Setup function, insert required objects into the database
    def setUp(self) -> None:
        # Every test should use factory object to spawn the request object
        self.factory = APIRequestFactory()

        harvested_mouse = HarvestedMouse(
            handler='handler1',
            physicalId='12345678',
            gender='M',
            mouseLine='mouseLine1',
            genoType='genoType1',
            birthDate=datetime.now(),
            endDate=datetime.now(),
            confirmationOfGenoType=True,
            phenoType='phenoType1',
            projectTitle='projectTitle1',
            experiment='experiement1',
            comment='comment1'
        )
        harvested_mouse.save()

    # Pass requirement
    # 1. create the user with required field
    # 2. use REST Api to retrieve the information without 404
    # 3. matched with the required field set in the first requirement
    def test_harvest_mouse_insert(self):
        data_to_post = {
            'handler': 'handler2',
            'physicalId': '12345679',
            'gender': 'M',
            'mouseLine': 'mouseLine1',
            'genoType': 'genoType1',
            'birthDate': str(datetime.now()),
            'endDate': str(datetime.now()),
            'confirmationOfGenoType': 'True',
            'phenoType': 'phenoType1',
            'projectTitle': 'projectTitle1',
            'experiment': 'experiement1',
            'comment': 'comment1'
        }

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion
        )

        # Make a Request to list all the harvested mouse
        # and use the list to matched to all the list of the harvested mouse
        # It will remove from the retrived mouse list.
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=2,
            list_to_matched=['handler1', 'handler2'],
            expect_num_of_remain=0,
            keyword='handler'
        )