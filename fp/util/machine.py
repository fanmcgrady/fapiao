'''
distinguish
'''

import uuid


def mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


servers = dict(S11='80:18:44:e4:24:b0',
               S60='ac:1f:6b:24:3f:c2',
               DGX='')


def is_(machine_name):
    machine_name = machine_name.upper()
    if not machine_name in servers.keys():
        return False
    mac = mac_address()
    return mac == servers[machine_name.upper()]
