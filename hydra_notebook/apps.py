import logging

from django.apps import AppConfig

# Get an instance of a logger
logger = logging.getLogger(__name__)

class HydraNotebookConfig(AppConfig):
    name = 'hydra_notebook'

    def ready(self):
        logger.info('Initialize notebooks ...')

