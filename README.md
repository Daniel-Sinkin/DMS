# DMS
The Daniel Management System (Prolly rename this to Daniel's Management System later on)

# How to launch
Need to have 3 seperate threads running, the command
```
python -m Pyro5.nameserver
```
established an IPC nameserver,
```
python3 data_provider.py
```
starts the DataProvider and
```
python3 client.py
```
starts the client. They should be run in that order.

# References
* PyQT
    * [Documentation](https://doc.qt.io/qtforpython-6/)
    * [PythonWiki](https://wiki.python.org/moin/PyQt)