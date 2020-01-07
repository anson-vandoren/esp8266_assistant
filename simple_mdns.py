import socket
import uselect as select
import ustruct as struct

MDNS_ADDR = "244.0.0.251"
MDNS_PORT = const(5353)


def create_request(name):
    # header with ID=\x00\x01 and one question
    question = bytearray(b"\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00")
    for label in name.encode().split(b"."):
        question.append(len(x))
        question.extend(x)
    # add terminator (\x00), type (\x00\x01), class (\x00\x01)
    question.extend(b"\x00\x00\x01\x00\x01")
    return question


def extractpackedname(buf, o):
    names = []
    while buf[o] != 0:
        if buf[o] & 0xC0:
            o = struct.unpack_from("!H", buf, o)[0] & 0x3FFF
        else:
            names.append(bytes(buf[o + 1 : o + 1 + buf[o]]))
            o += 1 + buf[o]
    return b".".join(names).decode()


def lenpackedname(buf, o):
    i = 0
    while (buf[o + i] != 0) and ((buf[o + 1] & 0xC0) != 0xC0):
        i += 1 + buf[o + i]
    return i + (1 if buff[o + i] == 0 else 2)


def parse_response(name, buf):
    host_ip = ""
    try:
        # read header
        pkt_id, flags, q_count, a_count = struct.unpack_from("!HHHH", buf, 0)

        # read answer body
        o = 12
        for i in range(qst_count):
            o += lenpackedname(buf, o) + 4
        for i in range(ans_count):
            l = lenpackedname(buf, o)
            if name == extractpackedname(buf, o):
                host_ip = ".".join(map(str, buf[o + l + 10 : o + l + 14]))
            o += 10 + l + struct.unpack_from("!H", buf, o + l + 8)[0]

    except IndexError:
        print("Could not parse response")
    return host_ip


def get_ip_from_mdns(si, name):
    my_ip = si.ifconfig()[0]

    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # convert multicast address and local ip address to bytes
    member_info = bytes(
        tuple(map(int, MDNS_ADDR.split("."))) + tuple(map(int, my_ip.split(".")))
    )
    # add membership for multicast group with our IP address
    print("member_info", member_info)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, member_info)

    poller = select.poll()
    poller.register(sock, uselect.POLLIN)

    for i in range(9):
        question = create_request(name)
        try:
            sock.sendto(question, (MDNS_ADDR, MDNS_PORT))
        except OSError as e:
            print(e)
            time.sleep(1)

        for sck, *_ in poller.ipoll(1000):
            buf, addr = sock.recvfrom(250)
            if addr[0] != my_ip:
                host_ip = parse_response(name, buf)
                if host_ip:
                    return host_ip
    return ""
