import os, sys
sys.path.insert(0, os.path.abspath('../simexpal'))

project = 'simexpal'
copyright = '2019, Eugenio Angriman, Alexander van der Grinten'
author = 'Eugenio Angriman, Alexander van der Grinten'

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
html_static_path = ['_static']
htmlhelp_basename = 'simexpaldoc'
