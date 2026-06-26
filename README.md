<div align="center">
	<img alt="GentestsAILib logo" src="https://raw.githubusercontent.com/codesavant23/gentestsai-lib/main/assets/logo/gtsailib_github_socialcard.png" width="650"/>
    <p style="position: relative; bottom: 70px; font-style: italic;">
        A SOLID Python library to build automatic tests generation frameworks/pipelines
    </p>
</div>

[![Paper Backed](https://img.shields.io/badge/paper--backed-8A2BE2)](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/thesis_ita.pdf)
[![License](https://img.shields.io/badge/license-Custom--SA-%231b25e5)](https://raw.githubusercontent.com/codesavant23/gentestsai-lib/refs/heads/main/LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-35b2e3)
[![Docs](https://img.shields.io/badge/docs-WIP-d37207)](https://codesavant23.github.io/gentestsai)

# What is GenTestsAILib?

**GenTestsAILib** is a sophisticated Python library that provides autonomous components, and services, to build automatic unit-tests generation frameworks, or pipelines, that leverage LLMs

## Software artifact Key Features

*   **LLM-Powered Test Generation and Correction**: Provides services for the creation, and correction, of Python unit tests for [autonomous entities](#framework-specific-terminology), by leveraging the power of LLMs.
*   **Focal Environments technology**: Provides sandbox environments called [focal environments](#general) that permits to execute syntactic and linting correctness check.
*   **Code Metrics calculation**: Implements services that computes specific metrics, such as Entity-by-Entity Code Coverage.
*   **Intelligent Caching**: Exposes services to access [partial test suite](#general) caching systems used to store results of generation and correction attempts avoiding redundant API calls and speeding up frameworks/pipelines built with GenTestsAILib.
*   **Failures recording**: Implements services to access local files indicating registration
*   **Prompt building**: Provides a tool to build full prompts from user's own prompt templates to guide the LLM's test generation and correction behavior.
*   **Extreme Modularity & Extensibility**: Built with a SOLID-driven architecture, the library enables highly composable and interchangeable logical units across the entire GenTestsAI framework. Every layer — from inference platform backends and LLM specific implementations to configuration schemas, hyperparameters, and software groups installed in focal environments — is designed to be almost independently extendable, easily replaceable, and consistently maintainable, allowing seamless customization and evolution without heavily impacting existing components.

# Library Structure

The library source code is organized into separate sub-components:

| Sub-component             | Description                                                                                                                                                  |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ptsuite_generation`      | Main sub-component that provides all services relating to [partial test suite](#general) production process (such as Entity-by-Entity Generation/Correction) |
| `focalproj_configuration` | Sub-component that provides services relating to the configuration of [focal projects](#general)                                                             |
| `calc_coverage`           | Sub-component that encapsulates services to compute code metrics                                                                                             |
| `prompt_builder`          | Sub-component that provides a service for building full prompts (starting from custom templates)                                                             |

# How to get this library

## Latest stable release

You can find the binaries of the component in the [release](https://github.com/codesavant23/gentestsai-lib/releases) section of this repository

## Latest build

### Installation

```python
pip install git+https://github.com/codesavant23/gentestsai-lib
```

### Update

```python
pip install git+https://github.com/codesavant23/gentestsai-lib
```

# Appendix
## Associated Paper
Here you can find the [Bachelor's Thesis](https://raw.githubusercontent.com/codesavant23/gentestsai/main/assets/thesis_ita.pdf) where most of GenTestsAILib (in his alpha version) is formally presented.

## (Custom) Python Terminology
- **<u>Module-file</u>**: A Python module consisting of only a single file, with the extension `.py`, different from an `__init__.py` file.

- **<u>Code Package (or Module-package)</u>**: A Python module consisting of multiple files with the .py extension, generally identified by the name of the folder containing them, which must contain an `__init__.py` file that specifies the visibility of elements in the various "submodules" that comprise it (be they module-files or other module-packages).

- **<u>Python Module</u>**: A module-file or a module-package of Python code

## Library specific Terminology

### General

- **<u>Focal Project/Method/Function/Anything</u>**:<br/> Something object of testing processes (e.g. Focal Project = [SUT](https://en.wikipedia.org/wiki/System_under_test))

- **<u>Focal Environment (of a focal project $X$):</u>**<br/> An isolated and pre-configured software environment aimed at hosting the focal project $X$, including the set of dependencies necessary for the execution, verification (static analysis/linting) and calculation of quality metrics of its source code, built according to one or more use cases among those listed.
<br/>

- **<u>Autonomous (Code) Entity:</u>**<br/> The smallest algorithmic unit of code whose semantics can be formalized in a contract (a function, or a class method).
<br/>

- **<u>Partial Test Suite of a Python module</u>**<br/> An organized and structured set of multiple test cases designed to verify the functionality, correctness, and reliability of a single autonomous code entity, of the focal Python module-file it concerns.
<br/>

- **<u>(Whole) Test Suite of a Python module</u>**<br/> An organized and structured set of multiple test cases, or partial test suites, designed to verify the functioning, correctness, and reliability of **each** autonomous code entity of the focal Python module it concerns.

### Paths and Directories
- **<u>Directory:</u>**  A folder in the o.s. file system.
- **<u>Path (of a directory $D$):</u>** An ordered sequence of directories that identifies the location of directory $D$ within the file system tree. A path can be expressed in absolute form (making the identification unique) or relative.
- **<u>Root Path (of an element $P$):</u>** A path identifying a directory $R$, where $R$ represents the root directory containing all directories and files associated with element $P$.
<br/><br/>

- **<u>Focal Project Root Path (also referred to as "Focal Root"):</u>** Root path of a focal project containing the source code (focal code) for which tests will be automatically generated. This directory may also include files or subdirectories not strictly related to the focal code.
- **<u>Tests Project Root Path (also referred to as "Tests Root"):</u>** Root path of a focal project containing test cases manually developed by human programmers.
- **<u>Gen-tests Project Root Path (also referred to as "Gen-tests Root"):</u>** Root path of a focal project intended to contain exclusively test cases automatically generated via Large Language Models.
- **<u>Env-config Project Root Path (also referred to as "Env-config Root"):</u>** Root path of a focal project containing the files required to configure its specific focal environment.
- **<u>Cov-config Project Root Path (also referred to as "Cov-config Root"):</u>** Root path of a focal project containing the files required to configure the tools for calculating coverage and other focal code quality metrics.
- **<u>Full Project Root Path (also referred to as "Full Root"):</u>** Root path of a focal project that includes the entire contents of the project involved in an automatic test case generation process and a test evaluation process. Specifically, it contains:
	- as subdirectories at the **first level**:
		- the Gen-tests Project Root Path
		- the Env-config Project Root Path 
		- the Cov-config Project Root Path 
	- as subdirectories at **arbitrary nesting** levels:
		- the Focal Project Root Path
		- the Tests Project Root Path
