class Interface():
    def __init__(self, parent):
        self.parent = parent
        self.base_endpoint = '/interfaces'
        
    def get(self, status=None, name=None, addressv4=None):
        response = self.parent.get(f"{self.base_endpoint}/overview/interfaces_info")['rows']
        
        if status is not None:
            response = [item for item in response if item.get('status') == status]
        
        if name is not None:
            if isinstance(name, str):
                response = [item for item in response if item.get('description') == name]
            elif isinstance(name, list):
                response = [item for item in response if item.get('description') in name]
        
        if addressv4 is not None:
            if isinstance(addressv4, str):
                response = [item for item in response if item.get('addr4') == addressv4]
            elif isinstance(addressv4, list):
                response = [item for item in response if item.get('addr4') in addressv4]
        return response