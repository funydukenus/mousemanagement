from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .views import harvested_mouse_list
from .views import harvested_mouse_insertion
from .views import harvested_mouse_update
from .models import HarvestedMouse
from datetime import datetime, timedelta


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
                             is_view_class=False, data=None):
    # Check if the return of list of users matched with the listToMatched

    # Create an instance of GET requests
    if not data:
        request = test_cases.factory.get(
            path=view_url
        )
    else:
        request = test_cases.factory.get(
            data=data,
            path=view_url,
            format='json'
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
            if not(len(list_to_matched) == expect_num_of_remain):
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
            birthDate=datetime.now().date(),
            endDate=datetime.now().date(),
            confirmationOfGenoType=True,
            phenoType='phenoType1',
            projectTitle='projectTitle1',
            experiment='experiementTesting',
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
            'birthDate': str(datetime.now().date()),
            'endDate': str(datetime.now().date()),
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

    # Pass requirement
    # 1. create the user with required field
    # 2. use REST Api to filter and retrieve the information without 404
    # 3. matched with the required field set in the first requirement
    def test_filter_harvest_mouse_list(self):

        # Insert the second mouse with same
        # handler as default first entry
        data_to_post = {
            'handler': 'handler1',
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

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion
        )

        # Create the 3rd entry with different handler
        # from the first and second entry
        data_to_post = {
            'handler': 'handler2',
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
            list_to_matched=['handler1'],
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'handler,1': 'handler1'
            }
        )

    # Pass requirement
    # 1. Create arbitrary number of harvested mouse entries
    # 2. Query with multiple different key
    # 3. matched with the required field set in the 1st and 2nd requirement
    def test_filter_advanced_harvest_mouse_list(self):
        # Insert with multiple handler 0 to 4 but with the same Expr1
        # Insert with multiple handler 5 to 8 but with same Expr2
        # It should return handler 1 to handler 3 if filtered with Expr1
        # But exclude the default entry
        experiment_1 = 'Expr1'
        experiment_2 = 'Expr2'

        normal_pheno = 'normal'
        special_pheno = 'speical'

        group_1_start = 0
        group_1_stop = 4
        group_2_start = 5
        group_2_stop = 8

        list_to_matched = []

        for i in range(group_1_start,group_2_stop):
            if i <= group_1_stop:
                experiment = experiment_1
                if i <= group_1_stop-2:
                    pheno = special_pheno
                    list_to_matched.append('handler' + str(i))
                else:
                    pheno = normal_pheno
            else:
                experiment = experiment_2
                pheno = normal_pheno

            data_to_post = {
                'handler': 'handler' + str(i),
                'physicalId': '12345679',
                'gender': 'M',
                'mouseLine': 'mouseLine1',
                'genoType': 'genoType1',
                'birthDate': str(datetime.now().date()),
                'endDate': str(datetime.now().date()),
                'confirmationOfGenoType': 'True',
                'phenoType': pheno,
                'projectTitle': 'projectTitle1',
                'experiment': experiment,
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
        # It will remove from the retrieved mouse list.
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_1_stop-1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'experiment,1': experiment_1,
                'phenoType,1': special_pheno
            }
        )

    # Pass requirement
    # 1. Create arbitrary number of harvested mouse entries
    # 2. Query with multiple different key
    # 3. matched with the required field set in the 1st and 2nd requirement
    def test_filter_datetime_harvest_mouse_list(self):
        # Insert with multiple handler 0 to 4 but with the same Expr1
        # Insert with multiple handler 5 to 8 but with same Expr2
        # It should return handler 1 to handler 3 if filtered with Expr1
        # But exclude the default entry
        experiment_1 = 'Expr1'
        experiment_2 = 'Expr2'

        normal_pheno = 'normal'
        special_pheno = 'speical'

        group_1_start = 0
        group_1_stop = 4
        group_2_start = 5
        group_2_stop = 8

        list_to_matched = []

        specific_date = datetime.now()
        for i in range(group_1_start,group_2_stop):

            cur_date = datetime.now().date() + timedelta(days=i)

            if i == group_2_start:
                specific_date = cur_date

            if i >= group_2_start:
                list_to_matched.append('handler' + str(i))

            data_to_post = {
                'handler': 'handler' + str(i),
                'physicalId': '12345679',
                'gender': 'M',
                'mouseLine': 'mouseLine1',
                'genoType': 'genoType1',
                'birthDate': str(cur_date),
                'endDate': str(datetime.now().date()),
                'confirmationOfGenoType': 'True',
                'phenoType': 'phenoType1',
                'projectTitle': 'projectTitle1',
                'experiment': 'Experiment1',
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
        # It will remove from the retrieved mouse list.
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_2_stop - group_2_start,
            list_to_matched=list_to_matched.copy(),
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'birthDate,2': specific_date
            }
        )

        list_to_matched.remove('handler' + str(group_2_stop - 1))

        # Make a Request to list all the harvested mouse
        # and use the list to matched to all the list of the harvested mouse
        # It will remove from the retrieved mouse list.
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_2_stop - group_2_start - 1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'birthDate,2': specific_date,
                'birthDate,3': specific_date + timedelta(days=1)
            }
        )


    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_advanced_harvest_mouse_insert_multiple(self):

        arr = []
        list_to_matched = []

        group_start = 0
        group_stop = 8

        for i in range(group_start,group_stop):
            list_to_matched.append('handler' + str(i))
            data_to_post = {
                'handler': 'handler' + str(i),
                'physicalId': '12345679',
                'gender': 'M',
                'mouseLine': 'mouseLine1',
                'genoType': 'genoType1',
                'birthDate': str(datetime.now().date()),
                'endDate': str(datetime.now().date()),
                'confirmationOfGenoType': 'True',
                'phenoType': 'phenoType1',
                'projectTitle': 'projectTitle1',
                'experiment': 'Experiment1',
                'comment': 'comment1'
            }

            arr.append(data_to_post)

        data = {}
        data['harvestedmouselist'] = arr


        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_stop - group_start + 1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler'
        )

    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_harvest_mouse_update(self):
        data_to_post = {
            'handler': 'handler1',
            'physicalId': '12345679',
            'gender': 'M',
            'mouseLine': 'mouseLine1',
            'genoType': 'genoType1',
            'birthDate': str(datetime.now().date()),
            'endDate': str(datetime.now().date()),
            'confirmationOfGenoType': 'True',
            'phenoType': 'phenoType1',
            'projectTitle': 'projectTitle1',
            'experiment': 'Experiment1',
            'comment': 'comment1'
        }


        # Make the request and check for the status code
        response = make_request_and_check(
                       test_cases=self,
                       data=data_to_post,
                       url='/harvestedmouse/insert',
                       request_object=self.factory.post,
                       expected_status_code=201,
                       view_class=harvested_mouse_insertion
                   )

        data_to_post['id'] = response.data['id']

        # Change handler to handler2
        data_to_post['handler'] = 'handler2'

        # Make the request and check for the status code
        response = make_request_and_check(
                       test_cases=self,
                       data=data_to_post,
                       url='/harvestedmouse/update',
                       request_object=self.factory.put,
                       expected_status_code=200,
                       view_class=harvested_mouse_update
                   )

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

    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_advanced_harvest_mouse_multiple_update(self):
        data_to_post_2 = {
            'handler': 'handler2',
            'physicalId': '12345679',
            'gender': 'M',
            'mouseLine': 'mouseLine1',
            'genoType': 'genoType1',
            'birthDate': str(datetime.now().date()),
            'endDate': str(datetime.now().date()),
            'confirmationOfGenoType': 'True',
            'phenoType': 'phenoType1',
            'projectTitle': 'projectTitle1',
            'experiment': 'Experiment1',
            'comment': 'comment1'
        }

        data_to_post_3 = {
            'handler': 'handler3',
            'physicalId': '12345679',
            'gender': 'M',
            'mouseLine': 'mouseLine1',
            'genoType': 'genoType1',
            'birthDate': str(datetime.now().date()),
            'endDate': str(datetime.now().date()),
            'confirmationOfGenoType': 'True',
            'phenoType': 'phenoType1',
            'projectTitle': 'projectTitle1',
            'experiment': 'Experiment1',
            'comment': 'comment1'
        }
        data_arr = {}
        data_arr['harvestedmouselist'] = []
        data_arr['harvestedmouselist'].append(data_to_post_2)
        data_arr['harvestedmouselist'].append(data_to_post_3)

        # Make the request and check for the status code
        response = make_request_and_check(
                       test_cases=self,
                       data=data_arr,
                       url='/harvestedmouse/insert',
                       request_object=self.factory.post,
                       expected_status_code=201,
                       view_class=harvested_mouse_insertion
                   )

        data_to_post_2['id'] = response.data[0]['id']
        data_to_post_3['id'] = response.data[1]['id']

        # Change handler to handler2
        data_to_post_2['projectTitle'] = 'ABC'

        # Change handler to handler2
        data_to_post_3['projectTitle'] = 'CBA'

        # Make the request and check for the status code
        response = make_request_and_check(
                       test_cases=self,
                       data=data_arr,
                       url='/harvestedmouse/update',
                       request_object=self.factory.put,
                       expected_status_code=200,
                       view_class=harvested_mouse_update
                   )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=3,
            list_to_matched=['ABC', 'CBA'],
            expect_num_of_remain=0,
            keyword='projectTitle'
        )