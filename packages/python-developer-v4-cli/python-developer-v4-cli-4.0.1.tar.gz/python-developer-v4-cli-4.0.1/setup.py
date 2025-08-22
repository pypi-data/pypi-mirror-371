from setuptools import setup, find_packages
import os

setup(
    name="python-developer-v4-cli",
    version="4.0.1",
    author="Dev Ops Axum PP-2025",
    author_email="francoenzopecora@gmail.com",
    description="Herramienta de deployment automatizado para proyectos .NET",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pyramid-debugtoolbar==4.9",
        "colorama==0.4.6",
        "bcrypt==4.3.0",
        "certifi==2025.8.3",
        "cffi==1.17.1",
        "Chameleon==4.6.0",
        "charset-normalizer==3.4.3",
        "cryptography==45.0.6",
        "hupper==1.12.1",
        "idna==3.10",
        "invoke==2.2.0",
        "paramiko==4.0.0",
        "PasteDeploy==3.1.0",
        "pip==24.0",
        "plaster==1.1.2",
        "plaster-pastedeploy==1.0.1",
        "pycparser==2.22",
        "PyNaCl==1.5.0",
        "pyramid==2.0.2",
        "pyramid_chameleon==0.3",
        "requests==2.32.4",
        "setuptools==65.5.0",
        "translationstring==1.4",
        "urllib3==2.5.0",
        "venusian==3.1.1",
        "waitress==3.0.2",
        "WebOb==1.8.9",
        "zope.deprecation==5.1",
        "zope.interface==7.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
    "console_scripts": [
        "python-deployer = python_developer_v4_cli.Python_Deployer_V4:main",
    ]
},
)