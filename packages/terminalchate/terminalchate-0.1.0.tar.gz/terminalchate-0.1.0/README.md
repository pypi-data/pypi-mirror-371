# Terminal Chat

## Tiny terminal chat with an asyncio server and CLI client. Python 3.12+.

## Install
```
pip3 install terminalchate
```

## Run the server
```
terminalchate-server --host 0.0.0.0 --port 9000
```

## Connect a client
```
terminalchate 127.0.0.1 9000 --name alice
```
In another terminal then
```
terminalchate 127.0.0.1 9000 --name bob
```

Type to chat. Commands:

* /nick <name> change nickname
* /quit leave