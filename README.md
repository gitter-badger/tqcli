# TQCli

## Setup

Setup and activate virtualenv:


```
virtualenv ~/.virtualenvs/tqcli
source ~/.virtualenv/tqcli/bin/activate
```

Install dependencies:

```
pip install -r requirements
```


## Usage

```
python tq.py --input <dataset.file> --token <user-token> --datasource-id <datasource-id>
```


## Test
To test the package run the mock server that's under tests/

 ```
 python tests/tqserver.py
 ```
