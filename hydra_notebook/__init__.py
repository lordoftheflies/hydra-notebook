import sys

from hydra_notebook.core import NotebookFinder
from hydra_notebook.core import NotebookExecutor

sys.meta_path.append(NotebookFinder())

default_app_config = 'hydra_notebook.apps.HydraNotebookConfig'
