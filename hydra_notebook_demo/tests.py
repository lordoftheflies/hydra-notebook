import os
from django.test import TestCase

# Create your tests here.
# import hydra_notebook
import hydra_notebook


class TestHook(TestCase):

    def setUp(self):
        pass

    def test_module_methods_and_functions(self):
        import notebooks.demo_notebook as given_module
        self.assertListEqual(dir(given_module), [
            'SampleClass',
            '__builtins__',
            '__doc__',
            '__file__',
            '__loader__',
            '__name__',
            '__package__',
            '__spec__',
            'get_ipython',
            'sample_dictionary',
            'sample_float',
            'sample_instance',
            'sample_integer',
            'sample_list',
            'sample_object',
            'sample_strng',
            'sample_tuple',
        ])

        given_module.sample_instance.sample_method()
        given_module.sample_instance.sample_method_with_inoutput(param='omega', param_a='alfa', param_b='beta')
        # pass

    def test_execute(self):
        print(os.path.abspath(os.path.curdir))
        with hydra_notebook.NotebookExecutor(
                path=os.path.join('.', 'notebooks'),
                fullname='demo_notebook'
        ) as e:
            e()
        # pass
