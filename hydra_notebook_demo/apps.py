import logging

from django.apps import AppConfig

# Get an instance of a logger
logger = logging.getLogger(__name__)


class HydraNotebookDemoConfig(AppConfig):
    name = 'hydra_notebook_demo'

    def ready(self):
        logger.info('Initialize module with notebooks ...')
