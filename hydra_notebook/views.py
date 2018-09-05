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

formatter = HtmlFormatter()
lexer = PythonLexer()


class NotebookFileManager():

    @property
    def _files(self):
        return os.listdir(settings.NOTEBOOKS_ROOT)

    def all(self):
        notebooks = [NotebookFileModel(filename=file) for file in self._files]
        return notebooks

    def get(self, name):
        matched = [f for f in self._files if f.startswith(name)]
        return NotebookFileModel(filename=matched[0])


class NotebookFileModel:
    objects = NotebookFileManager()

    def __init__(self, filename=None, name=None, extension=None):
        self.name = os.path.splitext(filename)[0] if name is None else name
        self.extension = os.path.splitext(filename)[1] if extension is None else extension

    @property
    def filename(self):
        return "%s%s" % (self.name, self.extension)

    @property
    def abspath(self):
        return os.path.join(settings.NOTEBOOKS_ROOT, self.filename)

    def read(self):
        with io.open(self.abspath, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        return notebook


def list_notebooks(request):
    return render(request, template_name='hydra_notebook/index.html', context={
        'notebooks': NotebookFileModel.objects.all()
    })


# Create your views here.
def notebook_html(request, name):
    notebook = NotebookFileModel(name=name, extension='.ipynb').read()
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'

    # 3. Process the notebook we loaded earlier
    (body, resources) = html_exporter.from_notebook_node(notebook)

    return render(request, template_name='hydra_notebook/detail.html', context={
        'body': body,
        'style': resources['inlining']['css'][0]
    })


def notebook_script(request, name):
    notebook = NotebookFileModel(name=name, extension='.ipynb').read()
    html_exporter = ScriptExporter()

    # 3. Process the notebook we loaded earlier
    (body, resources) = html_exporter.from_notebook_node(notebook)

    return HttpResponse(body)


def notebook_script_download(request, name):
    model = NotebookFileModel(name=name, extension='.ipynb')
    notebook = model.read()

    html_exporter = ScriptExporter()
    (body, resources) = html_exporter.from_notebook_node(notebook)

    response = HttpResponse(body, content_type=notebook['metadata']['language_info']['mimetype'])
    response['Content-Disposition'] = 'attachment; filename=%s%s' % (
        name,
        notebook['metadata']['language_info']['file_extension'],

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
