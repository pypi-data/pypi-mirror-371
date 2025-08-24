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
            return self.parent.parent.get(endpoint)['rows']

        def search(self, interface_description=None):
            endpoint = f'{self.parent.base_endpoint}/search_reservation'
            response = self.parent.parent.get(endpoint)['rows']

            if interface_description is not None:
                interface_list = self.parent.parent.Interface().get()
                subnet_to_name = {iface['routes'][0]: iface['description'] for iface in interface_list if 'routes' in iface}

                if isinstance(interface_description, str):
                    response = [item for item in response if subnet_to_name.get(item['subnet']) == interface_description]
                elif isinstance(interface_description, list):
                    response = [item for item in response if subnet_to_name.get(item['subnet']) in interface_description]

            return response
        
class KeaLeasev4():
    def __init__(self, parent):
        self.parent = parent
        self.base_endpoint = '/kea/leases4'
        
    def search(self, interface_description=None):
        endpoint = f'{self.base_endpoint}/search'
        
        response = self.parent.get(endpoint)['rows']
        if interface_description is not None:
            if isinstance(interface_description, str):
                return [item for item in response if item.get('if_descr') == interface_description]
            elif isinstance(interface_description, list):
                return [item for item in response if item.get('if_descr') in interface_description]
        return response