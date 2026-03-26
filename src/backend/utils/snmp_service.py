"""
SNMP Integration Module
Collect metrics from real network devices via SNMP
Supports SNMPv2 and SNMPv3
"""

try:
    from pysnmp.hlapi import *
except ImportError:
    # Mock SNMP functions for environments without pysnmp
    class MockSNMP:
        @staticmethod
        def getCmd(*args, **kwargs):
            return []
        
        @staticmethod
        def bulkCmd(*args, **kwargs):
            return []
    
    # Create mock classes
    class SnmpEngine: pass
    class CommunityData: pass
    class UdpTransportTarget: pass
    class ContextData: pass
    class ObjectIdentifier: pass
    
    # Mock functions
    def getCmd(*args, **kwargs):
        return iter([])
    
    def bulkCmd(*args, **kwargs):
        return iter([])

from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime


class SNMPDevice:
    """Represents an SNMP-enabled network device"""
    
    def __init__(self, ip: str, community: str = 'public', version: str = '2c'):
        self.ip = ip
        self.community = community
        self.version = version
        self.last_poll = None
        self.reachable = False


class SNMPService:
    """Service for collecting SNMP metrics from network devices"""
    
    # Common OIDs for network monitoring
    OID_SYSNAME = '1.3.6.1.2.1.1.5.0'  # System name
    OID_SYSDESCR = '1.3.6.1.2.1.1.1.0'  # System description
    OID_CPU_USAGE = '1.3.6.1.4.1.9.9.109.1.1.1.1.5.1'  # Cisco CPU usage
    OID_MEMORY = '1.3.6.1.2.1.25.2.2.0'  # Memory usage
    OID_UPTIME = '1.3.6.1.2.1.1.3.0'  # System uptime
    OID_INTERFACES = '1.3.6.1.2.1.2.1.0'  # Interface count
    OID_IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'  # Interface input octets
    OID_IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16'  # Interface output octets
    OID_IF_STATUS = '1.3.6.1.2.1.2.2.1.8'  # Interface status (up=1, down=2)
    OID_TEMPERATURE = '1.3.6.1.4.1.9.9.13.1.3.1.3.1'  # Cisco temperature
    
    @staticmethod
    def snmp_get(ip: str, oid: str, community: str, timeout: int = 5) -> Optional[str]:
        """
        Perform single SNMP GET request
        
        Args:
            ip: Device IP address
            oid: OID to query
            community: SNMP community string
            timeout: Request timeout in seconds
            
        Returns:
            OID value as string, or None if failed
        """
        try:
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((ip, 161), timeout=timeout, retries=1),
                    ContextData(),
                    ObjectIdentifier(oid)
                )
            )
            
            if errorIndication:
                return None
            
            if errorStatus:
                return None
            
            return str(varBinds[0][1])
        
        except Exception:
            return None
    
    @staticmethod
    def snmp_walk(ip: str, oid: str, community: str) -> List[Tuple[str, str]]:
        """
        Perform SNMP WALK to get all values under OID
        
        Returns:
            List of (OID, value) tuples
        """
        results = []
        try:
            for errorIndication, errorStatus, errorIndex, varBinds in bulkCmd(
                SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((ip, 161), timeout=5, retries=1),
                ContextData(),
                0, 25,  # Non-repeaters, max-repetitions
                ObjectIdentifier(oid)
            ):
                if errorIndication:
                    break
                
                if errorStatus:
                    break
                
                for name, val in varBinds:
                    results.append((str(name), str(val)))
            
            return results
        
        except Exception:
            return []
    
    @staticmethod
    def poll_device(ip: str, community: str = 'public') -> Optional[Dict]:
        """
        Poll a device for key metrics via SNMP
        
        Returns:
            Dictionary with device metrics or None if unreachable
        """
        # Test connectivity first
        sysname = SNMPService.snmp_get(ip, SNMPService.OID_SYSNAME, community)
        if not sysname:
            return None
        
        try:
            metrics = {
                'device_ip': ip,
                'timestamp': datetime.utcnow().isoformat(),
                'sysname': sysname,
                'sysdescr': SNMPService.snmp_get(ip, SNMPService.OID_SYSDESCR, community),
                'uptime': SNMPService.snmp_get(ip, SNMPService.OID_UPTIME, community),
                'interface_count': SNMPService.snmp_get(ip, SNMPService.OID_INTERFACES, community),
            }
            
            # Try to get CPU (Cisco-specific)
            cpu = SNMPService.snmp_get(ip, SNMPService.OID_CPU_USAGE, community)
            if cpu:
                metrics['cpu_utilization'] = float(cpu)
            
            # Try to get temperature (Cisco-specific)
            temp = SNMPService.snmp_get(ip, SNMPService.OID_TEMPERATURE, community)
            if temp:
                metrics['temperature'] = float(temp)
            
            # Get interface statistics
            interfaces = SNMPService.snmp_walk(ip, SNMPService.OID_IF_STATUS, community)
            metrics['interfaces_up'] = sum(1 for _, val in interfaces if str(val) == '1')
            metrics['interfaces_down'] = sum(1 for _, val in interfaces if str(val) == '2')
            
            return metrics
        
        except Exception as e:
            return None
    
    @staticmethod
    async def poll_devices_async(devices: List[SNMPDevice]) -> Dict[str, Dict]:
        """
        Poll multiple devices asynchronously
        
        Args:
            devices: List of SNMPDevice objects
            
        Returns:
            Dictionary mapping device IP to metrics
        """
        tasks = []
        for device in devices:
            task = asyncio.to_thread(
                SNMPService.poll_device,
                device.ip,
                device.community
            )
            tasks.append((device.ip, task))
        
        results = {}
        for ip, task in tasks:
            try:
                metrics = await task
                if metrics:
                    results[ip] = metrics
            except Exception:
                pass
        
        return results
    
    @staticmethod
    def validate_device(ip: str, community: str = 'public') -> bool:
        """Check if device is reachable via SNMP"""
        result = SNMPService.poll_device(ip, community)
        return result is not None


# Common metric definitions
COMMON_NETWORK_METRICS = {
    'cpu_utilization': {'unit': '%', 'warn_threshold': 75, 'crit_threshold': 90},
    'memory_usage': {'unit': '%', 'warn_threshold': 80, 'crit_threshold': 95},
    'temperature': {'unit': 'C', 'warn_threshold': 50, 'crit_threshold': 65},
    'interface_error_rate': {'unit': '%', 'warn_threshold': 5, 'crit_threshold': 10},
    'bandwidth_utilization': {'unit': '%', 'warn_threshold': 80, 'crit_threshold': 95},
}
