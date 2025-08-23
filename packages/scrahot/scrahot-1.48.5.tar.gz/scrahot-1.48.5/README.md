# Instructions to execute

## Running multiple instances with uvx:
# Instance 1
```sh 
FLASK_PORT=5005 MITMPROXY_PORT=6005 uvx --python 3.12 scrahot 
```

# Instance 2  
```sh 
FLASK_PORT=5006 MITMPROXY_PORT=6006 uvx --python 3.12 scrahot
```

# Instance 3
```sh 
FLASK_PORT=5007 MITMPROXY_PORT=6007 uvx --python 3.12 scrahot
``` 

## Alternatively, using command line arguments:
# Instance 1
```sh 
uvx --python 3.12 scrahot -- --port 5005 --proxy-port 6005
```

# Instance 2
```sh
uvx --python 3.12 scrahot -- --port 5006 --proxy-port 6006
```