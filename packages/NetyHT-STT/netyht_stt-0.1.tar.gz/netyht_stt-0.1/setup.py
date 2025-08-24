#pip install setuptools
#pip install twine

from setuptools import setup, find_packages                             #Make own package

setup(
    name = 'NetyHT-STT',
    version = '0.1',
    author = 'CallMeDenz',
    author_email= 'randomplacesxo@gmail.com',
    description= 'This is speech-to-text package created by CallMeDenz',
    packages = find_packages(),
install_requirements = [
    "selenium",
    "webdriver_manager",
    "SpeechRecognition",
    "pyaudio",
    "colorama"
    ],
)