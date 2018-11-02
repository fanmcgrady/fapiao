'''
distinguish
'''

import uuid


def mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

servers = dict(S11='80:18:44:e4:24:b0',
               S60='ac:1f:6b:24:3f:c2',
               DGX='9d:7e:97:c8:4a:af')

def is_(machine_name):
    '''
    Args
        machine_name [str]: name of server, can be
            - 's11': *.*.*.11 server
            - 's60': *.*.*.60 server
            - 'dgx': DGX station
            Both lower-case and upper-case letters are ok.
    '''
    machine_name = machine_name.upper()
    if not machine_name in servers.keys():
        return False
    mac = mac_address()
    return mac == servers[machine_name.upper()]