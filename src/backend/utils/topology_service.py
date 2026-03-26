"""
Network Topology Module
Visualize network connections and relationships
"""

from typing import Dict, List, Optional
from datetime import datetime


class NetworkNode:
    """Represents a device node in network topology"""
    
    def __init__(self, device_id: str, device_name: str, device_type: str, ip: str, status: str):
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.ip = ip
        self.status = status
        self.connections = []
    
    def to_dict(self) -> Dict:
        return {
            'id': self.device_id,
            'label': self.device_name,
            'type': self.device_type,
            'ip': self.ip,
            'status': self.status,
            'color': self._get_status_color(),
            'size': self._get_node_size()
        }
    
    def _get_status_color(self) -> str:
        """Get node color based on status"""
        color_map = {
            'UP': '#22c55e',
            'DEGRADED': '#eab308',
            'DOWN': '#ef4444',
            'UNKNOWN': '#64748b'
        }
        return color_map.get(self.status, '#64748b')
    
    def _get_node_size(self) -> int:
        """Get node size based on importance"""
        type_size = {
            'Router': 30,
            'Switch': 25,
            'Firewall': 28,
            'Load Balancer': 26,
            'Server': 20,
            'Workstation': 15
        }
        return type_size.get(self.device_type, 20)


class NetworkLink:
    """Represents a connection between nodes"""
    
    def __init__(self, source: str, destination: str, connection_type: str, bandwidth: float = 0):
        self.source = source
        self.destination = destination
        self.connection_type = connection_type
        self.bandwidth = bandwidth
        self.status = 'UP'
        self.utilization = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'target': self.destination,
            'label': f"{self.connection_type} ({self.bandwidth} Mbps)",
            'type': self.connection_type,
            'status': self.status,
            'bandwidth': self.bandwidth,
            'utilization': self.utilization,
            'color': self._get_link_color(),
            'weight': self._get_link_weight()
        }
    
    def _get_link_color(self) -> str:
        """Get link color based on status and utilization"""
        if self.status == 'DOWN':
            return '#ef4444'
        
        if self.utilization > 0.9:
            return '#ef4444'
        elif self.utilization > 0.7:
            return '#eab308'
        else:
            return '#3b82f6'
    
    def _get_link_weight(self) -> float:
        """Get link weight for visualization"""
        return 1.0 + (self.utilization * 3)


class TopologyService:
    """Service for managing network topology"""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.links: List[NetworkLink] = []
    
    def add_device(self, device: Dict) -> bool:
        """Add device as network node"""
        try:
            node = NetworkNode(
                device_id=device.get('device_id'),
                device_name=device.get('device_name'),
                device_type=device.get('device_type', 'Unknown'),
                ip=device.get('ip_address', 'N/A'),
                status=device.get('status', 'UNKNOWN')
            )
            self.nodes[device['device_id']] = node
            return True
        except Exception as e:
            print(f"Failed to add device: {e}")
            return False
    
    def add_connection(self, source_id: str, dest_id: str, connection_type: str, bandwidth: float = 0) -> bool:
        """Add connection between two devices"""
        try:
            if source_id not in self.nodes or dest_id not in self.nodes:
                return False
            
            link = NetworkLink(source_id, dest_id, connection_type, bandwidth)
            self.links.append(link)
            return True
        except Exception as e:
            print(f"Failed to add connection: {e}")
            return False
    
    def get_topology_graph(self) -> Dict:
        """Get graph representation suitable for D3.js visualization"""
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'links': [link.to_dict() for link in self.links],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_device_connections(self, device_id: str) -> List[Dict]:
        """Get all connections for a specific device"""
        connections = []
        
        # Outbound connections
        for link in self.links:
            if link.source == device_id:
                connections.append({
                    'direction': 'outbound',
                    'connected_to': link.destination,
                    'type': link.connection_type,
                    'bandwidth': link.bandwidth
                })
        
        # Inbound connections
        for link in self.links:
            if link.destination == device_id:
                connections.append({
                    'direction': 'inbound',
                    'connected_from': link.source,
                    'type': link.connection_type,
                    'bandwidth': link.bandwidth
                })
        
        return connections
    
    def find_path(self, source: str, destination: str) -> Optional[List[str]]:
        """Find path between two devices (BFS)"""
        if source not in self.nodes or destination not in self.nodes:
            return None
        
        from collections import deque
        
        visited = set()
        queue = deque([(source, [source])])
        
        while queue:
            current, path = queue.popleft()
            
            if current == destination:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for link in self.links:
                if link.source == current and link.destination not in visited:
                    queue.append((link.destination, path + [link.destination]))
        
        return None
    
    def get_network_criticality(self) -> Dict:
        """Identify critical devices and links"""
        criticality = {
            'critical_devices': [],
            'critical_links': [],
            'single_points_of_failure': []
        }
        
        # Devices with high connection count are critical
        connection_count = {}
        for link in self.links:
            connection_count[link.source] = connection_count.get(link.source, 0) + 1
            connection_count[link.destination] = connection_count.get(link.destination, 0) + 1
        
        critical_threshold = len(self.nodes) / 3
        for device_id, count in connection_count.items():
            if count > critical_threshold:
                criticality['critical_devices'].append(device_id)
        
        # Links with high utilization are critical
        for link in self.links:
            if link.utilization > 0.8:
                criticality['critical_links'].append({
                    'source': link.source,
                    'destination': link.destination,
                    'utilization': link.utilization
                })
        
        return criticality
    
    def analyze_redundancy(self) -> Dict:
        """Analyze network redundancy"""
        analysis = {
            'fully_redundant': 0,
            'single_path_only': 0,
            'no_path': 0
        }
        
        # Get critical devices first
        criticality = self.get_network_criticality()
        
        # Check if alternative paths exist between critical devices
        for device in criticality['critical_devices']:
            for other_device in self.nodes:
                if device != other_device:
                    paths = self._find_all_paths(device, other_device)
                    if len(paths) > 1:
                        analysis['fully_redundant'] += 1
                    elif len(paths) == 1:
                        analysis['single_path_only'] += 1
                    else:
                        analysis['no_path'] += 1
        
        return analysis
    
    def _find_all_paths(self, source: str, destination: str, max_depth: int = 10) -> List[List[str]]:
        """Find all paths between two devices"""
        all_paths = []
        
        def dfs(current, target, path, visited):
            if current == target:
                all_paths.append(path[:])
                return
            
            if len(path) > max_depth:
                return
            
            visited.add(current)
            
            for link in self.links:
                if link.source == current and link.destination not in visited:
                    path.append(link.destination)
                    dfs(link.destination, target, path, visited.copy())
                    path.pop()
        
        dfs(source, destination, [source], set())
        return all_paths
    
    def get_topology_summary(self) -> Dict:
        """Get summary statistics about topology"""
        return {
            'total_devices': len(self.nodes),
            'total_connections': len(self.links),
            'average_connections_per_device': len(self.links) * 2 / max(1, len(self.nodes)),
            'network_density': self._calculate_density(),
            'device_types': self._count_device_types(),
            'status_distribution': self._count_device_statuses()
        }
    
    def _calculate_density(self) -> float:
        """Calculate network density (connectivity ratio)"""
        if len(self.nodes) < 2:
            return 0
        
        max_connections = len(self.nodes) * (len(self.nodes) - 1) / 2
        actual_connections = len(self.links)
        
        return actual_connections / max_connections if max_connections > 0 else 0
    
    def _count_device_types(self) -> Dict[str, int]:
        """Count devices by type"""
        type_count = {}
        for node in self.nodes.values():
            type_count[node.device_type] = type_count.get(node.device_type, 0) + 1
        return type_count
    
    def _count_device_statuses(self) -> Dict[str, int]:
        """Count devices by status"""
        status_count = {}
        for node in self.nodes.values():
            status_count[node.status] = status_count.get(node.status, 0) + 1
        return status_count
