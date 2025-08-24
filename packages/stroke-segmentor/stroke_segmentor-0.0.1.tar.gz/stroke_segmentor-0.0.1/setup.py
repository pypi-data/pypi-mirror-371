# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stroke_segmentor']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.7.3,<0.8.0',
 'monai>=1.5.0,<2.0.0',
 'nibabel>=5.3.2,<6.0.0',
 'requests>=2.32.5,<3.0.0',
 'rich>=13.9.4,<14.0.0',
 'simpleitk>=2.2.1']

setup_kwargs = {
    'name': 'stroke-segmentor',
    'version': '0.0.1',
    'description': '',
    'long_description': '# Stroke Segmentor\n\n[![Python Versions](https://img.shields.io/pypi/pyversions/stroke_segmentor)](https://pypi.org/project/stroke_segmentor/)\n[![Stable Version](https://img.shields.io/pypi/v/stroke_segmentor?label=stable)](https://pypi.python.org/pypi/stroke_segmentor/)\n[![Documentation Status](https://readthedocs.org/projects/stroke_segmentor/badge/?version=latest)](http://stroke_segmentor.readthedocs.io/?badge=latest)\n[![tests](https://github.com/BrainLesion/stroke_segmentor/actions/workflows/tests.yml/badge.svg)](https://github.com/BrainLesion/stroke_segmentor/actions/workflows/tests.yml)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n<!-- [![codecov](https://codecov.io/gh/BrainLesion/stroke_segmentor/graph/badge.svg?token=A7FWUKO9Y4)](https://codecov.io/gh/BrainLesion/stroke_segmentor) -->\n\nState-of-the-art ischemic stroke lesion segmentation in MRI\n\n\n## Installation\n\nWith a Python 3.8+ environment, you can install `stroke_segmentor` directly from [PyPI](https://pypi.org/project/stroke_segmentor/):\n\n```bash\npip install stroke_segmentor\n```\n\n\n## Use Cases and Tutorials\n\nA minimal example to create a segmentation could look like this:\n\n```python\nfrom stroke_segmentor.inferer import Inferer\n\ninferer = Inferer()\npred = inferer.infer(\n    dwi_path="path/to/dwi.nii.gz",\n    adc_path="path/to/adc.nii.gz",\n    segmentation_path="seg.nii.gz", # optional. the numpy array is always returned for direct usage\n)\n```\n\n## Citation\n\n> [!IMPORTANT]\n> `stroke_segmentor` is part of the [BrainLesion](https://github.com/BrainLesion) suite.  \n> Please cite it support the development!  \n> https://github.com/BrainLesion#-citing-brainlesion-suite\n\n This project is based on [DeepISLES](https://github.com/ezequieldlrosa/DeepIsles) and offers its NVAUTO algorithm.\n Please cite the [original manuscript](https://github.com/ezequieldlrosa/DeepIsles?tab=readme-ov-file#citations).\n\n## Contributing\n\nWe welcome all kinds of contributions from the community!\n\n### Reporting Bugs, Feature Requests and Questions\n\nPlease open a new issue [here](https://github.com/BrainLesion/stroke_segmentor/issues).\n\n### Code contributions\n\nNice to have you on board! Please have a look at our [CONTRIBUTING.md](CONTRIBUTING.md) file.\n',
    'author': 'Marcel Rosier',
    'author_email': 'marcel.rosier@tum.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BrainLesion/stroke_segmentor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
