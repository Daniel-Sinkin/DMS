# DMS
Learning how to make Guis in python.

![Screenshot](images/Screenshot%202024-11-29%20at%2001.41.39.png)

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
* [PyQT Documentation](https://doc.qt.io/qtforpython-6/)
* [Pyro5 Documentation](https://pyro5.readthedocs.io/en/latest/)