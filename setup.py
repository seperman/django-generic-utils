from setuptools import setup #, find_packages

try:
    with open('README.md') as file:
        long_description = file.read()
except:
    long_description = "Generic Useful Django Classes/Functions"

setup(name='django-generics',
      version='0.1.7',
      description='Generic Useful Django Classes/Functions',
      url='https://github.com/erasmose/django-generics',
      download_url='https://github.com/erasmose/django-generics/tarball/master',
      author='Erasmose',
      author_email='xpower3d@yahoo.com',
      license='MIT',
      packages=['django-generics'],
      zip_safe=False,
      install_requires=[
        "django",
        "South",
        "beautifulsoup4",
      ],
      long_description=long_description,
      classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
        ],
      )