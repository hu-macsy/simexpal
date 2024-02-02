import os, sys
sys.path.insert(0, os.path.abspath('../simexpal'))

project = 'simexpal'
copyright = 'Humboldt-Universität zu Berlin, 2024'
author = 'Florian Willich, Eugenio Angriman, Alexander van der Grinten'

version = ''
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = None
html_theme = 'sphinx_rtd_theme'
htmlhelp_basename = 'simexpaldoc'
