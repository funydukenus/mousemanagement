import os
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .mvc_model.Error import DuplicationMouseError
from .mvc_model.databaseAdapter import GenericSqliteConnector
from .mvc_model.mouseFilter import MouseFilter, FilterOption
from .views import harvested_mouse_list, harvested_mouse_force_list
from .views import harvested_mouse_insertion
from .views import harvested_mouse_update
from .views import harvested_mouse_delete
from .models import HarvestedMouse, HarvestedBasedNumber, HarvestedAdvancedNumber
from datetime import datetime, timedelta

# Use in MVC model test
from harvestmouseapp.mvc_model.model import Mouse, MouseList, Record, AdvancedRecord
from harvestmouseapp.mvc_model.mouseAdapter import XmlModelAdapter, JsonModelAdapter
from harvestmouseapp.mvc_model.mouseViewer import XmlMouseViewer, JsonMouseViewer
import random
import string
import time
import copy


############################################
# Function name: create_mouse_object
# Description:
#              This function creats the mouse object and transform based on the transfom object
############################################
def create_mouse_object(physical_id, handler, gender, mouseline, genotype,
                        birth_date, end_date, cog, phenotype, project_title, experiment, comment,
                        pfa_record, freeze_record):
    harvested_mouse = Mouse(
        handler=handler,
        physical_id=physical_id,
        gender=gender,
        mouseline=mouseline,
        genotype=genotype,
        birth_date=birth_date,
        end_date=end_date,
        cog=cog,
        phenotype=phenotype,
        project_title=project_title,
        experiment=experiment,
        comment=comment
    )

    harvested_mouse.pfa_record = pfa_record
    harvested_mouse.freeze_record = freeze_record

    return harvested_mouse


############################################
# Function name: is_match_data
# Description:
#              This function provide the functionality to which to match the provided target value with the data in the
#              given response data
############################################
def is_match_data(data, keyword, target, child_keyword=None):
    if isinstance(data, Mouse):
        if not child_keyword:
            if data.__dict__[keyword] == target:
                return True
        else:
            if data.__dict__[keyword][child_keyword] == target:
                return True
    else:
        for raw_data in data:
            if not child_keyword:
                if raw_data[keyword] == target:
                    return True
            else:
                if raw_data[keyword][child_keyword] == target:
                    return True
    return False


############################################
# Function name: remove_if_matched
# Description: This function provide the functionality
#              to delete a list of objects in the listToMatched
#              with corresponding objects in the data of the response
############################################
def remove_if_matched(data, keyword, list_to_matched, child_keyword=None):
    keyword = '_Mouse__'+keyword
    if child_keyword:
        if 'liver' in child_keyword or 'others' in child_keyword:
            child_keyword = '_Record__' + child_keyword
        else:
            child_keyword = '_AdvancedRecord__' + child_keyword

    if isinstance(data, list):
        for raw_data in data:
            raw_data = raw_data.__dict__
            if not child_keyword:
                target_value = raw_data[keyword]
            else:
                target_value = raw_data[keyword].__dict__[child_keyword]
            if target_value in list_to_matched:
                list_to_matched.remove(target_value)
    else:
        if not child_keyword:
            target_value = data[keyword]
        else:
            target_value = data[keyword].__dict__[child_keyword]

        if target_value in list_to_matched:
            list_to_matched.remove(target_value)


############################################
# Function name: make_request_and_check
# Description: This function provides the different type request
#              to the target Url based on the type of request, url and
#              it will check the correct status code with the provided
#              status code
############################################
def make_request_and_check(test_cases, data, url, request_object, expected_status_code, view_class,
                           is_view_class=False, viewer=None):
    if viewer:
        data = viewer.transform(data)

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
# Function name: make_request_and_check
# Description: This function provides the functionality to force
#              force reset the mouse list in the database
############################################
def force_refresh_cache(test_cases):
    make_request_and_check(
        test_cases=test_cases,
        data=None,
        url='/harvestedmouse/force_list',
        request_object=test_cases.factory.get,
        expected_status_code=200,
        view_class=harvested_mouse_force_list
    )


############################################
# Function name: check_model_view_objects
# Description: This function checks the data in the response data
#              of matched with the given number
############################################
def check_model_view_objects(test_cases, view_list_class, view_url, expect_num_of_return, list_to_matched,
                             expect_num_of_remain, keyword, remove_involved=True, target=None, find_matched=False,
                             is_view_class=False, data=None, child_keyword=None, adapter=None):
    # Check if the return of list of users matched with the listToMatched

    # Create an instance of GET requests
    if data is None:
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

    data = adapter.transform(response.data)

    is_list_and_size_is_expected = False
    if isinstance(data, MouseList):
        if len(data) == expect_num_of_return:
            is_list_and_size_is_expected = True

    if (isinstance(data, Mouse) and expect_num_of_return == 1) or is_list_and_size_is_expected:
        # Remove all the user in the listToMatched if it exists in the data of the response

        if remove_involved:
            if '_mouse_list' in data.__dict__.keys():
                data = data.__dict__['_mouse_list']
            else:
                data = data.__dict__

            remove_if_matched(data, keyword, list_to_matched, child_keyword)
            # If the list is not empty,
            # it means the list getting from the
            # view is incorrect
            if not (len(list_to_matched) == expect_num_of_remain):
                test_cases.assertTrue(False)
        else:
            if find_matched:
                if not (is_match_data(data, keyword, target, child_keyword)):
                    test_cases.assertTrue(False)
            else:
                if is_match_data(data, keyword, target, child_keyword):
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

        self.viewer = JsonMouseViewer()
        self.adapter = JsonModelAdapter()

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

        freeze_record = HarvestedBasedNumber(
            harvestedMouseId=harvested_mouse,
            liver=1,
            liverTumor=1,
            others='3'
        )

        freeze_record.save()

        pfa_record = HarvestedAdvancedNumber(
            harvestedMouseId=harvested_mouse,
            liver=1,
            liverTumor=1,
            smallIntestine=1,
            smallIntestineTumor=1,
            skin=1,
            skinHair=1,
            others='5'
        )

        pfa_record.save()

    # Pass requirement
    # 1. create the user with required field
    # 2. use REST Api to retrieve the information without 404
    # 3. matched with the required field set in the first requirement
    def test_harvest_mouse_insert(self):
        data_to_post = create_mouse_object(
            handler='handler2',
            physical_id='12345679',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
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
            keyword='handler',
            adapter=self.adapter
        )

    # Pass requirement
    # 1. create the user with required field
    # 2. use REST Api to filter and retrieve the information without 404
    # 3. matched with the required field set in the first requirement
    def test_filter_harvest_mouse_list(self):
        force_refresh_cache(self)
        data_to_post = create_mouse_object(
            handler='handler1',
            physical_id='12345679',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        data_to_post = create_mouse_object(
            handler='handler2',
            physical_id='1234567A',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
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
                'filter': 'handler@handler1'
            },
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Create arbitrary number of harvested mouse entries
    # 2. Query with multiple different key
    # 3. matched with the required field set in the 1st and 2nd requirement
    def test_filter_advanced_harvest_mouse_list(self):
        force_refresh_cache(self)
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
        group_2_stop = 8

        list_to_matched = []

        for i in range(group_1_start, group_2_stop):
            if i <= group_1_stop:
                experiment = experiment_1
                if i <= group_1_stop - 2:
                    pheno = special_pheno
                    list_to_matched.append('handler' + str(i))
                else:
                    pheno = normal_pheno
            else:
                experiment = experiment_2
                pheno = normal_pheno

            data_to_post = create_mouse_object(
                handler='handler' + str(i),
                physical_id='1234567A' + str(i),
                gender='M',
                mouseline='mouseLine1',
                genotype='genoType1',
                birth_date=datetime.now().date(),
                end_date=datetime.now().date(),
                cog='True',
                phenotype=pheno,
                project_title='projectTitle1',
                experiment=experiment,
                comment='comment1',
                pfa_record=AdvancedRecord(
                    1, 1, 1, 1, 1, 1, '1'
                ),
                freeze_record=Record(
                    1, 1, '1'
                )
            )

            # Make the request and check for the status code
            make_request_and_check(
                test_cases=self,
                data=data_to_post,
                url='/harvestedmouse/insert',
                request_object=self.factory.post,
                expected_status_code=201,
                view_class=harvested_mouse_insertion,
                viewer=self.viewer
            )

        filter_option = 'experiment@{}$phenotype@{}'.format(experiment_1, special_pheno)
        # Make a Request to list all the harvested mouse
        # and use the list to matched to all the list of the harvested mouse
        # It will remove from the retrieved mouse list.
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_1_stop - 1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'filter': filter_option
            },
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Create arbitrary number of harvested mouse entries
    # 2. Query with multiple different key
    # 3. matched with the required field set in the 1st and 2nd requirement
    def test_filter_datetime_harvest_mouse_list(self):
        force_refresh_cache(self)
        # Insert with multiple handler 0 to 4 but with the same Expr1
        # Insert with multiple handler 5 to 8 but with same Expr2
        # It should return handler 1 to handler 3 if filtered with Expr1
        # But exclude the default entry
        group_1_start = 0
        group_2_start = 5
        group_2_stop = 8

        list_to_matched = []

        specific_date = datetime.now()
        for i in range(group_1_start, group_2_stop):

            cur_date = datetime.now().date() + timedelta(days=i)

            if i == group_2_start:
                specific_date = cur_date

            if i >= group_2_start:
                list_to_matched.append('handler' + str(i))

            data_to_post = create_mouse_object(
                handler='handler' + str(i),
                physical_id='1234567A' + str(i),
                gender='M',
                mouseline='mouseLine1',
                genotype='genoType1',
                birth_date=cur_date,
                end_date=datetime.now().date(),
                cog='True',
                phenotype='phenoType1',
                project_title='projectTitle1',
                experiment='Experiment1',
                comment='comment1',
                pfa_record=AdvancedRecord(
                    1, 1, 1, 1, 1, 1, '1'
                ),
                freeze_record=Record(
                    1, 1, '1'
                )
            )

            # Make the request and check for the status code
            make_request_and_check(
                test_cases=self,
                data=data_to_post,
                url='/harvestedmouse/insert',
                request_object=self.factory.post,
                expected_status_code=201,
                view_class=harvested_mouse_insertion,
                viewer=JsonMouseViewer()
            )

        filter_option = 'birth_date@{}@{}'.format(str(specific_date), 0)
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
                'filter': filter_option
            },
            adapter=JsonModelAdapter()
        )

        list_to_matched.remove('handler' + str(group_2_stop - 1))

        # Make a Request to list all the harvested mouse
        # and use the list to matched to all the list of the harvested mouse
        # It will remove from the retrieved mouse list.
        # The remaining should be 0
        filter_option = 'birth_date@{}@{}$birth_date@{}@{}'.format(
            str(specific_date), 0, str(specific_date + timedelta(days=1)), 2)

        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=group_2_stop - group_2_start - 1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler',
            data={
                'filter': filter_option
            },
            adapter=JsonModelAdapter()
        )

    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_advanced_harvest_mouse_insert_multiple(self):
        # Force get the new mouse list from the db
        force_refresh_cache(self)
        list_to_matched = []

        group_start = 0
        group_stop = 8
        mouse_list = MouseList()
        for i in range(group_start, group_stop):
            list_to_matched.append('handler' + str(i))
            data_to_post = create_mouse_object(
                handler='handler' + str(i),
                physical_id='1234567A' + str(i),
                gender='M',
                mouseline='mouseLine1',
                genotype='genoType1',
                birth_date=datetime.now().date(),
                end_date=datetime.now().date(),
                cog='True',
                phenotype='phenoType1',
                project_title='projectTitle1',
                experiment='experiment1',
                comment='comment1',
                pfa_record=AdvancedRecord(
                    1, 1, 1, 1, 1, 1, '1'
                ),
                freeze_record=Record(
                    1, 1, '1'
                )
            )
            mouse_list.add_mouse(data_to_post)

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=mouse_list,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=mouse_list.get_size() + 1,
            list_to_matched=list_to_matched,
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_harvest_mouse_update(self):

        # Force get the new mouse list from the db
        force_refresh_cache(self)

        data_to_post = create_mouse_object(
            handler='handler1',
            physical_id='12345679',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )
        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        # Change handler to handler2
        data_to_post.handler = 'handler2'

        # Change pfaRecord.smallIntestineTumor to 15
        data_to_post.pfa_record.small_intenstine_tumor = 15

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/update',
            request_object=self.factory.put,
            expected_status_code=200,
            view_class=harvested_mouse_update,
            viewer=self.viewer
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=2,
            list_to_matched=['handler1', 'handler2'],
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=2,
            list_to_matched=[1, 15],
            expect_num_of_remain=0,
            keyword='pfa_record',
            child_keyword='small_intenstine_tumor',
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Insert multiple mouses at one time
    # 2. matched with the required field set
    def test_advanced_harvest_mouse_multiple_update(self):
        # Force get the new mouse list from the db
        force_refresh_cache(self)

        data_to_post_2 = create_mouse_object(
            handler='handler2',
            physical_id='12345679',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        data_to_post_3 = create_mouse_object(
            handler='handler3',
            physical_id='1234567B',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        mouse_list = MouseList()
        mouse_list.add_mouse([data_to_post_2, data_to_post_3])

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=mouse_list,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        # Change handler to handler2
        data_to_post_2.project_title = 'ABC'

        # Change handler to handler2
        data_to_post_3.project_title = 'CBA'

        # Change pfaRecord.smallIntestineTumor to 16
        data_to_post_2.pfa_record.small_intenstine_tumor = 16
        # Change pfaRecord.smallIntestineTumor to 15
        data_to_post_3.pfa_record.small_intenstine_tumor = 15

        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=mouse_list,
            url='/harvestedmouse/update',
            request_object=self.factory.put,
            expected_status_code=200,
            view_class=harvested_mouse_update,
            viewer=self.viewer
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=3,
            list_to_matched=['ABC', 'CBA'],
            expect_num_of_remain=0,
            keyword='project_title',
            adapter=self.adapter
        )

        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=3,
            list_to_matched=[1, 16, 15],
            expect_num_of_remain=0,
            keyword='pfa_record',
            child_keyword='small_intenstine_tumor',
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Delete inserted mouse handler2
    # 2. handler 2 should not exists in the list
    def test_harvest_mouse_delete(self):
        # Force get the new mouse list from the db
        force_refresh_cache(self)

        data_to_post = create_mouse_object(
            handler='handler2',
            physical_id='1234567B',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        # Insert handler 2 mouse into db
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        # Check handler 2 is inserted into db
        # by retrieving entire mouse entries
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=2,
            list_to_matched=['handler1', 'handler2'],
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )

        # Make request to delete the handler 2 mouse
        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=data_to_post,
            url='/harvestedmouse/delete',
            request_object=self.factory.delete,
            expected_status_code=200,
            view_class=harvested_mouse_delete,
            viewer=self.viewer
        )

        # After deleted handler2 mouse
        # only handler1 remained
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=1,
            list_to_matched=['handler1'],
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )

    # Pass requirement
    # 1. Delete inserted mouse handler2
    # 2. handler 2 should not exists in the list
    def test_advanced_harvest_mouse_multiple_delete(self):
        # Force get the new mouse list from the db
        force_refresh_cache(self)

        data_to_post_2 = create_mouse_object(
            handler='handler2',
            physical_id='1234567B',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        # Insert handler 2 mouse into db
        make_request_and_check(
            test_cases=self,
            data=data_to_post_2,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        data_to_post_3 = create_mouse_object(
            handler='handler3',
            physical_id='1234567C',
            gender='M',
            mouseline='mouseLine1',
            genotype='genoType1',
            birth_date=datetime.now().date(),
            end_date=datetime.now().date(),
            cog='True',
            phenotype='phenoType1',
            project_title='projectTitle1',
            experiment='experiment1',
            comment='comment1',
            pfa_record=AdvancedRecord(
                1, 1, 1, 1, 1, 1, '1'
            ),
            freeze_record=Record(
                1, 1, '1'
            )
        )

        # Make the request and check for the status code
        # Insert handler 2 mouse into db
        make_request_and_check(
            test_cases=self,
            data=data_to_post_3,
            url='/harvestedmouse/insert',
            request_object=self.factory.post,
            expected_status_code=201,
            view_class=harvested_mouse_insertion,
            viewer=self.viewer
        )

        # After inserted 2 mice
        # there will be 3 mouses handler1,handler2 and handler3
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=3,
            list_to_matched=['handler1', 'handler2', 'handler3'],
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )

        mouse_list = MouseList()

        mouse_list.add_mouse([data_to_post_2, data_to_post_3])

        # Delete handler 2 and handler 3
        # Make request to delete the handler 2 mouse
        # Make the request and check for the status code
        make_request_and_check(
            test_cases=self,
            data=mouse_list,
            url='/harvestedmouse/delete',
            request_object=self.factory.delete,
            expected_status_code=200,
            view_class=harvested_mouse_delete,
            viewer=self.viewer
        )

        # After deleted handler2 and handler 3mouse
        # only handler1 remained
        # The remaining should be 0
        check_model_view_objects(
            test_cases=self,
            view_list_class=harvested_mouse_list,
            view_url='/harvestedmouse/list',
            expect_num_of_return=1,
            list_to_matched=['handler1'],
            expect_num_of_remain=0,
            keyword='handler',
            adapter=self.adapter
        )


'''
MVC Test
'''


def str_time_prop(start, end, format_input, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format_input))
    etime = time.mktime(time.strptime(end, format_input))
    ptime = stime + prop * (etime - stime)

    return time.strftime(format_input, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y-%m-%d', prop)


def random_boolean():
    return random.choice([True, False])


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_random_gender():
    return random.choice(['Male', 'Female'])


def get_random_hanlder():
    return random.choice(['Shih Han', 'Alex', 'Hui San', 'David', 'Mark'])


##############################################################################################################
# Unit Test name: Model Model test case
# Target: Mouse, MouseList
# Description:
#              1. Populate information into Mouse, retrieve the same information from the mouse
#              2. Testing basic manipulation of MouseList
##############################################################################################################
class ModelTestCase(TestCase):
    # Setup function, insert required objects into the database
    def setUp(self) -> None:
        self.physical_id = get_random_string(8)
        self.handler = get_random_hanlder()
        self.gender = get_random_gender()
        self.mouseline = get_random_string(8)
        self.genotype = get_random_string(8)
        self.birth_date = random_date("2008-1-1", "2009-1-1", random.random())
        self.end_date = random_date("2008-1-1", "2009-1-1", random.random())
        self.cog = str(random_boolean())
        self.phenotype = get_random_string(8)
        self.project_title = get_random_string(6)
        self.experiment = get_random_string(6)
        self.comment = get_random_string(30)

        self.sample_mouse = Mouse(physical_id=self.physical_id,
                                  handler=self.handler,
                                  gender=self.gender,
                                  mouseline=self.mouseline,
                                  genotype=self.genotype,
                                  birth_date=self.birth_date,
                                  end_date=self.end_date,
                                  cog=self.cog,
                                  phenotype=self.phenotype,
                                  project_title=self.project_title,
                                  experiment=self.experiment,
                                  comment=self.comment)

    # Pass requirement
    # 1. Checl the inforamtion created and populated is the same
    def test_model_mouse(self):
        if not (self.sample_mouse.physical_id == self.physical_id and
                self.sample_mouse.handler == self.handler and
                self.sample_mouse.genotype == self.genotype):
            self.assertTrue(False)

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly
    def test_model_mouse_list_add_retrieve(self):
        self.check_moust_list = []
        self.mouselist = MouseList()

        for i in range(1, 10):
            m = Mouse(physical_id=get_random_string(8),
                      handler=self.handler,
                      gender=self.gender,
                      mouseline=self.mouseline,
                      genotype=self.genotype,
                      birth_date=self.birth_date,
                      end_date=self.end_date,
                      cog=self.cog,
                      phenotype=self.phenotype,
                      project_title=self.project_title,
                      experiment=self.experiment,
                      comment=self.comment)
            self.check_moust_list.append(m)
            self.mouselist.add_mouse(m)

        for m in self.check_moust_list:
            self.mouselist.remove_mouse(m)

        if self.mouselist.get_size() != 0:
            self.assertTrue(False)

        self.check_moust_list = []
        self.mouselist = MouseList()

        # Using different mouse but with same id, different ref
        for i in range(1, 10):
            m = Mouse(physical_id=get_random_string(8),
                      handler=self.handler,
                      gender=self.gender,
                      mouseline=self.mouseline,
                      genotype=self.genotype,
                      birth_date=self.birth_date,
                      end_date=self.end_date,
                      cog=self.cog,
                      phenotype=self.phenotype,
                      project_title=self.project_title,
                      experiment=self.experiment,
                      comment=self.comment)
            self.check_moust_list.append(m)
            self.mouselist.add_mouse(copy.deepcopy(m))

        for m in self.check_moust_list:
            self.mouselist.remove_mouse(m)

        if self.mouselist.get_size() != 0:
            self.assertTrue(False)

    # Pass requirement
    # 1. Check if the mouse list can be retrived correctly
    def test_model_mouse_List_equality_matched(self):
        self.check_moust_list = []
        self.mouselist = MouseList()
        self.sample_mouse_list = MouseList()

        for i in range(1, 10):
            m = Mouse(physical_id=get_random_string(8),
                      handler=self.handler,
                      gender=self.gender,
                      mouseline=self.mouseline,
                      genotype=self.genotype,
                      birth_date=self.birth_date,
                      end_date=self.end_date,
                      cog=self.cog,
                      phenotype=self.phenotype,
                      project_title=self.project_title,
                      experiment=self.experiment,
                      comment=self.comment)
            self.check_moust_list.append(m)
            self.mouselist.add_mouse(m)
            self.sample_mouse_list.add_mouse(m)

        if not (self.mouselist == self.sample_mouse_list):
            self.assertTrue(False)

        # Clear everything
        self.mouselist.clear()
        self.sample_mouse_list.clear()

        for i in range(1, 10):
            physical_id = get_random_string(8)
            m = Mouse(physical_id=physical_id,
                      handler=self.handler,
                      gender=self.gender,
                      mouseline=self.mouseline,
                      genotype=self.genotype,
                      birth_date=self.birth_date,
                      end_date=self.end_date,
                      cog=self.cog,
                      phenotype=self.phenotype,
                      project_title=self.project_title,
                      experiment=self.experiment,
                      comment=self.comment)
            m2 = Mouse(physical_id=physical_id[::-1],
                       handler=self.handler,
                       gender=self.gender,
                       mouseline=self.mouseline,
                       genotype=self.genotype,
                       birth_date=self.birth_date,
                       end_date=self.end_date,
                       cog=self.cog,
                       phenotype=self.phenotype,
                       project_title=self.project_title,
                       experiment=self.experiment,
                       comment=self.comment)
            self.mouselist.add_mouse(m)
            self.sample_mouse_list.add_mouse(m2)

        if self.mouselist == self.sample_mouse_list:
            self.assertTrue(False)

    # Pass requirement
    # 1. Check if the mouse list can be retrived correctly
    def test_model_mouse_List_update_matched(self):
        # Tested with modifying handler with same ref
        self.mouselist = MouseList()
        self.mouselist.add_mouse(self.sample_mouse)
        self.sample_mouse.handler = 'ABC'
        self.mouselist.update_mouse(self.sample_mouse)

        mouse = self.mouselist.get_mouse_by_id(self.sample_mouse.physical_id)
        if not(mouse.handler == 'ABC'):
            self.assertTrue(False)

        # Tested with different reference address
        # Creating a diff address of the mouse with different handler
        # but with same physical id
        m2 = Mouse(physical_id=self.physical_id,
                   handler='CBA',
                   gender=self.gender,
                   mouseline=self.mouseline,
                   genotype=self.genotype,
                   birth_date=self.birth_date,
                   end_date=self.end_date,
                   cog=self.cog,
                   phenotype=self.phenotype,
                   project_title=self.project_title,
                   experiment=self.experiment,
                   comment=self.comment)
        self.mouselist.update_mouse(m2)

        mouse = self.mouselist.get_mouse_by_id(self.sample_mouse.physical_id)
        if not(mouse.handler == 'CBA'):
            self.assertTrue(False)

    ##############################################################################################################


# Unit Test name: Model Adapter test case
# Target: Mouse, MouseList
# Description:
#              1. Populated a predefined mouse list
#              2. make sure the converted information in the xml file matched with the predefined mouse list
##############################################################################################################
class ModelAdapterTestCase(TestCase):
    # Setup function, insert required objects into the database
    def setUp(self) -> None:
        self.physical_id = 'abc'
        self.handler = 'Shih Han'
        self.gender = 'Male'
        self.mouseline = 'mouseline1'
        self.genotype = 'genotype1'
        self.birth_date = '2020-06-11'
        self.end_date = '2020-05-21'
        self.cog = '1'
        self.phenotype = 'Phenotyp1'
        self.project_title = 'abc'
        self.experiment = 'exprement1'
        self.comment = 'comment1'

        self.sample_mouse_1 = Mouse(physical_id=self.physical_id,
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.sample_mouse_2 = Mouse(physical_id=self.physical_id[::-1],
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.mouse_list = MouseList()
        self.mouse_list.add_mouse([self.sample_mouse_1, self.sample_mouse_2])

        self.adapter = XmlModelAdapter()

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly
    def test_model_mouse_matched(self):
        # open xml file
        with open('harvestmouseapp/mvc_model/sample/singlemouse.xml') as r_open:
            xml_raw_data = r_open.read()
            # transform the data into mouse object
            converted = self.adapter.transform(xml_raw_data)
            if not (self.sample_mouse_1.physical_id == converted.physical_id and
                    self.sample_mouse_1.handler == converted.handler and
                    self.sample_mouse_1.genotype == converted.genotype):
                self.assertTrue(False)

    # Pass requirement
    # 1. Check if the mouse list can be retrived correctly
    def test_model_mouse_List_matched(self):
        # open xml file
        with open('harvestmouseapp/mvc_model/sample/groupmouse.xml') as r_open:
            xml_raw_data = r_open.read()
            # transform the data into mouse object
            converted_list = self.adapter.transform(xml_raw_data)
            for m in converted_list:
                if self.mouse_list.is_mouse_in_list(physical_id=m.physical_id):
                    # Compare with the first mouse
                    if self.sample_mouse_1.physical_id == m.physical_id:
                        if not (self.sample_mouse_1.physical_id == m.physical_id and
                                self.sample_mouse_1.handler == m.handler and
                                self.sample_mouse_1.genotype == m.genotype):
                            self.assertTrue(False)
                    # Compare with the second mouse
                    elif self.sample_mouse_2.physical_id == m.physical_id:
                        if not (self.sample_mouse_2.physical_id == m.physical_id and
                                self.sample_mouse_2.handler == m.handler and
                                self.sample_mouse_2.genotype == m.genotype):
                            self.assertTrue(False)
                    else:
                        # nothing has matched, asserted
                        self.assertTrue(False)

                    # Remove the mouse from the mouse list regardless
                    # of the reference, compare the id only
                    self.mouse_list.remove_mouse(m)
                else:
                    # nothing in the current mouse list, asserted
                    self.assertTrue(False)

            # must be 0 if everything matched perfectly
            if not (len(self.mouse_list) == 0):
                self.assertTrue(False)


##############################################################################################################
# Unit Test name: Model Adapter test case
# Target: Mouse, MouseList
# Description:
#              1. Populated a predefined mouse list
#              2. make sure the converted information in the xml file matched with the predefined mouse list
#              3. Check if the xml parser and object xml serilizer can work perfectly
##############################################################################################################
class ModelViewerTestCase(TestCase):
    # Setup function, insert required objects into the database
    def setUp(self) -> None:
        self.physical_id = 'abc'
        self.handler = 'Shih Han'
        self.gender = 'Male'
        self.mouseline = 'mouseline1'
        self.genotype = 'genotype1'
        self.birth_date = '2020-06-11'
        self.end_date = '2020-05-21'
        self.cog = '1'
        self.phenotype = 'Phenotyp1'
        self.project_title = 'abc'
        self.experiment = 'exprement1'
        self.comment = 'comment1'

        self.sample_mouse_1 = Mouse(physical_id=self.physical_id,
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.sample_mouse_2 = Mouse(physical_id=self.physical_id[::-1],
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.mouse_list = MouseList()
        self.mouse_list.add_mouse([self.sample_mouse_1, self.sample_mouse_2])

        self.adapter = XmlModelAdapter()
        self.viewer = XmlMouseViewer()

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly
    def test_viewer_mouse_matched(self):
        # open xml file
        # Convert mouse sample to xml and save it
        xml_data = self.viewer.transform(self.sample_mouse_1)
        with open('testing.xml', 'w') as w_open:
            w_open.write(xml_data)

        with open('testing.xml') as r_open:
            xml_raw_data = r_open.read()
            # transform the data into mouse object
            converted = self.adapter.transform(xml_raw_data)
            if not (self.sample_mouse_1.physical_id == converted.physical_id and
                    self.sample_mouse_1.handler == converted.handler and
                    self.sample_mouse_1.genotype == converted.genotype):
                self.assertTrue(False)

        os.remove('testing.xml')

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly
    def test_viewer_mouse_list_matched(self):
        # open xml file
        # Convert mouse sample to xml and save it
        xml_data = self.viewer.transform(self.mouse_list)
        with open('testing.xml', 'w') as w_open:
            w_open.write(xml_data)

        with open('testing.xml') as r_open:
            xml_raw_data = r_open.read()
            # transform the data into mouse object
            converted_list = self.adapter.transform(xml_raw_data)
            for m in converted_list:
                if self.mouse_list.is_mouse_in_list(physical_id=m.physical_id):
                    # Compare with the first mouse
                    if self.sample_mouse_1.physical_id == m.physical_id:
                        if not (self.sample_mouse_1.physical_id == m.physical_id and
                                self.sample_mouse_1.handler == m.handler and
                                self.sample_mouse_1.genotype == m.genotype):
                            self.assertTrue(False)
                    # Compare with the second mouse
                    elif self.sample_mouse_2.physical_id == m.physical_id:
                        if not (self.sample_mouse_2.physical_id == m.physical_id and
                                self.sample_mouse_2.handler == m.handler and
                                self.sample_mouse_2.genotype == m.genotype):
                            self.assertTrue(False)
                    else:
                        # nothing has matched, asserted
                        self.assertTrue(False)

                    # Remove the mouse from the mouse list regardless
                    # of the reference, compare the id only
                    self.mouse_list.remove_mouse(m)
                else:
                    # nothing in the current mouse list, asserted
                    self.assertTrue(False)

            # must be 0 if everything matched perfectly
            if not (len(self.mouse_list) == 0):
                self.assertTrue(False)

        os.remove('testing.xml')


##############################################################################################################
# Unit Test name: SQLlite Database test case
# Target: Mouse, MouseList
# Description:
#              1. Validation of Create, Update, Read and Delete of the mouse databse
##############################################################################################################
class SqliteDatabaserTestCase(TestCase):
    def setUp(self) -> None:
        self.physical_id = 'abc'
        self.handler = 'Shih Han'
        self.gender = 'Male'
        self.mouseline = 'mouseline1'
        self.genotype = 'genotype1'
        self.birth_date = '2020-06-11'
        self.end_date = '2020-05-21'
        self.cog = '1'
        self.phenotype = 'Phenotyp1'
        self.project_title = 'abc'
        self.experiment = 'exprement1'
        self.comment = 'comment1'

        self.sample_mouse_1 = Mouse(physical_id=self.physical_id,
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.sample_mouse_2 = Mouse(physical_id=self.physical_id[::-1],
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.mouse_list = MouseList()
        self.mouse_list.add_mouse([self.sample_mouse_1, self.sample_mouse_2])

        self.db_adapter = GenericSqliteConnector()
        self.adapter = XmlModelAdapter()
        self.viewer = XmlMouseViewer()

        self.db_adapter.create_mouse(self.mouse_list)

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly from the databse
    def test_get_mouse_list_from_db(self):
        mouse_output = self.db_adapter.get_all_mouse(True)
        if not (mouse_output == self.mouse_list):
            self.assertTrue(False)

    # Pass requirement
    # 1. Check if the mouse can be retrived correctly from the databse
    def test_create_list_into_db(self):
        self.sample_mouse_3 = Mouse(physical_id=self.physical_id + '1',
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.sample_mouse_4 = Mouse(physical_id=self.physical_id[::-1] + '3',
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.mouse_list.add_mouse([self.sample_mouse_3, self.sample_mouse_4])
        try:
            self.db_adapter.create_mouse(self.mouse_list)
        except DuplicationMouseError as e:
            print(e.message)

        mouse_output = self.db_adapter.get_all_mouse(True)
        if not (mouse_output == self.mouse_list):
            self.assertTrue(False)

        # cache integrity check
        mouse_output = self.db_adapter.get_all_mouse()
        if not (mouse_output == self.mouse_list):
            self.assertTrue(False)

    def test_update_mouse_list(self):
        # Force to get a new mouse list
        mouse_list_before = copy.deepcopy(self.db_adapter.get_all_mouse(True))

        self.sample_mouse_2_copy = copy.deepcopy(self.sample_mouse_2)
        self.sample_mouse_2_copy.handler = 'CBA'
        self.db_adapter.update_mouse(self.sample_mouse_2_copy)

        # Force to get a new mouse list
        mouse_list = self.db_adapter.get_all_mouse(True)
        mouse = mouse_list.get_mouse_by_id(self.sample_mouse_2_copy.physical_id)
        if not mouse.handler == 'CBA':
            self.assertTrue(False)

        if mouse_list_before == mouse_list:
            self.assertTrue(False)

    def test_update_mouse_list_list(self):
        # Force to get a new mouse list
        mouse_list_before = copy.deepcopy(self.db_adapter.get_all_mouse(True))

        self.sample_mouse_1_copy = copy.deepcopy(self.sample_mouse_1)
        self.sample_mouse_1_copy.handler = 'ABC'

        self.sample_mouse_2_copy = copy.deepcopy(self.sample_mouse_2)
        self.sample_mouse_2_copy.handler = 'CBA'

        updating_mouse_list = MouseList()
        updating_mouse_list.add_mouse([self.sample_mouse_1_copy, self.sample_mouse_2_copy])
        self.db_adapter.update_mouse(updating_mouse_list)

        # Force to get a new mouse list
        mouse_list = self.db_adapter.get_all_mouse(True)
        mouse = mouse_list.get_mouse_by_id(self.sample_mouse_1_copy.physical_id)
        if not mouse.handler == 'ABC':
            self.assertTrue(False)

        mouse = mouse_list.get_mouse_by_id(self.sample_mouse_2_copy.physical_id)
        if not mouse.handler == 'CBA':
            self.assertTrue(False)

        if mouse_list_before == mouse_list:
            self.assertTrue(False)

    def test_update_mouse_list_delete(self):
        self.db_adapter.delete_mouse(self.sample_mouse_1)
        self.db_adapter.delete_mouse(self.sample_mouse_2)

        mouselist = self.db_adapter.get_all_mouse()

        if not(mouselist.get_size() == 0):
            self.assertTrue(False)

        mouselist = self.db_adapter.get_all_mouse(True)

        if not(mouselist.get_size() == 0):
            self.assertTrue(False)

    def test_update_mouse_list_delete_list(self):

        to_be_deleted = MouseList()
        to_be_deleted.add_mouse([self.sample_mouse_1, self.sample_mouse_2])

        self.db_adapter.delete_mouse(to_be_deleted)

        mouselist = self.db_adapter.get_all_mouse()

        if not(mouselist.get_size() == 0):
            self.assertTrue(False)

        mouselist = self.db_adapter.get_all_mouse(True)

        if not(mouselist.get_size() == 0):
            self.assertTrue(False)

    def test_update_mouse_list_delete_particular_check(self):

        self.db_adapter.delete_mouse(self.sample_mouse_2)

        mouselist = self.db_adapter.get_all_mouse()

        if not(mouselist.get_size() == 1):
            self.assertTrue(False)

        mouse = mouselist.get_mouse_by_id(self.sample_mouse_1.physical_id)
        if mouse is None:
            self.assertTrue(False)

        mouse = mouselist.get_mouse_by_id(self.sample_mouse_2.physical_id)
        if mouse is not None:
            self.assertTrue(False)

        mouselist = self.db_adapter.get_all_mouse(True)

        if not(mouselist.get_size() == 1):
            self.assertTrue(False)

        mouse = mouselist.get_mouse_by_id(self.sample_mouse_1.physical_id)
        if mouse is None:
            self.assertTrue(False)

        mouse = mouselist.get_mouse_by_id(self.sample_mouse_2.physical_id)
        if mouse is not None:
            self.assertTrue(False)


##############################################################################################################
# Unit Test name: Moues Filter class test case
# Target: Mouse, MouseList
# Description:
#              1. Validation of filter functionality on the mouse list model
##############################################################################################################
class MouseFilterTestCase(TestCase):
    def setUp(self) -> None:
        self.physical_id = 'abc'
        self.handler = 'Shih Han'
        self.gender = 'Male'
        self.mouseline = 'mouseline1'
        self.genotype = 'genotype1'
        self.birth_date = '2020-06-11'
        self.end_date = '2020-05-21'
        self.cog = '1'
        self.phenotype = 'Phenotyp1'
        self.project_title = 'abc'
        self.experiment = 'exprement1'
        self.comment = 'comment1'

        self.sample_mouse_1 = Mouse(physical_id=self.physical_id,
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.sample_mouse_2 = Mouse(physical_id=self.physical_id[::-1],
                                    handler=self.handler,
                                    gender=self.gender,
                                    mouseline=self.mouseline,
                                    genotype=self.genotype,
                                    birth_date=self.birth_date,
                                    end_date=self.end_date,
                                    cog=self.cog,
                                    phenotype=self.phenotype,
                                    project_title=self.project_title,
                                    experiment=self.experiment,
                                    comment=self.comment)

        self.mouse_list = MouseList()
        self.mouse_list.add_mouse([self.sample_mouse_1, self.sample_mouse_2])
        self.filter = MouseFilter()

    def test_simple_mouse_filter_case(self):

        # Current mouse list contains mouse with physical_id of 'abc' and 'cba'

        # Test case 1
        # Retrieve only abc, filter physical_id by value of 'ab'
        mouse_list = self.filter.filter(
            self.mouse_list,
            FilterOption(
                column_name='physical_id',
                value='ab'
            ))

        if len(mouse_list) != 1:
            self.assertTrue(False)

        if mouse_list.get_mouse_by_id('abc') is None:
            self.assertTrue(False)
