from setuptools import setup,find_packages

setup(
    name='subhan-stt',
    version='0.1',
    author='Subhan Saeed',
    author_email='subhanmian@950.com',
    description='this speech to text package created by Subhan Saeed'
)
    
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
