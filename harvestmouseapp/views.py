from django.db import DatabaseError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
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


# With api view wrapper, method validation is auto-checked
# wrong API request will auto return Unathorized method
@api_view(['GET'])
def harvested_mouse_list(request):
    """
    List all the harvested mouse
    { 'filter': '[column_name_1]@[value_1]@[filter_option_1]$[column_name_2][value_2][filter_option_2]' }
    """
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
    mouse_list = mouse_controller_g.get_mouse_for_transfer(force=True)

    return Response(mouse_list)


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
    try:
        mouse_list_in_xml = mouse_controller_g.get_mouse_for_transfer()
        mouse_controller_g.delete_mouse(mouse_list_in_xml)
    except ValueError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)
    except DatabaseError as e:
        return Response(data='DB Error', status=status.HTTP_400_BAD_REQUEST)

    if mouse_controller_g.get_num_total_mouse() == 0:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def harvested_import_mouse(request):
    """
    Handling of the process of importing external
    csv file for insertion of list of mouse
    """
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid() and request.FILES['file'].name.endswith('.csv'):
        filename = save_uploaded_file(request.FILES['file'])
        return insert_external_data(filename)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_data_option_list(request):
    """
    Providing the selecting option to the client
    """
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


# Helper
def save_uploaded_file(f):
    """
    Helper function to save the transmitting csv file
    from the client
    """
    with open('input.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return 'input.csv'


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


def convert_csv_to_json_arr(filename):
    """
    Helper function to parse the csv file and
    save into database
    """
    csv_file = pd.read_csv(filename)

    csv_file = csv_file.fillna('No Data')

    mouse_list = MouseList()

    for index, row in csv_file.iterrows():
        gender = row['gender']
        if gender == 'Male':
            gender = 'M'
        else:
            gender = 'F'
        try:
            birth_date = datetime.strptime(row['birthdate'], '%m-%d-%Y')
            end_date = datetime.strptime(row['End date'], '%m-%d-%Y')
        except ValueError:
            continue

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

        mouse_list.add_mouse(mouse)

    return mouse_list


def insert_external_data(filename):
    """
    Handling of the external csv file and return status based on the
    result of the processing file
    """
    mouse_list = convert_csv_to_json_arr(filename)
    try:
        mouse_controller_g.create_mouse(mouse_list)
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
