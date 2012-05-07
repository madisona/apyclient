
import os

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme, 'r').read()

params = dict(
    name='apyclient',
    version='0.0.2',
    url='https://github.com/madisona/apyclient',
    license='BSD',
    author='Aaron Madison',
    author_email='aaron.l.madison@gmail.com',
    description='A Python Api Client',
    long_description=LONG_DESCRIPTION,
    py_modules=['apyclient'],
    install_requires=['apysigner'],

    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    params['tests_require'] = ['unittest2', 'mock']
    params['test_suite'] = 'unittest2.collector'

setup(**params)
