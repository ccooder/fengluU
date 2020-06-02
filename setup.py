import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fengluB",
    version="0.0.02_alpha1",
    # version="0.0.02_alpha2",
    author="Fenglu Niu",
    author_email="niufenglu@gmail.com",
    description="牛逢路的开发工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccooder/fengluU",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    python_requires='>=3.6',
    install_requires=[
        "mysql-connector-python==8.0.11",
    ],
)
# 1. python setup.py sdist bdist_wheel
# python setup.py install bdist_wheel
# 2. twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# 2. twine upload dist/*
# 3. sudo pip install --index-url https://test.pypi.org/project/fengluA projectname
