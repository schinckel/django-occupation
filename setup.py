from setuptools import find_packages, setup

setup(
    name="django-occupation",
    version='0.0.1',
    description="Multitenancy support in django, via Row Level Security.",
    url="https://bitbucket.org/schinckel/django-occupation",
    author="Matthew Schinckel",
    author_email="matt@schinckel.net",
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'occupation': ['templates/**.html']},
    exclude_package_data={
        '': ['test*.py', 'tests/*.env', '**/tests.py'],
    },
    python_requires='>=3.6',
    install_requires=[
        'django',
        'psycopg2-binary',  # or psycopg2cffi under pypy
    ],
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='runtests.runtests',
)
