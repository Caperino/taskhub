from django.shortcuts import render
import re
from rest_framework import viewsets
from rest_framework.response import Response
from TaskHub import urls
from . import renderers


# Create your views here.
class ApiView(viewsets.ViewSet):

    def list(self, request):
        endpoints = []
        for pattern in urls.urlpatterns:
            endpoint = str(pattern.pattern)
            # Include only api/ views and include only top-level endpoints:
            if "api/" in endpoint and re.search("<.*>", endpoint) is None:
                endpoints.append("http://localhost:8000/%s" % endpoint)
        return Response(endpoints)


class EmployeeViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving employees.
    """
    renderer_classes = [renderers.PNGRenderer, renderers.JPEGRenderer]

    def list(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def create(self, request):
        pass

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


class ImageUploadViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for uploading images.
    """
    renderer_classes = [renderers.PNGRenderer, renderers.JPEGRenderer]

    def download_pfp(self, request):
        """

        :param request:
        :return:
        """
        pass

    def upload_pfp(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return:
        """
        pass

    def download_proof(self, request):
        """

        :param request:
        :return:
        """
        pass

    def upload_proof(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return:
        """
        pass

    def destroy(self, request, pk=None):
        """
        YET UNUSED
        :param request:
        :param pk:
        :return:
        """
        pass