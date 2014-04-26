from setuptools import setup, find_packages


f = open('README')
readme = f.read()
f.close()

setup(
    name='django-dag',
    version='0.1',
    description='django-dag is a reusable Django application for directed acyclic graphs.',
    long_description=readme,
    author='C',
    url='http://github.com/cazgp/django-dag/tree/master',
    packages=find_packages(exclude=('tests*',)),
    license='BSD',
    include_package_data=True,
    zip_safe=False,
)
