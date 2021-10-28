# coding:utf-8

import os
import time
import select
import socket
import struct
import sys


class Convert2Icmp:

    def __init__(self, host, payload):
        self.error = 0
        self.HOST = host
        self.payload = payload

    # 校验
    @staticmethod
    def checksum(packet):
        sum = 0
        count_to = (len(packet) // 2) * 2
        count = 0

        while count < count_to:
            sum += ((packet[count + 1] << 8) | packet[count])
            count += 2
        if count_to < len(packet):
            sum += packet[len(packet) - 1]
            sum = sum & 0xffffffff

        sum = (sum >> 16) + (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def send_one_ping(self, rawsocket, dst_addr, icmp_id, icmp_sq):
        length = len(self.payload)
        payload = bytes(self.payload, encoding="utf8")
        dst_addr = socket.gethostbyname(dst_addr)
        packet = struct.pack('!BBHHH' + str(length + 4) + 's', 8, 0, 0, icmp_id, icmp_sq, b';;' + payload + b';;')
        chksum = self.checksum(packet)
        packet = struct.pack('!BBHHH' + str(length + 4) + 's', 8, 0, chksum, icmp_id, icmp_sq, b';;' + payload + b';;')
        send_time = time.time()
        try:
            rawsocket.sendto(packet, (dst_addr, 80))
        except OSError as bigPacket:
            self.error = 1
        return send_time, dst_addr

    @staticmethod
    def recv_one_ping(rawsocket, icmp_id, icmp_sq, time_sent, timeout):
        while True:
            started_select = time.time()
            what_ready = select.select([rawsocket], [], [], timeout)
            how_long_in_select = (time.time() - started_select)
            # Timeout
            if what_ready[0] == []:
                return -1
            time_received = time.time()
            received_packet, addr = rawsocket.recvfrom(1024 * 500 * 2)
            icmp_header = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(
                "!BBHHH", icmp_header
            )
            if type == 0 and packet_id == icmp_id and sequence == icmp_sq:
                return time_received - time_sent
            timeout = timeout - how_long_in_select
            if timeout <= 0:
                return -1

    def one_ping(self, dst_addr, icmp_sq, timeout=2):
        try:
            rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        except socket.error as e:
            if e.errno == 1:
                msg = e.message + (" please run as root ")
                raise socket.error(msg)
            raise

        icmp_id = os.getpid() & 0xFFFF

        send_time, addr = self.send_one_ping(rawsocket, dst_addr, icmp_id, icmp_sq)
        time = self.recv_one_ping(rawsocket, icmp_id, icmp_sq, send_time, timeout)
        return time, addr

    def _ping(self, timeout=10):
        dst_addr = self.HOST
        time, addr = self.one_ping(dst_addr, 3, timeout)
        if time > 0:
            sys.stdout.write("[+] send to {0} success({1}ms)\n".format(addr, int(time * 1000)))
        elif os.name == "nt" and time <= 0:
            sys.stdout.write("[+] send to {0} success({1}ms)\n".format(addr, int(time * 1000)))
        else:
            if self.error:
                sys.stdout.write("[-] the packet is too loooong\n")
            sys.stdout.write("[-] something error\n".format(addr))


class Listener:
    def __init__(self, host, is_server=0):
        self.host = host
        self.is_server = is_server

    def os_listener(self):
        HOST = self.host
        if os.name == "nt":
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP
        rawSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        rawSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rawSocket.bind((HOST, 0))
        rawSocket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        if os.name == "nt":
            rawSocket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        if self.is_server == 1:
            rawSocket.settimeout(8)
            try:
                pkt = rawSocket.recvfrom(2048 * 500)
                return pkt
            except socket.timeout as e:
                return ";;"
        else:
            pkt = rawSocket.recvfrom(2048 * 500)
            return pkt
