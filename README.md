Scistarter-Recommendation-Algorithms
------

## Install

First install `python3` and `python3-pip`, then

```bash
pip3 install -r requirements.txt
```

## Deploy

```bash
export HOST=127.0.0.1 # host & port to listen on
export PORT=8080
export INTVL=86400 # interval between each update, in seconds
bash deploy.sh
```

This script will periodically update the data and run the web interface server.
