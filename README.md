    
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
source ~/.virtualenvs/tqcli/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

## Usage

```
python tq.py --input <dataset.file> --token <user-token> --datasource-id <datasource-id> --dataset-id <dataset-id>
```

## The flow

- TQCli starts to read the file in chunks, the size of the chunks is set in `config.py`
- Creates a multipart request
- Uploads each part of the file
- Completes the multipart request when all parts are uploaded