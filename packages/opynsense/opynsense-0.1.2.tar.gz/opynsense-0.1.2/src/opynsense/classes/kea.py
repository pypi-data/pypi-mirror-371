class KeaDHCPv4():
    def __init__(self, parent):
        self.parent = parent
        self.base_endpoint = '/kea/dhcpv4'
        
    def get(self):
        endpoint = f'{self.base_endpoint}/get'
        return self.parent.get(endpoint)
        
    def Reservation(self):
        return self.ReservationClass(self)

    class ReservationClass():
        def __init__(self, parent):
            self.parent = parent

        def get(self):
            endpoint = f'{self.parent.base_endpoint}/get_reservation'
            return self.parent.parent.get(endpoint)
        
        def search(self):
            endpoint = f'{self.parent.base_endpoint}/search_reservation'
            return self.parent.parent.get(endpoint)
        
class KeaLeasev4():
    def __init__(self, parent):
        self.parent = parent
        self.base_endpoint = '/kea/leases4'
        
    def search(self, interface_description=None):
        endpoint = f'{self.base_endpoint}/search'
        
        response = self.parent.get(endpoint)
        if interface_description is not None:
            if isinstance(interface_description, str):
                return [item for item in response['rows'] if item.get('if_descr') == interface_description]
            elif isinstance(interface_description, list):
                return [item for item in response['rows'] if item.get('if_descr') in interface_description]
        return response