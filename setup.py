from setuptools import setup

setup(
    name='ogn-alert',
    version='0.1',
    description='Alerts based on OGN data',
    author='Florian Sammüller',
    author_email='info@aufwin.de',
    license='MIT',
    packages=['ogn_alert'],
    install_requires=['ogn-client', 'shapely', 'RPi.GPIO'],
    zip_safe=False,
)
