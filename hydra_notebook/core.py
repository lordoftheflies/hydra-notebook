import io, os, sys, types

import nbformat
from IPython import get_ipython
from django.conf import settings
from nbconvert import ScriptExporter
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat import read, NotebookNode
from IPython.core.interactiveshell import InteractiveShell
from nbformat import v4 as nbf
from . import exceptions


def find_notebook(fullname, path=None):
    """find a notebook, given its fully qualified name and an optional path

    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo Bar" if Foo_Bar
    does not exist.
    """
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for d in path:
        nb_path = os.path.join(d, name + ".ipynb")
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find "Notebook Name.ipynb"
        nb_path = nb_path.replace("_", " ")
        if os.path.isfile(nb_path):
            return nb_path


class NotebookLoader(object):
    """Module Loader for Jupyter Notebooks"""

    def __init__(self, path=None):
        self.shell = InteractiveShell.instance()
        self.path = path

    def load_module(self, fullname):
        """import a notebook as a module"""
        path = find_notebook(fullname, self.path)

        print("importing Jupyter notebook from %s" % path)

        # load the notebook object
        with io.open(path, 'r', encoding='utf-8') as f:
            nb = read(f, 4)

        # create the module and add it to sys.modules
        # if name in sys.modules:
        #    return sys.modules[name]
        mod = types.ModuleType(fullname)
        mod.__file__ = path
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        sys.modules[fullname] = mod

        # extra work to ensure that magics that would affect the user_ns
        # actually affect the notebook module's ns
        save_user_ns = self.shell.user_ns
        self.shell.user_ns = mod.__dict__

        try:
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    # transform the input to executable Python
                    code = self.shell.input_transformer_manager.transform_cell(cell.source)
                    # run the code in themodule
                    exec(code, mod.__dict__)
        finally:
            self.shell.user_ns = save_user_ns
        return mod


class NotebookFinder(object):
    """Module finder that locates Jupyter Notebooks"""

    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname, path=None):
        nb_path = find_notebook(fullname, path)
        if not nb_path:
            return

        key = path
        if path:
            # lists aren't hashable
            key = os.path.sep.join(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]


class NotebookFileHandler(object):

    def __init__(self, fullname, path=None, extension="ipynb"):
        super().__init__()
        self.fullname = fullname
        self.path = settings.NOTEBOOKS_ROOT if path is None else path
        self.extension = extension
        self.nb = None

    @property
    def notebook_path(self):
        return '%s/%s.%s' % (self.path, self.fullname, self.extension)

    def __enter__(self):
        self.nb = self.read()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()

    @property
    def notebook(self) -> NotebookNode:
        return self.nb

    @notebook.setter
    def notebook(self, notebook: NotebookNode):
        self.nb = notebook

    def write(self):
        with open(self.notebook_path, 'wt') as f:
            nbformat.write(self.nb, f)

    def read(self) -> NotebookNode:
        print("reading Jupyter notebook from %s" % self.notebook_path)
        # load the notebook object
        with io.open(self.notebook_path, 'r', encoding='utf-8') as f:
            self.nb = read(f, 4)  # type: NotebookNode
        return self.nb


class NotebookExecutor(NotebookFileHandler):
    """Executor that execute notebooks"""

    def __init__(self, fullname, path=None, extension="ipynb", kernel_name='python3', timeout=600):
        super().__init__(fullname=fullname, path=path, extension=extension)
        self.kernel_name = kernel_name
        self.timeout = timeout

    def __call__(self, *args, **kwargs):
        ep = ExecutePreprocessor(timeout=self.timeout, kernel_name=self.kernel_name)
        ep.preprocess(self.nb, {'metadata': {'path': '%s/' % self.path}})


class NotebookBuilder():

    def __init__(self, notebook: NotebookNode = None, **kwargs):
        self.notebook_node = notebook  # type: NotebookNode
        self.cells = []
        self.kwargs = kwargs
        self.metadata = dict()

    def notebook(self, **kwargs):
        self.notebook_node = nbf.new_notebook(**kwargs)
        return self

    def markdown(self, *text):
        cell = nbf.new_markdown_cell('\n'.join(text))
        self.cells.append(cell)
        return self

    def code(self, *code):
        cell = nbf.new_code_cell('\n'.join(code))
        self.cells.append(cell)
        return self

    def meta_property(self, name, value):
        self.metadata[name] = value
        return self

    def build(self) -> NotebookNode:
        if self.notebook_node is None:
            self.notebook_node = self.notebook(**self.kwargs)
        self.notebook_node['metadata'] = self.metadata
        self.notebook_node['cells'] = self.cells
        return self.notebook_node


class NotebookFileManager():
    _instance = None

    @classmethod
    def create(cls, root=None):
        cls._instance = cls(settings.NOTEBOOKS_ROOT if root is None else root)
        return cls._instance

    @classmethod
    def instance(self):
        return self._instance

    def __init__(self, root) -> None:
        self.root = root

    @property
    def _files(self):
        return os.listdir(self.root)

    def all(self):
        notebooks = [NotebookFileModel(filename=file) for file in self._files]
        return notebooks

    def get(self, name) -> 'NotebookFileModel':
        if name is None:
            raise Exception('Notebook name is required.')
        try:
            matched = [f for f in self._files if f.startswith(name)]
            return NotebookFileModel(filename=matched[0])
        except BaseException as e:
            raise exceptions.NotebookNotFindException(name, e)

class NotebookFileModel:

    def __init__(self, filename=None, name=None, extension=None):
        self.name = os.path.splitext(filename)[0] if name is None else name
        self.extension = os.path.splitext(filename)[1] if extension is None else extension
        self._notebook = None
        self._script = None

    @property
    def filename(self):
        return "%s%s" % (self.name, self.extension)

    @property
    def notebook(self):
        if self._notebook is None:
            self.refresh_notebook()
        return self._notebook

    @property
    def script(self):
        if self._script is None:
            self.refresh_script()
        return self._script

    @property
    def abspath(self):
        return os.path.join(NotebookFileManager.instance().root, self.filename)

    def read(self):
        with io.open(self.abspath, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        return notebook

    def export(self, exporter=ScriptExporter()):
        (body, resources) = exporter.from_notebook_node(self.notebook)
        return dict(
            body=body,
            resources=resources
        )

    def refresh_notebook(self):
        self._notebook = self.read()

    def refresh_script(self):
        self._script = self.export()['body']
