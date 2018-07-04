# hydra-notebooks

Jupyter notebooks integration for Django. 
Features:
 - Expose and API to handle notebooks,
 - Import as modules
 - Execute by notebook
 - Embedd to Django-extensions shell plus

### Configuration

Jupyter configuration has to be add to the site directory, aside the ```settings.py```

### Usage

#### Importing and using notebooks

Assume, we have a notebook called ```my_notebook``` with the following cell:

```python
class SampleClass(object):
    
    def sample_method(self):
        print('execute sample_method')
        pass

    def sample_method_with_output(self):
        print('execute sample_method_with_output')
        return 'output'

    def sample_method_with_inoutput(self, param, *args, **kwargs):
        print('execute sample_method_with_inoutput(%s, %s, %s)' % (param, args, kwargs))
        return 'output'
    
    def __str__(self):
        return 'sample_class'
```

```python
# To use the module capabilities
import hydra_notebook

import notebooks.my_notebook as mynb

new_instance = mynb.SampleClass()

new_instance.sample_method_with_output()

``` 

As result:

```
execute sample_method_with_output
```

#### Executing notebooks

```python
import hydra_notebook
import os

with hydra_notebook.NotebookExecutor(path=os.path.join('.', 'notebooks'), fullname='demo_notebook') as e:
    e()
```

#### Displaying notebooks as HTML5 page

```/notebook/index```: List all notebooks

```/notebook/detail/<notebook_name>```: Show a notebook

#### Displaying notebooks as JSON

```/notebook/```: List all notebooks

```/notebook/<notebook_name>/```: Show a notebook

```/notebook/<notebook_name>/execute```: Execute a notebook
