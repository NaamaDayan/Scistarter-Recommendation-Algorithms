Scistarter-Recommendation-Algorithms
------

## Install

First install `python3` and `python3-pip`, then

```bash
pip3 install -r requirements.txt
```

## Initialize

```bash
bash init.sh
```

This will initialize the user-algo mapping file and the log file.

## Deploy

```bash
export HOST=127.0.0.1 # host & port to listen on
export PORT=8080
export INTVL=600 # interval between each update, in seconds
bash Scistarter-Recommendation-Algorithms/deploy.sh
bash s3sync.sh
```

This script will periodically update the data and run the web interface server.
