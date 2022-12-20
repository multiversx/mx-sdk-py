# sdk-erdpy-network-providers

Network providers for **erdpy**.

## Documentation
[docs.elrond.com](https://docs.elrond.com/sdk-and-tools/erdpy/erdpy/)

## Development setup

Create a virtual environment and install the dependencies:

```
python3 -m venv ./.venv
source ./.venv/bin/activate
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
 - Choose `./.venv/bin/python`.
 
### Tests

Run the tests as follows:

```
pytest .
```

### Linting

First, install [`pyright`](https://github.com/microsoft/pyright) as follows:

```
npm install --global pyright
```

Run `pyright`:

```
pyright
```

Run `flake8`:

```
flake8 erdpy_core
```
