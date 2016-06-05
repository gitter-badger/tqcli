    
    ___________________    _________  .____     .___ 
    \__    ___/\_____  \   \_   ___ \ |    |    |   |
      |    |    /  / \  \  /    \  \/ |    |    |   |
      |    |   /   \_/.  \ \     \____|    |___ |   |
      |____|   \_____\ \_/  \______  /|_______ \|___|
                      \__>         \/         \/     

                                           TranQuant Client
                                                Version 1.0


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


## The flow

- TQCli starts to read the file in chunks, the size of the chunks is set in `config.py`

- Builds a payload: 
```
    {
        'datasource_id': 'this-is-a-datasource-id', 
        'from_byte': 0, 
        'remained_bytes': 0, 
        'to_byte': 10000, 
        'chunk': 'DATA'
    }
```

- Makes a POST request to `TQ_DATASOURCE_UPLOAD_ENDPOINT`
