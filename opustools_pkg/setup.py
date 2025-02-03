import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ['ruamel.yaml']

langid_require = ['pycld2', 'langid']

all_require = langid_require

setuptools.setup(
    name="opustools",
    version="1.7.1",
    author="Mikko Aulamo",
    author_email="mikko.aulamo@helsinki.fi",
    description="Tools to read OPUS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Helsinki-NLP/OpusTools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    scripts=["bin/opus_read", "bin/opus_cat", "bin/opus_get",
        "bin/opus_langid", "bin/opus_express"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=install_requires,
    extras_require={'langid': langid_require, 'all': all_require}
)
