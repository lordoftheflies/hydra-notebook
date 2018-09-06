import io
import json
import os

import nbformat
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from nbconvert import HTMLExporter, ScriptExporter, PythonExporter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer
from rest_framework import viewsets as rest_viewsets, views as rest_views
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from hydra_notebook.core import NotebookFileModel, NotebookFileManager

formatter = HtmlFormatter()
lexer = PythonLexer()

notebook_manager = NotebookFileManager.create()

def list_notebooks(request):
    return render(request, template_name='hydra_notebook/index.html', context={
        'notebooks': notebook_manager.all()
    })


# Create your views here.
def notebook_html(request, name):
    model = NotebookFileModel(name=name, extension='.ipynb')

    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'

    # 3. Process the notebook we loaded earlier
    (body, resources) = model.export(exporter=html_exporter)

    return render(request, template_name='hydra_notebook/detail.html', context={
        'body': body,
        'style': resources['inlining']['css'][0]
    })


def notebook_script(request, name):
    model = NotebookFileModel(name=name, extension='.ipynb')
    return HttpResponse(model.notebook)


def notebook_script_download(request, name):
    model = NotebookFileModel(name=name, extension='.ipynb')
    response = HttpResponse(model.script, content_type=model.notebook['metadata']['language_info']['mimetype'])
    response['Content-Disposition'] = 'attachment; filename=%s%s' % (
        name,
        model.notebook['metadata']['language_info']['file_extension'],

    )
    return response


@api_view(['GET'])
def list_notebooks_json(request):
    contents = os.listdir(settings.NOTEBOOKS_ROOT)
    return Response(contents)


@api_view(['GET'])
def show_notebook_json(request, name):
    """display a short summary of the cells of a notebook"""
    EXTENSION = 'ipynb'
    with io.open(file=os.path.join(settings.NOTEBOOKS_ROOT, ('%s.%s' % (name, EXTENSION))), mode='r',
                 encoding='utf-8') as file_handler:
        notebook = json.load(file_handler)
    return Response(notebook)


class FileUploadView(rest_views.APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        with io.open(file=os.path.join(settings.NOTEBOOKS_ROOT, filename), mode='wb+',
                     encoding='utf-8') as file_handler:
            for chunk in file_obj.chunks():
                file_handler.write(chunk)
        # ...
        # do some stuff with uploaded file
        # ...
        return Response(status=204)
