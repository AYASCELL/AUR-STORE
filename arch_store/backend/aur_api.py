import requests
import json

AUR_RPC_URL = "https://aur.archlinux.org/rpc/"

class AurApi:
    def __init__(self):
        self.session = requests.Session()

    def search(self, query):
        """
        Search for packages in the AUR.
        """
        params = {
            'v': 5,
            'type': 'search',
            'arg': query
        }
        try:
            response = self.session.get(AUR_RPC_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if 'results' in data:
                return data['results']
            return []
        except requests.RequestException as e:
            print(f"Error searching AUR: {e}")
            return []

    def get_info(self, package_names):
        """
        Get detailed info for a list of packages.
        """
        if isinstance(package_names, str):
            package_names = [package_names]
            
        params = {
            'v': 5,
            'type': 'info',
            'arg[]': package_names
        }
        try:
            response = self.session.get(AUR_RPC_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if 'results' in data:
                return data['results']
            return []
        except requests.RequestException as e:
            print(f"Error getting package info: {e}")
            return []
