    
    ___________________    _________  .____     .___ 
    \__    ___/\_____  \   \_   ___ \ |    |    |   |
      |    |    /  / \  \  /    \  \/ |    |    |   |
      |    |   /   \_/.  \ \     \____|    |___ |   |
      |____|   \_____\ \_/  \______  /|_______ \|___|
                      \__>         \/         \/     

                                           TranQuant Client
                                                Version 1.0


## Setup

[![Join the chat at https://gitter.im/tqcli/Lobby](https://badges.gitter.im/tqcli/Lobby.svg)](https://gitter.im/tqcli/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

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

Upload a new dataset to an existing datasouce

```
python tq.py --input <dataset.file> --token <user-token> --datasource-id <datasource-id>
```

ex)

```
$ python tq.py --input data\all-shakespeare.txt --token SECRET_TOKEN --datasource-id 524b0f9f-d829-4ea7-8e62-e06d21b3dd13
Initiated upload
Uploading part 1 of 2 (5242880 bytes)
Uploading part 2 of 2 (99881 bytes)
Upload complete!

```

## The flow

- TQCli starts to read the file in chunks, the size of the chunks is set in `config.py`
- Creates a multipart request
- Uploads each part of the file
- Completes the multipart request when all parts are uploaded