from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="django-log-hub",
    version="1.0.6",
    author="Enes HAZIR",
    description="Advanced logging and monitoring module for Django projects with centralized logging system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eneshazr/django-log-hub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "log_hub": [
            "templates/log_hub/*.html",
            "static/log_hub/*",
            "locale/tr/LC_MESSAGES/*",
            "locale/en/LC_MESSAGES/*",
        ],
    },
    keywords="django, logging, admin, logs, monitoring, debug, centralized logging, context manager, decorator",
    project_urls={
        "Bug Reports": "https://github.com/eneshazr/django-log-hub/issues",
        "Source": "https://github.com/eneshazr/django-log-hub",
        "Documentation": "https://github.com/eneshazr/django-log-hub#readme",
    },
    zip_safe=False,
)
