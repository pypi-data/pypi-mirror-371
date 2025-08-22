
# ruffit

A modern Python CLI tool to monitor `.py` files and automatically run code quality checks and formatting on change.

## Features

- **Watches** for changes to Python files in any folder you specify
- **Debounces** rapid file events to avoid duplicate triggers
- On modification, automatically runs:
  - `ruff format` to auto-format code
  - `ruff check` to lint and check for code issues (with optional autofix)
  - `ty check` to check type annotations
- **Rich terminal output** for clear, colorful feedback
- **Flexible CLI**: monitor any folder or the whole project
- **Easy to extend and test** (modular code, pytest support)

## Installation

```sh
pip install ruffit
```
Or, for local development:
```sh
pip install -e .
```

## Usage

Monitor all Python files in the project:
```sh
ruffit all
```

Monitor only a specific folder (e.g., `tests`):
```sh
ruffit tests
```

Enable autofix with ruff check:
```sh
ruffit . --autofix
```

If the folder does not exist, ruffit will give an error and exit.

## CLI Options

- `folder` (argument): Folder to monitor (default: current directory). Use `all` to monitor the whole project, or just leave it blank.
- `--autofix`: Enable autofix with ruff check.

## Development & Testing

- Tests are in the `tests/` folder and use `pytest`.
- To install test dependencies:
  ```sh
  pip install .[test]
  ```
- To run tests:
  ```sh
  pytest
  ```

## Contributing

Pull requests and issues are welcome!

## License

MIT

## Troubleshooting: Command Not Found

If you see an error like:

```
'ruffit' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

This usually means the Python Scripts directory is not in your PATH, or you are not in the correct virtual environment.

- If you are using a virtual environment, make sure it is activated before installing and running ruffit:
  ```powershell
  .venv\Scripts\Activate
  pip install ruffit
  ruffit
  ```
- If you still see the error, you can always run ruffit with:
  ```sh
  python -m ruffit
  ```

See the [Python documentation](https://docs.python.org/3/using/cmdline.html#environment-variables) for more on PATH and script locations.
