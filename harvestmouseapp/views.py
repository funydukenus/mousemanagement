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
    harvested_mouse = HarvestedMouse.objects.all()
    harvested_mouse_serializer = HarvestedMouseSerializer(harvested_mouse, many=True)
    return Response(harvested_mouse_serializer.data)


@api_view(['POST'])
def harvested_mouse_insertion(request):
    """
    Insertion of the harvested mouse into database
    """
    incoming_serialzier = HarvestedMouseSerializer(data=request.data)
    if incoming_serialzier.is_valid():
        incoming_serialzier.save()
        return Response(incoming_serialzier.data, status=status.HTTP_201_CREATED)
    else:
        return Response(incoming_serialzier.errors, status=status.HTTP_400_BAD_REQUEST)
