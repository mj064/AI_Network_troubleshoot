"""
NetBox API Integration Module
Sync network device inventory from NetBox
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class NetBoxAPI:
    """Interface with NetBox API for device inventory"""
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize NetBox API connection
        
        Args:
            base_url: NetBox API base URL (e.g., 'https://netbox.company.com/api')
            api_token: NetBox API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make API request to NetBox"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=15)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, timeout=15)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"NetBox API error: {e}")
            return None
    
    def get_devices(self, limit: int = 1000) -> List[Dict]:
        """
        Get all devices from NetBox
        
        Returns:
            List of device dictionaries
        """
        devices = []
        offset = 0
        
        while True:
            endpoint = f"/dcim/devices/?limit={limit}&offset={offset}"
            response = self._request(endpoint)
            
            if not response or 'results' not in response:
                break
            
            devices.extend(response['results'])
            
            if not response.get('next'):
                break
            
            offset += limit
        
        return devices
    
    def get_device_by_name(self, name: str) -> Optional[Dict]:
        """Get specific device by name"""
        endpoint = f"/dcim/devices/?name={name}"
        response = self._request(endpoint)
        
        if response and response.get('results'):
            return response['results'][0]
        return None
    
    def get_device_interfaces(self, device_id: int) -> List[Dict]:
        """Get interfaces for a device"""
        endpoint = f"/dcim/interfaces/?device_id={device_id}"
        response = self._request(endpoint)
        
        if response and 'results' in response:
            return response['results']
        return []
    
    def get_sites(self) -> List[Dict]:
        """Get all sites (locations)"""
        endpoint = "/dcim/sites/"
        response = self._request(endpoint)
        
        if response and 'results' in response:
            return response['results']
        return []
    
    def get_device_types(self) -> List[Dict]:
        """Get all device types"""
        endpoint = "/dcim/device-types/"
        response = self._request(endpoint)
        
        if response and 'results' in response:
            return response['results']
        return []
    
    def get_manufacturers(self) -> List[Dict]:
        """Get all device manufacturers"""
        endpoint = "/dcim/manufacturers/"
        response = self._request(endpoint)
        
        if response and 'results' in response:
            return response['results']
        return []
    
    def create_device(self, device_data: Dict) -> Optional[Dict]:
        """Create a new device in NetBox"""
        endpoint = "/dcim/devices/"
        return self._request(endpoint, method='POST', data=device_data)
    
    def update_device(self, device_id: int, device_data: Dict) -> Optional[Dict]:
        """Update device in NetBox"""
        endpoint = f"/dcim/devices/{device_id}/"
        return self._request(endpoint, method='PATCH', data=device_data)


class NetBoxSyncService:
    """Service to sync NetBox devices with local database"""
    
    def __init__(self, netbox_api: NetBoxAPI, db_session):
        self.netbox = netbox_api
        self.db = db_session
    
    def sync_devices(self) -> Dict[str, int]:
        """
        Sync all devices from NetBox to local database
        
        Returns:
            Dictionary with sync statistics
        """
        from src.backend.utils.enterprise_models import NetworkDevice
        
        stats = {'created': 0, 'updated': 0, 'failed': 0}
        
        try:
            devices = self.netbox.get_devices()
            
            for nb_device in devices:
                try:
                    # Check if device exists
                    existing = self.db.query(NetworkDevice).filter_by(
                        device_id=str(nb_device.get('id'))
                    ).first()
                    
                    device_dict = {
                        'device_id': str(nb_device.get('id')),
                        'device_name': nb_device.get('name', 'Unknown'),
                        'device_type': nb_device.get('device_type', {}).get('model', 'Unknown'),
                        'vendor': nb_device.get('device_type', {}).get('manufacturer', {}).get('name', 'Unknown'),
                        'ip_address': nb_device.get('primary_ip', {}).get('address', ''),
                        'location': nb_device.get('site', {}).get('name', 'Unknown'),
                        'status': 'UP' if nb_device.get('status', {}).get('value') == 'active' else 'DOWN',
                        'last_seen': datetime.utcnow()
                    }
                    
                    if existing:
                        # Update existing device
                        for key, value in device_dict.items():
                            setattr(existing, key, value)
                        stats['updated'] += 1
                    else:
                        # Create new device
                        new_device = NetworkDevice(**device_dict)
                        self.db.add(new_device)
                        stats['created'] += 1
                
                except Exception as e:
                    print(f"Failed to sync device: {e}")
                    stats['failed'] += 1
            
            self.db.commit()
        
        except Exception as e:
            print(f"Device sync failed: {e}")
            self.db.rollback()
        
        return stats
    
    def sync_device(self, device_id: str) -> bool:
        """Sync a single device from NetBox"""
        from src.backend.utils.enterprise_models import NetworkDevice
        
        try:
            nb_device = self.netbox.get_device_by_name(device_id)
            if not nb_device:
                return False
            
            existing = self.db.query(NetworkDevice).filter_by(device_id=device_id).first()
            
            device_dict = {
                'device_id': str(nb_device.get('id')),
                'device_name': nb_device.get('name', 'Unknown'),
                'device_type': nb_device.get('device_type', {}).get('model', 'Unknown'),
                'vendor': nb_device.get('device_type', {}).get('manufacturer', {}).get('name', 'Unknown'),
                'ip_address': nb_device.get('primary_ip', {}).get('address', ''),
                'location': nb_device.get('site', {}).get('name', 'Unknown'),
                'status': 'UP' if nb_device.get('status', {}).get('value') == 'active' else 'DOWN',
                'last_seen': datetime.utcnow()
            }
            
            if existing:
                for key, value in device_dict.items():
                    setattr(existing, key, value)
            else:
                new_device = NetworkDevice(**device_dict)
                self.db.add(new_device)
            
            self.db.commit()
            return True
        
        except Exception as e:
            print(f"Sync failed: {e}")
            self.db.rollback()
            return False
