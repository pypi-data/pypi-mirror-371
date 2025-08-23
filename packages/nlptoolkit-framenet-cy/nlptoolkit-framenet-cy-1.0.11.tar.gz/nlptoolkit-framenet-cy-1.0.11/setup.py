from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["FrameNet/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='nlptoolkit-framenet-cy',
    version='1.0.11',
    packages=['FrameNet', 'FrameNet.data'],
    package_data={'FrameNet': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'FrameNet.data': ['*.xml']},
    url='https://github.com/StarlangSoftware/TurkishFrameNet-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='FrameNet library',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
