from django.shortcuts import render
import re
from rest_framework import viewsets
from rest_framework.response import Response
from TaskHub import urls


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
