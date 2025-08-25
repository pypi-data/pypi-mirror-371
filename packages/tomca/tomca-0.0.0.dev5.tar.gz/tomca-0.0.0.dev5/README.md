<!--- 
\mainpage TOMCA test
-->

# TOMCA Brain

Tissue Optics Monte Carlo Analysis, TNO's custom MCX package


## Useful Links
-   [🌐 TOMCA GitLab Website](https://ci.tno.nl/gitlab/tissue-optics/mcx)
-   [🔆 TOMCA Package Documentation](https://tissue-optics.ci.tno.nl/mcx)
-   [🏛 TOMCA Literature Resources](https://tissue-optics.ci.tno.nl/mcx/TOMCAReferenceandResourceManagement.html)
-   [👩‍💻 TOMCA tmcx Package Documentation](https://tissue-optics.ci.tno.nl/mcx/namespacetmcx.html)

## Table of Contents

  * [Introduction](#introduction)
  * [Requirements and Installation](#requirements-and-installation)
  * [Running Simulations](#running-simulations)
  * [Using JSON-formatted input files](#using-json-formatted-input-files)
  * [User list](#user-list)

<a name="introduction"></a>
## Introduction

\b TOMCA (Tissue Optics Monte Carlo Analysis) is a TNO package written for Monte Carlo analysis of light through tissues and scattering media based on the MCX package.  TOMCA helps organize shared functions between projects and aims to make research, simulation, and analysis easier.

Monte Carlo eXtreme (MCX) is a fast physically-accurate photon simulation software for 3D heterogeneous complex media. By taking advantage of the massively parallel threads and extremely low memory latency in a modern graphics processing unit (GPU), this program is able to perform Monte Carlo (MC) simulations at a blazing speed, typically hundreds to a thousand times faster than a single-threaded CPU-based MC implementation.

See the full readme for mcx at: 

- [MCX.space](https://mcx.space)
  - [MCX parameters list](https://mcx.space/wiki/index.cgi?Options)

The algorithm of this software is detailed in the References \cite Yan2020 , \cite Fang_2009 , \cite Yu2018.

<a name="requirements-and-installation"></a>
## Requirements and Installation
- [Software setup](https://tissue-optics.ci.tno.nl/mcx/softwareSetup.html)
- [Git Repo login](https://tissue-optics.ci.tno.nl/mcx/gitRepoUsage.html)
- [Installing Doxygen and TeX, compiling documentation](https://tissue-optics.ci.tno.nl/mcx/compilingDoxygen.html)

<a name="running-simulations"></a>
## Running Simulations

(To be added)

<a name="using-json-formatted-input-files"></a>
## Using JSON-formatted input files

Our model files and jcfg dict in code are based on the mcx JSON structure used in the .exe version of the scripts.  This was chosen so that our code is always backwards compatible with the NEU group.  See their documentation for the exact specifications on inputs (link)

Please also browse this interactive [Jupyter Notebook based MCXLAB tutorial](https://colab.research.google.com/github/fangq/mcx/blob/master/mcxlab/tutorials/mcxlab_getting_started.ipynb)
to see a suite of examples showing the key functionalities of MCXLAB (using GNU Octave).


## Using PMCX in Python

We have based our code on the python binding of MCX called PMCX. 

Please read the `pmcx/README.txt` file for more details on how to install and 
use PMCX.

Please also browse this interactive [Jupyter Notebook based PMCX tutorial](https://colab.research.google.com/github/fangq/mcx/blob/master/pmcx/tutorials/pmcx_getting_started.ipynb)
to see a suite of examples showing the key functionalities of PMCX.

<a name="user-list"></a>
## User list
**TOMCA users**
* Vincent Zoutenbier* (2022 - Present) 
      - Lead developer of TMCX package, contact with questions
* Sadok Jbenyeni (2025 - Present)
* Amerens Bekkers (2024 - Present)
* Margherita Vaselli (2024 - Present)
* Tijmen van Ree (2024 - Present)
* Arjen Amelink ( - )
* Bastiaan Florijn ( - 2022)
* Man Xu ( - X)

**Auxillary work by:**
* Thijs van der Knaap, TNO ACE
      - Integration of TNO's [Offloader](https://codingguild.tno.nl/coding-at-tno/tno-offloader/?h=offloader) (2024)
* Frank Wessels, Sioux 
      - Framework for ML (2024)
* Panagiotis Meletis, Sioux 
    - AI algorithms for determination of biomarker sensitivity in:
      - Bilihome: Extracting bilirubine concentration from infant skin model (2023)
      - ERP Determine: Extracting blood O2 saturation from skin model (2023)

**Other known MCX users:**
* Gijs Buist (Vrije U., Amsterdam 2021 - Present)

*Note: This page should use markdown syntax to parse properly on the GitLab main page.*