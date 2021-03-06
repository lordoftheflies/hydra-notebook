from django.test import TestCase

# Create your tests here.
from .core import NotebookBuilder, NotebookFileHandler, NotebookFileModel, NotebookFileManager
from . import exceptions


class NotebookBuilderTestCase(TestCase):

    def test_build(self):
        nb = NotebookBuilder().notebook().markdown(
            "# Heading 1",
            "## Heading 2",
            "### Heading 3",
            "#### Heading 4",
            "Normal text"
        ).code(
            "a = 'kacsa %s %s' % (111, 222)",
            "print(a)"
        ).build()

    def test_build_with_persistence(self):
        b = NotebookBuilder()
        nb = b.notebook().markdown(
            "# Heading 1",
            "## Heading 2",
            "### Heading 3",
            "#### Heading 4",
            "Normal text"
        ).code(
            "a = 'kacsa %s %s' % (111, 222)",
            "print(a)"
        ).build()

        fh = NotebookFileHandler(fullname='test_build_with_persistence')

        fh.notebook = nb

        fh.write()


class NotebookFileManagerTestCase(TestCase):

    def setUp(self):
        self.manager = NotebookFileManager.create()

    def test_all(self):
        notebooks = self.manager.all()
        self.assertEqual(len(notebooks), 3)

    def test_get(self):
        notebook = self.manager.get('test_notebook')
        self.assertEqual(notebook.filename, 'test_notebook.ipynb')

        with self.assertRaises(Exception):
            self.manager.get(None)
        with self.assertRaises(exceptions.NotebookNotFindException):
            self.manager.get('none')


class NotebookFileModelTestCase(TestCase):

    def setUp(self):
        manager = NotebookFileManager.create()
        self.notebook = manager.get('test_notebook')

    def test_scriptt(self):
        self.assertGreater(len(self.notebook.script), 0)
