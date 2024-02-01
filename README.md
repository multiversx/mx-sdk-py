# mx-sdk-py

The Python SDK for interacting with MultiversX. It's an all in one sdk that can be used to create transactions (including smart contract calls and deployments), sign and broadcast transactions, create wallets and many more.

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

Above, `requirements.txt` should mirror the **dependencies** section of `pyproject.toml`.

If using VSCode, restart it or follow these steps:
 - `Ctrl + Shift + P`
 - _Select Interpreter_
 - Choose `./venv/bin/python`.

### Tests

Run the tests as follows:

```
pytest .
```
