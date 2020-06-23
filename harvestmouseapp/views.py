from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import HarvestedMouse
from .serializers import HarvestedMouseSerializer
from django import forms
from datetime import datetime
import pandas as pd


# With api view wrapper, method validation is auto-checked
# wrong API request will auto return Unathorized method
@api_view(['GET'])
def harvested_mouse_list(request):
    """
    List all the harvested mouse
    """
    harvested_mouse_list_arr = HarvestedMouse.objects.all()

    if request.query_params:
        filter_set = {}
        for item in request.query_params:
            value_key_word = request.query_params[item]
            key = item.split(',')[0]
            comp = item.split(',')[1]
            if comp == '1':
                comp = '__contains'
            elif comp == '2':
                comp = '__gte'
            elif comp == '3':
                comp = '__lte'
            elif comp == '4':
                comp = '__startswith'
            filter_set[key + comp] = value_key_word
        harvested_mouse_list_arr = harvested_mouse_list_arr.filter(**filter_set)

    harvested_mouse_serializer = HarvestedMouseSerializer(harvested_mouse_list_arr, many=True)
    return Response(harvested_mouse_serializer.data)


@api_view(['POST'])
def harvested_mouse_insertion(request):
    """
    Insertion of the harvested mouse into database
    """
    data = request.data.get("harvestedmouselist") if 'harvestedmouselist' in request.data else request.data
    many = isinstance(data, list)
    incoming_serializer = HarvestedMouseSerializer(data=data, many=many)

    if incoming_serializer.is_valid():
        incoming_serializer.save()
        return Response(incoming_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(incoming_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def harvested_mouse_update(request):
    """
    Update of the harvested mouse into database
    """
    data = request.data.get("harvestedmouselist") if 'harvestedmouselist' in request.data else request.data
    many = isinstance(data, list)
    if not many:
        if update_mouse(data=data):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        for idx, item in enumerate(data):
            if not update_mouse(data=item):
                return Response(idx-1, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
def harvested_mouse_delete(request):
    """
    Delete of the selected harvested mouse
    """
    data = request.data.get("harvestedmouselist") if 'harvestedmouselist' in request.data else request.data
    many = isinstance(data, list)
    if not many:
        if delete_mouse(data=data):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        for idx, item in enumerate(data):
            if not delete_mouse(data=item):
                return Response(idx-1, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
def harvested_all_mouse_delete(request):
    """
    Deletion of the harvested mouse into database
    """
    HarvestedMouse.objects.all().delete()

    if HarvestedMouse.objects.all().count() == 0:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def harvested_import_mouse(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid() and request.FILES['file'].name.endswith('.csv'):
        filename = save_uploaded_file(request.FILES['file'])
        return insert_external_data(filename)
    return Response(status=status.HTTP_400_BAD_REQUEST)


# Helper
def update_mouse(data):
    """
    Helper function to update the given mouse data
    """
    instance = HarvestedMouse.objects.get(pk=data['id'])
    incoming_serializer = HarvestedMouseSerializer(instance, data=data)
    if incoming_serializer.is_valid():
        incoming_serializer.save()
        return True
    else:
        return False


def delete_mouse(data):
    """
    Helper function to delete the given mouse data
    """
    if HarvestedMouse.objects.filter(pk=data['id']).count() == 0:
        return False
    else:
        instance = HarvestedMouse.objects.get(pk=data['id'])
        instance.delete()
        return True


class UploadFileForm(forms.Form):
    """
    UploadFileForm class to validate
    """
    file = forms.FileField()


def save_uploaded_file(f):
    with open('input.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return 'input.csv'


def convert_csv_to_json_arr(filename):
    csv_file = pd.read_csv(filename)

    csv_file = csv_file.fillna('No Data')

    arr = []

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

        data = {
            'handler': row['Handled by'],
            'physicalId': row['physical_id'],
            'gender': gender,
            'mouseLine': row['mouseline'],
            'genoType': row['Genotype'],
            'birthDate': str(birth_date.date()),
            'endDate': str(end_date.date()),
            'confirmationOfGenoType': row['Confirmation of genotype'],
            'phenoType': row['phenotype'],
            'projectTitle': row['project_title'],
            'experiment': row['Experiment'],
            'comment': row['comment'],
            'freezeRecord': {
                'liver': row['Freeze Liver'],
                'liverTumor': row['Freeze Liver tumour'],
                'others': row['Freeze Others']
            },
            'pfaRecord': {
                'liver': row['PFA Liver'],
                'liverTumor': row['PFA Liver tumour'],
                'smallIntestine': row['PFA Small intestine'],
                'smallIntestineTumor': row['PFA SI tumour'],
                'skin': row['PFA Skin'],
                'skinHair': row['PFA Skin_Hair'],
                'others': row['PFA Others']
            }
        }
        arr.append(data)

    return arr


def insert_external_data(filename):
    arr = convert_csv_to_json_arr(filename)
    many = False
    if isinstance(arr, list):
        many = True

    incoming_serializer = HarvestedMouseSerializer(data=arr, many=many)
    if incoming_serializer.is_valid():
        incoming_serializer.save()
        return Response(incoming_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(incoming_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_data_option_list(request):
    # Get the list of mouse object first
    harvesed_mouse_list = list(HarvestedMouse.objects.all())
    mouseline_list = []
    genotype_list = []
    phenotype_list = []
    projecttitle_list = []
    handler_list = []
    experiement_list = []
    data = {}

    for harvestedMouse in harvesed_mouse_list:
        mouseline_list.append(harvestedMouse.mouseLine)
        genotype_list.append(harvestedMouse.genoType)
        phenotype_list.append(harvestedMouse.phenoType)
        projecttitle_list.append(harvestedMouse.projectTitle)
        handler_list.append(harvestedMouse.handler)
        experiement_list.append(harvestedMouse.experiment)

    data['mouseLineList'] = list(set(mouseline_list))
    data['genoTypeList'] = list(set(genotype_list))
    data['phenoTypeList'] = list(set(phenotype_list))
    data['projectTitleList'] = list(set(projecttitle_list))
    data['handlerList'] = list(set(handler_list))
    data['ExperiementList'] = list(set(experiement_list))

    return Response(data)
