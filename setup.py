import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fengluA",
    version="0.0.02_alpha",
    author="Fenglu Niu",
    author_email="niufenglu@gmail.com",
    description="牛逢路的开发工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://zyx00.xyz",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
# 1. python setup.py sdist bdist_wheel
# 2. twine upload dist/*
