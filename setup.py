
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme, 'r').read()

setup(
    name='apyclient',
    version='0.3.1',
    url='https://github.com/madisona/apyclient',
    license='BSD',
    author='Aaron Madison',
    author_email='aaron.l.madison@gmail.com',
    description='A Python Api Client',
    long_description=LONG_DESCRIPTION,
    py_modules=['apyclient'],
    install_requires=['apysigner>=3.0.1'],

    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
