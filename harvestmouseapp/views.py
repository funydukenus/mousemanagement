from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from usermanagement.views import get_random_alphanumeric_string, check_if_user_is_logged, get_response_frame_data, \
    return_response
from .models import HarvestedMouse
from .mvc_model.Error import DuplicationMouseError, MouseNotFoundError
from .mvc_model.model import Mouse, AdvancedRecord, Record
from django import forms
from datetime import datetime
import pandas as pd

from harvestmouseapp.mvc_model.databaseAdapter import GenericSqliteConnector
from harvestmouseapp.mvc_model.mouseAdapter import JsonModelAdapter
from harvestmouseapp.mvc_model.mouseController import MouseController
from harvestmouseapp.mvc_model.mouseViewer import JsonMouseViewer
from .mvc_model.mouseFilter import FilterOption, MouseFilter, get_enum_by_value
import os


mouse_controller_g = MouseController()
mouse_controller_g.set_db_adapter(GenericSqliteConnector())
mouse_controller_g.set_mouse_viewer(JsonMouseViewer())
mouse_controller_g.set_model_adapter(JsonModelAdapter())
mouse_controller_g.set_mouse_filter(MouseFilter())


class UploadFileForm(forms.Form):
    """
    UploadFileForm class to validate
    """
    file = forms.FileField()


@api_view(['GET'])
def harvested_mouse_get_total_num(request):
    """
    List all the harvested mouse
    Filtered option:
    by Json
    { 'filter': '[column_name_1]@[value_1]@[filter_option_1]$[column_name_2][value_2][filter_option_2]' }
    """
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    response_success = False

    params_key = {'filter'}
    if user is not None:
        filter_options = construct_filter_option(request, params_key)
        try:
            mouse_list_size = mouse_controller_g.get_num_of_mouse(filter_option=filter_options)
            response_success = True
            payload = mouse_list_size
        except Exception as err:
            payload = "Unknown database error"
    else:
        payload = "Authorization failed"

    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def harvested_mouse_force_list(request):
    """
    List all the harvested mouse
    Filtered option:
    by Json
    { 'filter': '[column_name_1]@[value_1]@[filter_option_1]$[column_name_2][value_2][filter_option_2]' }
    """
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    response_success = False

    params_key = {'filter'}
    params_key_for_pagination = {'page_index', 'page_size'}
    if user is not None:
        filter_options = construct_filter_option(request, params_key)
        try:
            if request.query_params.keys() >= params_key_for_pagination:
                page_size = int(request.query_params['page_size'])
                page_index = int(request.query_params['page_index'])
                mouse_list = mouse_controller_g.get_mouse_for_transfer(filter_option=filter_options, page_size=page_size, page_index=page_index)
            else:
                mouse_list = mouse_controller_g.get_mouse_for_transfer(filter_option=filter_options)
            response_success = True
            payload = mouse_list
        except Exception as err:
            payload = "Unknown database error"
    else:
        payload = "Authorization failed"

    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def harvested_mouse_insertion(request):
    """
    Insertion of the harvested mouse into database
    """
    try:
        mouse_controller_g.create_mouse(request.data)
        return Response(status=status.HTTP_201_CREATED)
    except DuplicationMouseError as e:
        return Response(data=e.message, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def harvested_mouse_update(request):
    """
    Update of the harvested mouse into database
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)
    response_frame = get_response_frame_data()
    response_success = False
    payload = ""

    try:
        mouse_controller_g.update_mouse(request.data)
        response_success = True
    except MouseNotFoundError:
        payload = "Target mouse is not found"
    except ValueError:
        payload = "Unknown database error"
    except DatabaseError:
        payload = "Unknown database error"

    return return_response(response_frame, response_success, payload)


@api_view(['DELETE'])
def harvested_mouse_delete(request):
    """
    Delete of the selected harvested mouse
    """
    response_frame = get_response_frame_data()
    response_success = False
    payload = ""

    try:
        mouse_controller_g.delete_mouse(request.data)
        response_success = True
    except MouseNotFoundError as e:
        payload = "Target mouse is not found"
    except ValueError as e:
        payload = "Unknown database error"
    except DatabaseError as e:
        payload = "Unknown database error"

    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def get_data_option_list(request):
    """
    Providing the selecting option to the client
    """
    response_frame = get_response_frame_data()
    response_success = False

    try:
        data = {}
        # Get the list of mouse object first
        data['mouseLineList'] = mouse_controller_g.get_distinct_data_list('mouseLine')
        data['genoTypeList'] = mouse_controller_g.get_distinct_data_list('genoType')
        data['phenoTypeList'] = mouse_controller_g.get_distinct_data_list('phenoType')
        data['projectTitleList'] = mouse_controller_g.get_distinct_data_list('projectTitle')
        data['handlerList'] = mouse_controller_g.get_distinct_data_list('handler')
        data['experiementList'] = mouse_controller_g.get_distinct_data_list('experiment')

        response_success = True
        payload = data
    except Exception as error:
        payload = "Unknown database error"
    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def harvested_import_mouse(request):
    """
    Handling of the process of importing external
    csv file for insertion of list of mouse
    """
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    response_success = False
    payload = ""
    filename = ""
    if user is not None:
        try:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                filename = get_random_alphanumeric_string(20, 20) + request.FILES['file'].name
                with transaction.atomic():
                    user.userextend.uploaded_file_name = save_uploaded_file(request.FILES['file'], filename)
                    user.save()

                # get again the user to double confirm
                user = User.objects.get(id=user.id)
                if user.userextend.uploaded_file_name == filename:
                    num_csv_file_rows = len(pd.read_csv(user.userextend.uploaded_file_name))
                    if num_csv_file_rows >= 200:
                        payload = 'Please restrict number entires to max 200 entries'
                    else:
                        response_success = True
                else:
                    payload = 'Unknown database error'
            else:
                payload = 'File missing in the form'
        except Exception as error:
            payload = 'Unknown database error'
    else:
        payload = "Authorization failed"

    if not response_success:
        if os.path.exists(filename):
            os.remove(filename)

    return return_response(response_frame, response_success, payload)


@api_view(['POST'])
def parsing_imported_mouse(request):
    user = check_if_user_is_logged(request)
    response_frame = get_response_frame_data()
    response_success = False
    payload = ""
    if user is not None:
        # Get the last saved filed
        filename = user.userextend.uploaded_file_name
        csv_file = pd.read_csv(filename)
        csv_file = csv_file.fillna('No Data')
        payload = convert_csv_to_json_arr(csv_file)

        if os.path.exists(filename):
            os.remove(filename)

        response_success = True
    else:
        payload = "Authorization failed"

    return return_response(response_frame, response_success, payload)


@api_view(['GET'])
def clear_all_mouse(request):
    try:
        HarvestedMouse.objects.all().delete()
        return Response(status=status.HTTP_200_OK)
    except TypeError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Helper
def save_uploaded_file(f, filename):
    """
    Helper function to save the transmitting csv file
    from the client
    """
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return filename


############################################
# Function name: create_mouse_object
# Description:
#              This function creats the mouse object and transform based on the transfom object
############################################
def create_mouse_object(physical_id, handler, gender, mouseline, genotype,
                        birth_date, end_date, cog, phenotype, project_title, comment, experiment,
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


def convert_csv_to_json_arr(csv_file):
    """
    Helper function to parse the csv file and
    save into database
    """
    error_msg = ""
    for index, row in csv_file.iterrows():
        try:
            gender = row['gender']
            if gender == 'Male':
                gender = 'M'
            else:
                gender = 'F'

            birth_date = convert_diff_datetime_format(row['birthdate'])
            end_date = convert_diff_datetime_format(row['End date'])

            mouse = create_mouse_object(
                handler=row['Handled by'],
                physical_id=row['physical_id'],
                gender=gender,
                mouseline=row['mouseline'],
                genotype=row['Genotype'],
                birth_date=birth_date.date(),
                end_date=end_date.date(),
                cog=row['Confirmation of genotype'],
                phenotype=row['phenotype'],
                project_title=row['project_title'],
                experiment=row['experiment'],
                comment=row['comment'],
                pfa_record=AdvancedRecord(
                    row['PFA Liver'],
                    row['PFA Liver tumour'],
                    row['PFA Small intestine'],
                    row['PFA SI tumour'],
                    row['PFA Skin'],
                    row['PFA Skin_Hair'],
                    row['PFA Others']
                ),
                freeze_record=Record(
                    row['Freeze Liver'],
                    row['Freeze Liver tumour'],
                    row['Freeze Others']
                )
            )

            # convert to json format
            json_viewer = JsonMouseViewer()

            mouse_controller_g.create_mouse(json_viewer.transform(mouse))
        except ValueError:
            error_msg += "Format Error Id:" + row['physical_id'] + "\n"
        except DuplicationMouseError:
            error_msg += "Duplicated Error Id:" + row['physical_id'] + "\n"
            continue

    return error_msg


def convert_diff_datetime_format(str_datetime):
    for fmt in ('%m-%d-%Y', '%m/%d/%Y', '%b-%d-%Y', '%b/%d/%Y',
                '%B-%d-%Y', '%B/%d/%Y', '%d-%b-%Y', '%d/%b/%Y',
                '%d-%B-%Y', '%d/%B/%Y'):
        try:
            return datetime.strptime(str_datetime, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def construct_filter_option(request, params_key):
    """
    Creates the filter option list based on the
    query param
    """
    option_found = False
    filter_options = None
    if len(request.query_params) != 0:
        option_found = True

    if option_found:
        if request.query_params.keys() >= params_key:
            option_filter_str = request.query_params['filter']
            split_filter_options = option_filter_str.split('$')
            filter_options = []
            if isinstance(split_filter_options, list):

                for filter_o in split_filter_options:
                    split_detailed_option = filter_o.split('@')

                    filter_option = FilterOption(
                        column_name=split_detailed_option[0],
                        value=split_detailed_option[1]
                    )
                    try:
                        filter_option.filter_type = get_enum_by_value(int(split_detailed_option[2]))
                    except IndexError:
                        pass

                    filter_options.append(filter_option)

    return filter_options