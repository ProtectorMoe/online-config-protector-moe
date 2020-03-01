from time import time
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter

from .models import Path
from .util import try_catch
from .serializer import PathGetSerializers, LikeSerializers, PathListSerializers


class StanderPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'p'
    max_page_size = 1000


class PathListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    获取配置文件列表
    """
    lookup_field = 'id'
    queryset = Path.objects.all().order_by('-last_download')
    serializer_class = PathListSerializers
    pagination_class = StanderPageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ['author', 'title']


class PathViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = 'id'
    queryset = Path.objects.all()
    serializer_class = PathGetSerializers

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.last_download = int(time())
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LikeView(APIView):
    @try_catch
    def get(self, request):
        like_serializers = LikeSerializers(request.data)
        if like_serializers.is_valid():
            result = like_serializers.save()
            return Response({'error': 0, 'result': result}, status=status.HTTP_200_OK)
        return Response({'errmsg': "表单错误"}, status=status.HTTP_400_BAD_REQUEST)


class LikeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LikeSerializers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




