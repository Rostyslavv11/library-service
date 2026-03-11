from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import CustomUserSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    if request.method == "GET":
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    serializer = CustomUserSerializer(
        request.user,
        data=request.data,
        partial=request.method == "PATCH",
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)

