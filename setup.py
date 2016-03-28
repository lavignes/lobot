from setuptools import setup
import lobot


setup(name='lobot',
      version=lobot.__version__,
      author='Scott LaVigne',
      author_email='pyrated@gmail.com',
      url='https://github.com/pyrated/lobot',
      description='An extensible IRC bot',
      download_url='https://github.com/pyrated/lobot.git',
      packages=['lobot'],
      scripts=['bin/lobot'],
      requires=['aiohttp']
      )
