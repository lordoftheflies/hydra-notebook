import io
import os

import nbformat
from django.conf import settings
from django.shortcuts import render
from nbconvert import HTMLExporter
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer

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
