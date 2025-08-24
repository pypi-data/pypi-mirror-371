# OpynSense

OpynSense is a Python client library for interacting with the OpnSense router API, providing convenient access to DHCP and lease management via Kea. It is designed for automation and integration with network infrastructure in homelab or enterprise environments.

## Features

- Authenticate and manage sessions with OpnSense
- Retrieve DHCPv4 configuration and reservations
- Search and filter DHCP leases by interface description
- Extensible for additional OpnSense API endpoints

## Installation

Install via pip (after packaging):

```bash
pip install opynsense
```

## Usage

```python
from opynsense.main import OpnSense

# Initialize client
opnsense = OpnSense(auth='your_auth_token', base_url='https://your-opnsense/api')

# Access Kea DHCPv4 configuration
dhcp = opnsense.KeaDHCPv4()
config = dhcp.get()

# Access DHCP reservations
reservations = dhcp.Reservation().get()

# Search DHCP reservations
search_results = dhcp.Reservation().search()

# Access and search DHCP leases
leases = opnsense.KeaLeasev4().search(interface_description='LAN')
```

## Project Structure

- `src/opynsense/main.py`: Main OpnSense client class
- `src/opynsense/classes/kea.py`: Kea DHCP and lease management classes
- `tests/`: Unit tests

## License

See [LICENSE](LICENSE) for details.
