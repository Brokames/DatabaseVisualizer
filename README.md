# Python Discord Code Jam Repository Template

## A Primer
Hello code jam participants! We've put together this repository template for you to use in [our code jams](https://pythondiscord.com/events/) or even other Python events!

This document will contain the following information:
1. [What does this template contain?](#what-does-this-template-contain)
2. [How do I use it?](#how-do-i-use-it)
3. [How do I adapt it to my project?](#how-do-i-adapt-it-to-my-project)

You can also look at [our style guide](https://pythondiscord.com/events/code-jams/code-style-guide/) to get more information about what we consider a maintainable code style.

## What does this template contain?

Here is a quick rundown of what each file in this repository contains:
- `LICENSE`: [The MIT License](https://opensource.org/licenses/MIT), an OSS approved license which grants rights to everyone to use and modify your projects and limits your liability. We highly recommend you to read the license.
- `.gitignore`: A list of files that will be ignored by Git. Most of them are auto-generated or contain data that you wouldn't want to share publicly.
- `dev-requirements.txt`: Every PyPI packages used for the project's development, to ensure a common and maintainable code style. [More on that below](#using-the-default-pip-setup).
- `tox.ini`: The configurations of two of our style tools: [`flake8`](https://pypi.org/project/flake8/) and [`isort`](https://pypi.org/project/isort/).
- `.pre-commit-config.yaml`: The configuration of the [`pre-commit`](https://pypi.org/project/pre-commit/) tool.
- `.github/workflows/lint.yaml`: A [GitHub Actions](https://github.com/features/actions) workflow, a set of actions run by GitHub on their server after each push, to ensure the style requirements are met.

Each of these files have comments for you to understand easily, and modify to fit your needs.

### flake8: general style rules

Our first and probably most important tool is flake8. It will run a set of plugins on your codebase and warn you about any non-conforming lines.
Here is a sample output:
```
~> flake8
./app.py:1:1: D100 Missing docstring in public module
./app.py:1:6: N802 function name 'helloWorld' should be lowercase
./app.py:1:16: E201 whitespace after '('
./app.py:1:17: ANN001 Missing type annotation for function argument 'name'
./app.py:1:23: ANN201 Missing return type annotation for public function
./app.py:2:1: D400 First line should end with a period
./app.py:2:1: D403 First word of the first line should be properly capitalized
./app.py:3:19: E225 missing whitespace around operator
```

Each line corresponds to an error. The first part is the file path, then the line number, and the column index.
Then comes the error code, a unique identifier of the error, and then a human-readable message.

If, for any reason, you do not wish to comply with this specific error on a specific line, you can add `# noqa: CODE` at the end of the line.
For example:
```python
def helloWorld():  # noqa: N802
    ...
```
will pass linting. Although we do not recommend ignoring errors unless you have a good reason to do so.

It is run by calling `flake8` in the project root.

#### Plugin List:

- `flake8-annotations`: Checks your code for the presence of [type-hints](https://docs.python.org/3/library/typing.html).
- `flake8-bandit`: Checks for common security breaches.
- `flake8-docstring`: Checks that you properly documented your code.
- `flake8-isort`: Makes sure you ran ISort on the project.

### ISort: automatic import sorting

This second tool will sort your imports according to the [PEP8](https://www.python.org/dev/peps/pep-0008/#imports). That's it! One less thing for you to do!

It is run by calling `isort .` in the project root. Notice the dot at the end, it tells ISort to use the current directory.

### Pre-commit: run linting before committing

This third tool doesn't check your code, but rather makes sure that you actually *do* check it.

It makes use of a feature called [Git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) which allow you to run a piece of code before running `git commit`.
The good thing about it is that it will cancel your commit if the lint doesn't pass. You won't have to wait for Github Actions to report and have a second fix commit.

It is *installed* by running `pre-commit install` and can be run manually by calling only `pre-commit`.

[Lint before you push!](https://soundcloud.com/lemonsaurusrex/lint-before-you-push)

#### Hooks List:

- `check-toml`: Lints and corrects your TOML files.
- `check-yaml`: Lints and corrects your YAML files.
- `end-of-file-fixer`: Makes sure you always have an empty line at the end of your file.
- `trailing-whitespaces`: Removes whitespaces at the end of each line.
- `python-check-blanket-noqa`: Forbids you from using noqas on large pieces of code.
- `isort`: Runs ISort.
- `flake8`: Runs flake8.

## Contributing

### Getting started

This project uses [Pipenv](https://pipenv.pypa.io/en/latest/) for package
management and [pre-commit](https://pre-commit.com) to enforce linting
requirements. Follow the steps below to get setup using both tools.

```shell
# Create virtual environment and install dependencies
$ pipenv install --dev

# Initialize git hooks
$ pre-commit install

# Activate the virtual environment
$ pipenv shell
```

With the environment activated you can start coding! When you are done you can
deactivate the environment by simply running `exit`.
