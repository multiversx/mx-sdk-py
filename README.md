# mx-sdk-py

The Python SDK for interacting with MultiversX. It's an all in one sdk that can be used to create transactions (including smart contract calls and deployments), sign and broadcast transactions, create wallets and many more.

## Documentation

- [Cookbook](./examples/v1.ipynb)
- [Auto-generated documentation](https://multiversx.github.io/mx-sdk-py/)

## Development setup

### Virtual environment

Create a virtual environment and install the dependencies:

```
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt --upgrade
```

Install development dependencies, as well:

```
pip install -r ./requirements-dev.txt --upgrade
```

Allow `pre-commit` to automatically run on `git commit`:
```
pre-commit install
```

Above, `requirements.txt` should mirror the **dependencies** section of `pyproject.toml`.

If using VSCode, restart it or follow these steps:
 - `Ctrl + Shift + P`
 - _Select Interpreter_
 - Choose `./venv/bin/python`.

### Tests

Run the tests as follows:

This command runs all tests:
```
pytest .
```

If you want to skip network interaction tests run:
```
pytest -m "not networkInteraction"
```

We have some tests fetching mainnet transactions that are quite time consuming. To skip those, run this command:
```
pytest -m "not mainnet"
```

### Generate test coverage report

First, we run the tests using coverage:
```sh
coverage run -m pytest .
```

Then, we can generate a report in the terminal using:
```sh
coverage report
```

We can also generate a html report using:
```sh
coverage html
```

### Regenerating the docs

Each time a new module/submodule is added it needs to be added to the docs, as well. To do so `cd` in the root directory then run the following command:
```bash
sphinx-apidoc -f -o docs/ multiversx_sdk/ '*_test.py' '*constants.py'
```

This command will regenerate the `.rst` files for each module, excluding the tests and the `constants.py` files.

Also, each time a new version is released, the [**conf.py**](/docs/conf.py) file should be updated accordingly.
