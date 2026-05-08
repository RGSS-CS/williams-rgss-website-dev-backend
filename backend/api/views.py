from rest_framework.response import Response
from rest_framework.decorators import api_view
from clubs.models import Club
from .serializers import ClubSerializer

@api_view(['GET'])
def getData(request):
    items = Club.objects.all()
    serilizer = ClubSerializer(items, many=True)
    return Response(serilizer.data)