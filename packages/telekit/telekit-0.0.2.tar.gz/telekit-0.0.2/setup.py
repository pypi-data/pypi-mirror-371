from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
    name='telekit',
    version='0.0.2',
    author='romashka',
    author_email='comfy6011@gmail.com',
    description='This is the simplest module for making Telegram Bots.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://t.me/TeleKitLib',
    packages=find_packages(),
    install_requires=['pyTelegramBotAPI>=4.27.0'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='files speedfiles ',
    project_urls={
        "Telegram": "https://t.me/TeleKitLib"
    },
    python_requires='>=3.12'
)