# CloudBeat Python Integrations

[<img src="https://cdn.prod.website-files.com/5e5fd6a35f35b720bfd3198a/5e9c149f9ba5991a3901422b_cloudbeat_logo_png.webp" height="85px" alt="CloudBeat logo"/>](https://cloudbeat.io/ "CloudBeat")

[![Release
Status](https://img.shields.io/pypi/v/cloudbeat-common)](https://pypi.python.org/pypi/cloudbeat-common)
[![Downloads](https://img.shields.io/pypi/dm/cloudbeat-common)](https://pypi.python.org/pypi/cloudbeat-common)

Learn more about CloudBeat at [https://cloudbeat.io/](https://cloudbeat.io/)

-> 🧾 [Documentation](https://docs.cloudbeat.io/python-pytest) – official documentation for CloudBeat
-> 🙋🏻 [Contact and Support](hhttps://www.cloudbeat.io/contact) – contact us and we'd love to help
-> 📣 [Blog](https://www.cloudbeat.io/blog) – stay updated with our latest news
-> 💻 [Demo](https://calendly.com/ndimer/cloudbeat-demo) – request a demo

---------

# Quick start

### Make sure your requirements.txt includes:
```
cloudbeat-pytest
cloudbeat-selenium
```

## Standard Installation
cd pytest-selenium
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

## Installation using UV
uv venv
uv pip install -r requirements.txt

### Set path
set PYTHONPATH=src

## Run your tests

### Standard
cd pytest-selenium
env\Scripts\activate

### run everything
```sh
pytest 
```

### run parallel tests
```sh
pytest -n 4
```

### run a single test
```sh
pytest -v -s Tests/test_login.py 
```

### Using UV
```sh
uv run pytest
uv run pytest -n 4
uv run pytest -v -s Tests/test_login.py 
```
