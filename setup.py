import os
from setuptools import setup #, find_packages

try:
    with open('README.md') as file:
        long_description = file.read()
except:
    long_description = "Generic Useful Django Classes/Functions"


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(name='django-generic-utils',
      version='0.3.2',
      description='Generic Useful Django Classes/Functions',
      url='https://github.com/seperman/django-generic-utils',
      download_url='https://github.com/seperman/django-generic-utils/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['generics'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "django",
        "South",
        "beautifulsoup4",
      ],
      long_description=long_description,
      classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: MIT License',
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',        
        ],
      )