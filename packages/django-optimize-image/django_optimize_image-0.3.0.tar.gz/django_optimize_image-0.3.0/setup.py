from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="django-optimize-image",
    version="0.3.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Pillow", "Django"],
    description="A Django middleware to optimize image uploads by converting them to WebP.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nahom D",
    author_email="nahom@nahom.eu.org",
    url="https://github.com/nahom-d54/django-optimize-image",
)
