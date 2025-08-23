# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name="tomca",  # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/guides/single-sourcing-package-version/
    version="0.0.0dev1",  # Required
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description="TOMCA (Tissue Optics Monte Carlo Analysis) is a TNO package written for Monte Carlo analysis of light through tissues and scattering media based on the MCX package.  TOMCA helps organize shared functions between projects and aims to make research, simulation, and analysis easier.",  # Optional
    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description=long_description,  # Optional
    # Denotes that our long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    #
    # Optional if long_description is written in reStructuredText (rst) but
    # required for plain-text or Markdown; if unspecified, "applications should
    # attempt to render [the long_description] as text/x-rst; charset=UTF-8 and
    # fall back to text/plain if it is not valid rst" (see link below)
    #
    # This field corresponds to the "Description-Content-Type" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url="https://ci.tno.nl/gitlab/tissue-optics/mcx",  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author="Sadok Jbenyeni",  # Optional
    # This should be a valid email address corresponding to the author listed
    # above.
    author_email="sadok.jbenyeni@tno.nl",  # Optional
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a list of additional keywords, separated
    # by commas, to be used to assist searching for the distribution in a
    # larger catalog.
    keywords="Development",  # Optional
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={"": "Software/src"},  # Optional
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(where="src"),  # Required
    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. See
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    # python_requires=">=3.7, <4",
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
        "asttokens==2.2.1",
        "autopep8==2.0.1",
        "backcall==0.2.0",
        "botorch==0.10.0",
        "colorama==0.4.6",
        "comm==0.1.2",
        "contourpy==1.0.7",
        "cycler==0.11.0",
        "dataclasses-json==0.5.7",
        "debugpy==1.6.6",
        "decorator==5.1.1",
        "entrypoints==0.4",
        "executing==1.2.0",
        "fonttools==4.38.0",
        "ipykernel==6.20.2",
        "ipython==8.8.0",
        "jdata==0.5.2",
        "jedi==0.18.2",
        "jupyterlab==4.1.2",
        "kiwisolver==1.4.4",
        "lightgbm==4.3.0",
        "marshmallow==3.19.0",
        "marshmallow-enum==1.5.1",
        "matplotlib==3.6.3",
        "matplotlib-inline==0.1.6",
        "mypy-extensions==1.0.0",
        "nest-asyncio==1.5.6",
        "numpy==1.24.1",
        "setuptools",
        "packaging==23.0",
        "pandas==1.5.3",
        "parso==0.8.3",
        "path",
        "pathlib==1.0.1",
        "pickleshare==0.7.5",
        "Pillow==9.4.0",
        "platformdirs==2.6.2",
        "pmcx",
        "prompt-toolkit==3.0.36",
        "psutil==5.9.4",
        "pure-eval==0.2.2",
        "pycodestyle==2.10.0",
        "pydantic==2.6",
        "Pygments==2.14.0",
        "pyparsing==3.0.9",
        "python-dateutil==2.8.2",
        "pytz==2022.7.1",
        "pyzmq",
        "scipy",
        "six==1.16.0",
        "stack-data==0.6.2",
        "tomli==2.0.1",
        "tornado==6.2",
        "traitlets==5.8.1",
        "typing-inspect==0.8.0",
        "typing_extensions>=4.4.0",
        "wcwidth==0.2.6",
        "tqdm",
        "tabulate",
        "oct2py",
        "offloader == 6.0.0",],  # Optional
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        # "dev": ["check-manifest"],
        # "test": ["coverage"],
    },
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={  # Optional
        # "sample": ["package_data.dat"],
    },
    # Entry points. The following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        # "console_scripts": [
        #     "sample=sample:main",
        # ],
    },
    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        "Documentation": "https://tissue-optics.ci.tno.nl/mcx/",
        "Repository": "https://ci.tno.nl/gitlab/tissue-optics/mcx",
        "Issues": "https://ci.tno.nl/gitlab/tissue-optics/mcx/-/issues"
    },
)
