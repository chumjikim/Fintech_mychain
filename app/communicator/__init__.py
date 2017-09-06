import socket
import threading
import time

import zmq

from app import log
from app import node

PING_PORT_NUMBER = 3399
PING_MSG_SIZE = 1
PING_INTERVAL = 5  # Once per second


def start():
    def find_node_thread():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', PING_PORT_NUMBER))

        t = threading.Thread(target=find_node_thread)
        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)

        ping_at = time.time()

        # is_running
        while True:
            timeout = ping_at - time.time()
            if timeout < 0:
                timeout = 0
            try:
                events = dict(poller.poll(1000 * timeout))
            except KeyboardInterrupt:
                print("interrupted")
                break

        if sock.fileno() in events:
            msg, addrinfo = sock.recvfrom(PING_MSG_SIZE)
            ip = addrinfo[0]
            n = node.Node(ip)
            if node.add_node(n):
                # print('Find ' + ip)
                log.write('Find ' + ip)

        if time.time() >= ping_at:
            print('Finding a node...')
            sock.sendto(b'!', 0, ("255.255.255.255", PING_PORT_NUMBER))
            ping_at = time.time() + PING_INTERVAL

        t.start()
