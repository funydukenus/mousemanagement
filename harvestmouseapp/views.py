from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from usermanagement.views import get_random_alphanumeric_string
from .mvc_model.Error import DuplicationMouseError, MouseNotFoundError
from .mvc_model.model import Mouse, AdvancedRecord, Record, MouseList
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


def _check_if_user_is_login(session):
    try:
        user = User.objects.get(username=session['username'])
        if user.is_active and user.is_authenticated and user.is_staff:
            return True
        else:
            return False
    except User.DoesNotExist:
        return False
    except KeyError:
        return False


# With api view wrapper, method validation is auto-checked
# wrong API request will auto return Unathorized method
@api_view(['GET'])
def harvested_mouse_list(request):
    """
    List all the harvested mouse
    { 'filter': '[column_name_1]@[value_1]@[filter_option_1]$[column_name_2][value_2][filter_option_2]' }
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    option_found = False
    fitler_options = None
    if len(request.query_params) != 0:
        option_found = True

    if option_found:
        if 'filter' in request.query_params.keys():
            option_filter_str = request.query_params['filter']
            split_filter_options = option_filter_str.split('$')
            fitler_options = []
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

                    fitler_options.append(filter_option)

    mouse_list = mouse_controller_g.get_mouse_for_transfer(filter_option=fitler_options)

    return Response(mouse_list)


@api_view(['GET'])
def harvested_mouse_force_list(request):
    """
    List all the harvested mouse
    Filtered option:
    by Json
    { 'filter': '[column_name_1]@[value_1]@[filter_option_1]$[column_name_2][value_2][filter_option_2]' }
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    option_found = False
    fitler_options = None
    if len(request.query_params) != 0:
        option_found = True

    if option_found:
        if 'filter' in request.query_params.keys():
            option_filter_str = request.query_params['filter']
            split_filter_options = option_filter_str.split('$')
            fitler_options = []
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

                    fitler_options.append(filter_option)

    mouse_list = mouse_controller_g.get_mouse_for_transfer(force=True, filter_option=fitler_options)

    return Response(mouse_list)


@api_view(['POST'])
def harvested_mouse_insertion(request):
    """
    Insertion of the harvested mouse into database
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

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

    try:
        mouse_controller_g.update_mouse(request.data)
        return Response(status=status.HTTP_200_OK)
    except MouseNotFoundError as e:
        return Response(data=e, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def harvested_mouse_delete(request):
    """
    Delete of the selected harvested mouse
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        mouse_controller_g.delete_mouse(request.data)
        return Response(status=status.HTTP_200_OK)
    except MouseNotFoundError as e:
        return Response(data=e, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def harvested_all_mouse_delete(request):
    """
    Deletion of the harvested mouse into database
    """
    """
    Delete of the selected harvested mouse
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        mouse_list_in_xml = mouse_controller_g.get_mouse_for_transfer(force=True)
        mouse_controller_g.delete_mouse(mouse_list_in_xml)
    except ValueError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)

    if mouse_controller_g.get_num_total_mouse() == 0:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_data_option_list(request):
    """
    Providing the selecting option to the client
    """
    # if not _check_if_user_is_login(request.session):
    #    return Response(status=status.HTTP_401_UNAUTHORIZED)

    # Get the list of mouse object first
    harvesed_mouse_list = mouse_controller_g.get_mouse_for_transfer(transform=False)
    mouseline_list = []
    genotype_list = []
    phenotype_list = []
    projecttitle_list = []
    handler_list = []
    experiement_list = []
    data = {}

    for harvestedMouse in harvesed_mouse_list:
        mouseline_list.append(harvestedMouse.mouseline)
        genotype_list.append(harvestedMouse.genotype)
        phenotype_list.append(harvestedMouse.phenotype)
        projecttitle_list.append(harvestedMouse.project_title)
        handler_list.append(harvestedMouse.handler)

    data['mouseLineList'] = list(set(mouseline_list))
    data['genoTypeList'] = list(set(genotype_list))
    data['phenoTypeList'] = list(set(phenotype_list))
    data['projectTitleList'] = list(set(projecttitle_list))
    data['handlerList'] = list(set(handler_list))

    return Response(data)


@api_view(['POST'])
def harvested_import_mouse(request):
    """
    Handling of the process of importing external
    csv file for insertion of list of mouse
    """
    try:
        user_id = request.session['_auth_user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['file'].name + get_random_alphanumeric_string(20, 20)
            user.userextend.uploaded_file_name = save_uploaded_file(request.FILES['file'], filename)
            user.save()

            return Response(status=status.HTTP_200_OK)
    except KeyError:
        return Response(data="No session", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def parsing_imported_mouse(request):
    try:
        user_id = request.session['_auth_user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Get the last saved filed
        filename = user.userextend.uploaded_file_name
        csv_file = pd.read_csv(filename)
        csv_file = csv_file.fillna('No Data')

        data = { 'error_msg': convert_csv_to_json_arr(csv_file) }

        if os.path.exists(filename):
            os.remove(filename)

        return Response(data=data, status=status.HTTP_200_OK)
    except KeyError:
        return Response(data="No session", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def gets_mouse_csv_info(request):
    try:
        user_id = request.session['_auth_user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Get the last saved filed
        filename = user.userextend.uploaded_file_name
        csv_file = pd.read_csv(filename)

        return Response(data=len(csv_file), status=status.HTTP_200_OK)
    except KeyError:
        return Response(data="No session", status=status.HTTP_400_BAD_REQUEST)


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

            birth_date = datetime.strptime(row['birthdate'], '%m-%d-%Y')
            end_date = datetime.strptime(row['End date'], '%m-%d-%Y')

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
