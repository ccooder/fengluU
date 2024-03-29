import setuptools

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="fengluB",
    version="0.0.03_alpha7",
    # version="0.0.03_alpha8",
    author="Fenglu Niu",
    author_email="niufenglu@gmail.com",
    description="牛逢路的开发工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccooder/fengluU",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "mysql-connector-python==8.0.14",
        "regex",
    ],
)
# 1. python setup.py sdist bdist_wheel
# python setup.py install bdist_wheetl
# 2. twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# 2. twine upload dist/*
# 3. sudo pip install --index-url https://test.pypi.org/project/fengluA projectname
