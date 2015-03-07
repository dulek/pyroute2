from pyroute2.netlink import NLM_F_REQUEST
from pyroute2.netlink import NLM_F_DUMP
from pyroute2.netlink import NETLINK_NETFILTER
from pyroute2.netlink import nla
from pyroute2.netlink.nlsocket import NetlinkSocket
from pyroute2.netlink.nfnetlink import NFNL_SUBSYS_IPSET
from pyroute2.netlink.nfnetlink import nfgen_msg


IPSET_MAXNAMELEN = 32

IPSET_CMD_NONE = 0
IPSET_CMD_PROTOCOL = 1  # Return protocol version
IPSET_CMD_CREATE = 2  # Create a new (empty) set
IPSET_CMD_DESTROY = 3  # Destroy a (empty) set
IPSET_CMD_FLUSH = 4  # Remove all elements from a set
IPSET_CMD_RENAME = 5  # Rename a set
IPSET_CMD_SWAP = 6  # Swap two sets
IPSET_CMD_LIST = 7  # List sets
IPSET_CMD_SAVE = 8  # Save sets
IPSET_CMD_ADD = 9  # Add an element to a set
IPSET_CMD_DEL = 10  # Delete an element from a set
IPSET_CMD_TEST = 11  # Test an element in a set
IPSET_CMD_HEADER = 12  # Get set header data only
IPSET_CMD_TYPE = 13  # 13: Get set type


class ipset_msg(nfgen_msg):
    nla_map = (('IPSET_ATTR_UNSPEC', 'none'),
               ('IPSET_ATTR_PROTOCOL', 'uint8'),
               ('IPSET_ATTR_SETNAME', 'asciiz'),
               ('IPSET_ATTR_TYPENAME', 'asciiz'),
               ('IPSET_ATTR_REVISION', 'uint8'),
               ('IPSET_ATTR_FAMILY', 'uint8'),
               ('IPSET_ATTR_FLAGS', 'hex'),
               ('IPSET_ATTR_DATA', 'data'),
               ('IPSET_ATTR_ADT', 'data'),
               ('IPSET_ATTR_LINENO', 'hex'),
               ('IPSET_ATTR_PROTOCOL_MIN', 'hex'))

    class data(nla):
        nla_map = ((0, 'IPSET_ATTR_UNSPEC', 'none'),
                   (1, 'IPSET_ATTR_IP', 'ipset_ip'),
                   (1, 'IPSET_ATTR_IP_FROM', 'ipset_ip'),
                   (2, 'IPSET_ATTR_IP_TO', 'ipset_ip'),
                   (3, 'IPSET_ATTR_CIDR', 'hex'),
                   (4, 'IPSET_ATTR_PORT', 'hex'),
                   (4, 'IPSET_ATTR_PORT_FROM', 'hex'),
                   (5, 'IPSET_ATTR_PORT_TO', 'hex'),
                   (6, 'IPSET_ATTR_TIMEOUT', 'hex'),
                   (7, 'IPSET_ATTR_PROTO', 'recursive'),
                   (8, 'IPSET_ATTR_CADT_FLAGS', 'hex'),
                   (9, 'IPSET_ATTR_CADT_LINENO', 'hex'),
                   (10, 'IPSET_ATTR_MARK', 'hex'),
                   (11, 'IPSET_ATTR_MARKMASK', 'hex'),
                   (17, 'IPSET_ATTR_GC', 'hex'),
                   (18, 'IPSET_ATTR_HASHSIZE', 'be32'),
                   (19, 'IPSET_ATTR_MAXELEM', 'be32'),
                   (20, 'IPSET_ATTR_NETMASK', 'hex'),
                   (21, 'IPSET_ATTR_PROBES', 'hex'),
                   (22, 'IPSET_ATTR_RESIZE', 'hex'),
                   (23, 'IPSET_ATTR_SIZE', 'hex'),
                   (24, 'IPSET_ATTR_ELEMENTS', 'hex'),
                   (25, 'IPSET_ATTR_REFERENCES', 'be32'),
                   (26, 'IPSET_ATTR_MEMSIZE', 'be32'))

        class ipset_ip(nla):
            nla_map = (('IPSET_ATTR_UNSPEC', 'none'),
                       ('IPSET_ATTR_IPADDR_IPV4', 'ip4addr'),
                       ('IPSET_ATTR_IPADDR_IPV6', 'ip6addr'))


class IPSet(NetlinkSocket):

    policy = {IPSET_CMD_PROTOCOL: ipset_msg,
              IPSET_CMD_LIST: ipset_msg}

    def __init__(self):
        super(IPSet, self).__init__(family=NETLINK_NETFILTER)
        policy = dict([(x | (NFNL_SUBSYS_IPSET << 8), y)
                       for (x, y) in self.policy.items()])
        self.register_policy(policy)

    def request(self, msg, msg_type,
                msg_flags=NLM_F_REQUEST | NLM_F_DUMP):
        return self.nlm_request(msg,
                                msg_type | (NFNL_SUBSYS_IPSET << 8),
                                msg_flags)

    def list(self, name=None):
        msg = ipset_msg()
        msg['attrs'] = [['IPSET_ATTR_PROTOCOL', 6]]
        if name is not None:
            msg['attrs'].append(['IPSET_ATTR_SETNAME', name])
        return self.request(msg, IPSET_CMD_LIST)
