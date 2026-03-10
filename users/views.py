from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import CustomUserSerializer
from .models import CustomUser


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


@api_view(["GET", "PUT", "PATCH"])
def my_profile(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)

