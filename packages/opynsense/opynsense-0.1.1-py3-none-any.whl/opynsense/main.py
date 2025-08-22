import re
from restpylot import RestClient

from .classes.kea import KeaDHCPv4, KeaLeasev4

class OpnSense(RestClient):
    def __init__(self, auth, base_url='https://router.oghomelab.com/api', debug=False):
        headers = dict(
            Accept = 'application/json'
        )
        super().__init__(base_url, auth=auth, headers=headers, debug=debug)
        
    def _regex_ip(ip_address):
        ip_regex = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'
        
        return re.match(ip_regex, ip_address)

    def _regex_mac(mac_address):
        mac_regex = r'^([0-9abcdef]{2}:){5}[0-9abcdef]{2}$'
        
        return re.match(mac_regex, mac_address)

    def KeaDHCPv4(self):
        return KeaDHCPv4(self)
    
    def KeaLeasev4(self):
        return KeaLeasev4(self)