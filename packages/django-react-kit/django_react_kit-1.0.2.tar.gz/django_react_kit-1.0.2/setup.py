from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def get_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="django-react-kit",
    version="1.0.2",
    author="Django React Kit Team",
    author_email="hello@djangoreactkit.com",
    description="Server-Side Rendering for React components in Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/django-react-kit/django-react-kit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django",
    ],
    include_package_data=True,
    package_data={
        "django_react_kit": [
            "templates/django_react_kit/*.html",
            "frontend/*.js",
            "frontend/*.json",
            "frontend/app/*.tsx",
            "frontend/app/*/*.tsx",
            "management/commands/*.py",
        ],
    },
    entry_points={
        "console_scripts": [
            "django-react-kit=django_react_kit.cli:main",
        ],
    },
    keywords="django react ssr server-side-rendering frontend",
    project_urls={
        "Bug Reports": "https://github.com/cyberwizdev/cyberwizdev/issues",
        "Source": "https://github.com/cyberwizdev/django-react-kit",
        "Documentation": "https://django-react-kit.readthedocs.io/",
    },
)