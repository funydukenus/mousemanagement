from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import HarvestedMouse
from .serializers import HarvestedMouseSerializer

# With api view wrapper, method validation is auto-checked
# wrong API request will auto return Unathorized method
@api_view(['GET'])
def harvested_mouse_list(request):
    """
    List all the harvested mouse
    """
    harvested_mouse_list = HarvestedMouse.objects.all()

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
        harvested_mouse_list = harvested_mouse_list.filter(**filter_set)

    harvested_mouse_serializer = HarvestedMouseSerializer(harvested_mouse_list, many=True)
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
    HarvestedMouse.objects.all().delete()

    if HarvestedMouse.objects.all().count() == 0:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# Helper
def update_mouse(data):
    instance = HarvestedMouse.objects.get(pk=data['id'])
    incoming_serializer = HarvestedMouseSerializer(instance, data=data)
    if incoming_serializer.is_valid():
        incoming_serializer.save()
        return True
    else:
        return False


def delete_mouse(data):
    if HarvestedMouse.objects.filter(pk=data['id']).count() == 0:
        return False
    else:
        instance = HarvestedMouse.objects.get(pk=data['id'])
        instance.delete()
        return True


