import re
from setuptools import setup


with open('expr/__init__.py') as f:
    try:
        version = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.M
        ).group(1)
    except AttributeError:
        raise RuntimeError('Could not identify version') from None

    # look at this boilerplate code
    try:
        author = re.search(
            r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.M
        ).group(1)
    except AttributeError:
        author = 'jay3332'


with open('README.md', encoding='utf-8') as f:
    readme = f.read()


setup(
    name='expr.py',
    author=author,
    url='https://github.com/jay3332/expr.py',
    project_urls={
        "Issue tracker": "https://github.com/jay3332/expr.py/issues",
    },
    version=version,
    packages=[
        'expr'
    ],
    license='MIT',
    description='A safe and simple math expression evaluator for Python.',
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'rply>=0.7.8'
    ],
    python_requires='>=3.7.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
