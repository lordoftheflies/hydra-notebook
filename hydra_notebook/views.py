import io
import json
import os

import nbformat
from django.conf import settings
from django.shortcuts import render
from nbconvert import HTMLExporter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from rest_framework import viewsets as rest_viewsets, views as rest_views
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

formatter = HtmlFormatter()
lexer = PythonLexer()


def list_notebooks(request):
    contents = os.listdir(settings.NOTEBOOKS_ROOT)

    return render(request, template_name='hydra_notebook/index.html', context={
        'notebooks': contents
    })


# Create your views here.
def show_notebook(request, fname):
    """display a short summary of the cells of a notebook"""
    with io.open(os.path.join(settings.NOTEBOOKS_ROOT, fname), 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
        html_exporter = HTMLExporter()
        html_exporter.template_file = 'basic'

        # 3. Process the notebook we loaded earlier
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return render(request, template_name='hydra_notebook/detail.html', context={
            'body': body,
            'style': resources['inlining']['css'][0]
        })


@api_view(['GET'])
def list_notebooks_json(request):
    contents = os.listdir(settings.NOTEBOOKS_ROOT)
    return Response(contents)


@api_view(['GET'])
def show_notebook_json(request, fname):
    """display a short summary of the cells of a notebook"""
    notebook = json.load(os.path.join(settings.NOTEBOOKS_ROOT, fname))
    return Response(notebook)

class FileUploadView(rest_views.APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        with io.open(file=os.path.join(settings.NOTEBOOKS_ROOT, filename), mode='wb+', encoding='utf-8') as file_handler:
            for chunk in file_obj.chunks():
                file_handler.write(chunk)
        # ...
        # do some stuff with uploaded file
        # ...
        return Response(status=204)