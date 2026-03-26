"""
AI Analysis Service for Network Incidents
Provides intelligent analysis, root cause detection, and remediation recommendations
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Tuple


class AIIncidentAnalyzer:
    """AI-powered incident analysis and remediation recommendation engine"""
    
    # Pattern mapping for common network issues
    ISSUE_PATTERNS = {
        'high_cpu': {
            'keywords': ['cpu', 'processor', 'utilization', 'load'],
            'themes': ['performance degradation', 'slow response', 'latency increase'],
            'probable_causes': [
                'Running processes consuming excessive CPU',
                'Malware or unauthorized processes',
                'Misconfigured application with infinite loops',
                'Insufficient hardware resources',
                'Thermal throttling due to overheating'
            ],
            'remediation': [
                'Identify CPU-consuming processes using top/taskmgr',
                'Kill unnecessary processes or restart services',
                'Check for malware using antivirus/EDR tools',
                'Review recent software deployments',
                'Monitor CPU temperature and improve cooling',
                'Scale up resources if consistently high',
                'Implement CPU limits/quotas for applications'
            ]
        },
        'high_memory': {
            'keywords': ['memory', 'ram', 'heap', 'buffer', 'swap'],
            'themes': ['out of memory', 'oom', 'memory leak'],
            'probable_causes': [
                'Memory leak in application code',
                'Insufficient system RAM',
                'Too many concurrent connections',
                'Cache not being evicted properly',
                'Buffer bloat in network stack'
            ],
            'remediation': [
                'Check memory usage per process',
                'Identify memory leak using profiling tools',
                'Restart application to free memory',
                'Increase available RAM or optimize application',
                'Configure memory limits and monitoring',
                'Implement garbage collection tuning',
                'Clear caches and restart services'
            ]
        },
        'network_connectivity': {
            'keywords': ['connection', 'unreachable', 'timeout', 'network', 'offline', 'down'],
            'themes': ['no connectivity', 'cannot reach', 'disconnected', 'network down'],
            'probable_causes': [
                'Network interface down or disabled',
                'Routing issue or incorrect route',
                'Firewall blocking traffic',
                'Physical cable disconnected',
                'DNS resolution failure',
                'Gateway or router failure',
                'IP address conflict'
            ],
            'remediation': [
                'Check physical cable connections',
                'Verify network interface status (ifconfig/ipconfig)',
                'Review routing table and default gateway',
                'Check firewall rules and security policies',
                'Test DNS resolution (nslookup/dig)',
                'Ping gateway and upstream routers',
                'Check ARP table for IP conflicts',
                'Restart network services'
            ]
        },
        'disk_space': {
            'keywords': ['disk', 'space', 'storage', 'full', 'capacity', 'inode'],
            'themes': ['disk full', 'no space left', 'storage exhausted'],
            'probable_causes': [
                'Application generating large log files',
                'Temporary files not being cleaned',
                'Old backups not deleted',
                'Database growth exceed capacity',
                'Large core dumps or crash files',
                'Inode exhaustion from many small files'
            ],
            'remediation': [
                'Identify large files: du -sh /* or dir /S',
                'Clear old log files and archives',
                'Remove temporary/cache files',
                'Compress old data or migrate to archive',
                'Implement log rotation (logrotate)',
                'Enable cleanup scripts or cron jobs',
                'Expand storage capacity',
                'Monitor disk usage trends'
            ]
        },
        'database_issue': {
            'keywords': ['database', 'db', 'sql', 'query', 'connection pool', 'deadlock'],
            'themes': ['database slow', 'query timeout', 'connection refused'],
            'probable_causes': [
                'Slow or long-running queries',
                'Missing database indexes',
                'Connection pool exhaustion',
                'Database deadlock',
                'Corrupted database files',
                'Insufficient database resources',
                'Replication lag'
            ],
            'remediation': [
                'Review slow query logs',
                'Identify missing indexes using EXPLAIN',
                'Optimize query performance',
                'Increase connection pool size',
                'Run database consistency checks (DBCC/CHECK)',
                'Kill long-running transactions',
                'Restart database service if hung',
                'Monitor replication status and lag'
            ]
        },
        'authentication': {
            'keywords': ['auth', 'login', 'permission', 'access denied', 'unauthorized', 'mfa', 'certificate'],
            'themes': ['cannot login', 'permission denied', 'access failure'],
            'probable_causes': [
                'Expired credentials or password',
                'Incorrect permissions or ACLs',
                'Expired SSL certificate',
                'MFA/2FA synchronization issue',
                'User account locked or disabled',
                'Wrong encryption algorithm',
                'Token expiration'
            ],
            'remediation': [
                'Verify user credentials and password expiry',
                'Check user account status (locked/disabled)',
                'Review file/directory permissions',
                'Check certificate validity and renewal dates',
                'Resynchronize MFA devices',
                'Verify encryption/TLS versions',
                'Check token refresh mechanisms',
                'Clear cached credentials'
            ]
        },
        'latency': {
            'keywords': ['latency', 'slow', 'response time', 'lag', 'delay', 'timeout'],
            'themes': ['high latency', 'slow response', 'performance degradation'],
            'probable_causes': [
                'Network congestion or packet loss',
                'Slow DNS resolution',
                'Application processing delay',
                'Database query slow',
                'Inefficient algorithm or code',
                'Disk I/O bottleneck',
                'Misconfigured timeout values'
            ],
            'remediation': [
                'Check network latency: ping, traceroute',
                'Monitor packet loss and jitter',
                'Profile application with APM tools',
                'Cache frequently accessed data',
                'Optimize database queries',
                'Increase cache size and TTL',
                'Use CDN for content delivery',
                'Adjust timeout configurations'
            ]
        },
        'service_restart': {
            'keywords': ['restart', 'crashed', 'died', 'respawn', 'reboot'],
            'themes': ['service constantly restarting', 'keeps crashing'],
            'probable_causes': [
                'Application has fatal error',
                'Out of memory causing crash',
                'Missing configuration or files',
                'Corrupted application binary',
                'Incompatible library version',
                'Segmentation fault or core dump',
                'Health check misconfigured'
            ],
            'remediation': [
                'Review application logs and error messages',
                'Check available memory and resources',
                'Verify all required files are present',
                'Validate configuration files',
                'Check for corrupted binaries/libraries',
                'Review system event logs for errors',
                'Enable core dumps for debugging',
                'Update to compatible versions',
                'Increase process restart delay'
            ]
        }
    }
    
    SEVERITY_IMPACT = {
        'P1': {
            'business_impact': 'Critical - Complete service outage',
            'response_time': '15 minutes',
            'sla': '99.99% uptime',
            'urgency': 'IMMEDIATE'
        },
        'P2': {
            'business_impact': 'Major - Significant functionality impaired',
            'response_time': '1 hour',
            'sla': '99.9% uptime',
            'urgency': 'HIGH'
        },
        'P3': {
            'business_impact': 'Minor - Limited functionality affected',
            'response_time': '4 hours',
            'sla': '99.5% uptime',
            'urgency': 'MEDIUM'
        },
        'P4': {
            'business_impact': 'Low - Minimal impact or workaround available',
            'response_time': '1 business day',
            'sla': '95% uptime',
            'urgency': 'LOW'
        }
    }
    
    def __init__(self):
        """Initialize the AI analyzer"""
        self.analysis_cache = {}
    
    def analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an incident and provide intelligent recommendations
        
        Args:
            incident: Incident data including title, description, severity, etc.
            
        Returns:
            Analysis with root causes, recommendations, and remediation steps
        """
        ticket_id = incident.get('ticket_id', 'UNKNOWN')
        
        # Combine all text for analysis
        text_to_analyze = f"{incident.get('title', '')} {incident.get('description', '')} {incident.get('symptom_summary', '')}".lower()
        
        # Detect issue patterns
        detected_issues = self._detect_issues(text_to_analyze)
        
        # Get severity details
        severity = incident.get('severity', 'P4')
        severity_info = self.SEVERITY_IMPACT.get(severity, self.SEVERITY_IMPACT['P4'])
        
        # Analyze related data
        affected_devices = incident.get('devices', [])
        alerts_triggered = incident.get('alerts_triggered', [])
        metrics = incident.get('metrics', [])
        
        # Calculate confidence score
        confidence = self._calculate_confidence(detected_issues, alerts_triggered, metrics)
        
        # Generate analysis
        analysis = {
            'ticket_id': ticket_id,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'severity': severity,
            'severity_details': severity_info,
            'detected_issues': detected_issues,
            'root_cause_analysis': self._generate_root_cause_analysis(
                detected_issues, 
                incident, 
                affected_devices, 
                alerts_triggered
            ),
            'recommended_actions': self._generate_recommended_actions(
                detected_issues, 
                severity,
                affected_devices
            ),
            'remediation_steps': self._generate_remediation_steps(detected_issues),
            'affected_devices': [d.get('device_name', d) for d in affected_devices] if affected_devices else [],
            'alerts_summary': self._summarize_alerts(alerts_triggered),
            'estimated_resolution_time': self._estimate_resolution_time(severity, detected_issues),
            'escalation_needed': self._check_escalation(severity, detected_issues),
            'prevention_measures': self._get_prevention_measures(detected_issues),
            'confidence_score': confidence,
            'additional_context': self._get_additional_context(incident)
        }
        
        return analysis
    
    def _detect_issues(self, text: str) -> List[Dict[str, Any]]:
        """Detect issue patterns from incident text"""
        detected = []
        
        for issue_type, pattern_data in self.ISSUE_PATTERNS.items():
            keywords = pattern_data['keywords']
            themes = pattern_data['themes']
            
            # Check if keywords are mentioned
            keyword_matches = sum(1 for kw in keywords if kw in text)
            theme_matches = sum(1 for theme in themes if theme in text)
            
            match_score = keyword_matches + (theme_matches * 2)
            
            if match_score > 0:
                detected.append({
                    'issue_type': issue_type,
                    'match_score': match_score,
                    'probability': min(100, (match_score * 25)),  # Out of 100
                    'probable_causes': pattern_data['probable_causes'],
                    'remediation_tips': pattern_data['remediation']
                })
        
        # Sort by probability
        return sorted(detected, key=lambda x: x['match_score'], reverse=True)
    
    def _generate_root_cause_analysis(self, issues: List, incident: Dict, devices: List, alerts: List) -> Dict:
        """Generate root cause analysis"""
        if not issues:
            return {
                'primary_cause': 'Undetermined - insufficient data for analysis',
                'contributing_factors': ['Limited incident information', 'No clear error patterns detected'],
                'confidence': 'Low'
            }
        
        primary_issue = issues[0]
        
        analysis = {
            'primary_cause': self._explain_issue(primary_issue['issue_type']),
            'probability': f"{primary_issue['probability']:.0f}%",
            'contributing_factors': [
                f"Alert triggered: {primary_issue['issue_type']}",
            ],
            'affected_component': self._determine_component(primary_issue['issue_type']),
            'confidence': 'High' if primary_issue['probability'] > 70 else 'Medium' if primary_issue['probability'] > 40 else 'Low'
        }
        
        # Add secondary issues
        if len(issues) > 1:
            analysis['secondary_causes'] = [
                self._explain_issue(issue['issue_type']) for issue in issues[1:3]
            ]
        
        return analysis
    
    def _explain_issue(self, issue_type: str) -> str:
        """Get human-readable explanation for issue type"""
        explanations = {
            'high_cpu': 'High CPU utilization detected - processes consuming excessive computational resources',
            'high_memory': 'Memory exhaustion or leak - RAM usage exceeds safe thresholds',
            'network_connectivity': 'Network connectivity issue - unable to establish or maintain connections',
            'disk_space': 'Disk space exhaustion - storage capacity critical or full',
            'database_issue': 'Database performance degradation - queries slow or connections blocked',
            'authentication': 'Authentication or authorization failure - access control issue',
            'latency': 'High latency detected - response times exceed acceptable thresholds',
            'service_restart': 'Service instability - application repeatedly crashing or restarting'
        }
        return explanations.get(issue_type, f'Issue detected: {issue_type}')
    
    def _determine_component(self, issue_type: str) -> str:
        """Determine affected component"""
        component_map = {
            'high_cpu': 'CPU/Processor',
            'high_memory': 'Memory/RAM',
            'network_connectivity': 'Network Interface',
            'disk_space': 'Storage/Disk',
            'database_issue': 'Database Service',
            'authentication': 'Authentication Service',
            'latency': 'Network/Application',
            'service_restart': 'Application Service'
        }
        return component_map.get(issue_type, 'Unknown Component')
    
    def _generate_recommended_actions(self, issues: List, severity: str, devices: List) -> List[str]:
        """Generate immediate recommended actions"""
        actions = []
        
        if severity == 'P1':
            actions.append('🚨 IMMEDIATE: Page on-call team')
            actions.append('🚨 IMMEDIATE: Start incident command post')
            actions.append('🚨 IMMEDIATE: Begin customer communication')
        
        if issues:
            primary_issue = issues[0]['issue_type']
            
            if primary_issue == 'high_cpu':
                actions.extend([
                    'Check top processes and identify CPU consumers',
                    'Monitor CPU temperature and thermal status',
                    'Consider graceful restart if safe'
                ])
            elif primary_issue == 'high_memory':
                actions.extend([
                    'Review memory utilization by process',
                    'Check for memory leak patterns',
                    'Restart services if memory not released'
                ])
            elif primary_issue == 'network_connectivity':
                actions.extend([
                    'Verify physical connections and interfaces',
                    'Check routing and gateway configuration',
                    'Restart network services'
                ])
            elif primary_issue == 'disk_space':
                actions.extend([
                    'Identify largest files and directories',
                    'Clear temporary and log files',
                    'Schedule cleanup jobs'
                ])
            elif primary_issue == 'database_issue':
                actions.extend([
                    'Check database service status',
                    'Review slow query logs',
                    'Monitor connection pool',
                    'Consider graceful restart if hung'
                ])
        
        if devices:
            actions.append(f'Isolate affected devices: {", ".join(str(d) for d in devices[:3])}')
        
        return actions[:6]  # Return top 6 actions
    
    def _generate_remediation_steps(self, issues: List) -> List[str]:
        """Generate detailed remediation steps"""
        steps = []
        
        for issue in issues[:2]:  # Focus on top 2 issues
            remediation = issue.get('remediation_tips', [])
            steps.extend(remediation[:3])
        
        return steps
    
    def _summarize_alerts(self, alerts: List) -> Dict:
        """Summarize triggered alerts"""
        if not alerts:
            return {'count': 0, 'summary': 'No alerts triggered'}
        
        alert_types = {}
        for alert in alerts:
            if isinstance(alert, dict):
                alert_type = alert.get('type', 'unknown')
            else:
                alert_type = str(alert)
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        return {
            'count': len(alerts),
            'types': alert_types,
            'summary': f"{len(alerts)} alert(s) triggered: {', '.join(alert_types.keys())}"
        }
    
    def _estimate_resolution_time(self, severity: str, issues: List) -> str:
        """Estimate time to resolution"""
        base_time = {
            'P1': '15-30 minutes',
            'P2': '30 minutes - 2 hours',
            'P3': '2-4 hours',
            'P4': '1-3 days'
        }
        
        estimate = base_time.get(severity, '1-3 days')
        
        if issues and issues[0]['issue_type'] == 'network_connectivity':
            estimate += ' (may be quicker if simple cable issue)'
        
        return estimate
    
    def _check_escalation(self, severity: str, issues: List) -> Dict:
        """Check if escalation is needed"""
        needs_escalation = severity in ['P1', 'P2']
        
        escalation_teams = []
        if severity in ['P1', 'P2']:
            escalation_teams.append('Infrastructure Team')
        if issues and any(i['issue_type'] == 'database_issue' for i in issues):
            escalation_teams.append('Database Team')
        if issues and any(i['issue_type'] == 'authentication' for i in issues):
            escalation_teams.append('Security Team')
        
        return {
            'needed': needs_escalation,
            'teams': escalation_teams,
            'urgency': self.SEVERITY_IMPACT.get(severity, {}).get('urgency', 'LOW')
        }
    
    def _get_prevention_measures(self, issues: List) -> List[str]:
        """Get prevention measures for future"""
        measures = [
            'Implement comprehensive monitoring and alerting',
            'Setup automated remediation for common issues',
            'Conduct regular capacity planning'
        ]
        
        if issues:
            primary = issues[0]['issue_type']
            if primary in ['high_cpu', 'high_memory']:
                measures.append('Implement resource limits and quotas')
                measures.append('Setup auto-scaling policies')
            elif primary == 'disk_space':
                measures.append('Configure automatic log rotation')
                measures.append('Setup disk space alerts before critical')
            elif primary == 'database_issue':
                measures.append('Implement database query analysis and optimization')
                measures.append('Setup connection pool tuning')
        
        return measures
    
    def _get_additional_context(self, incident: Dict) -> Dict:
        """Get additional context about the incident"""
        context = {
            'incident_age_hours': self._calculate_incident_age(incident.get('created_at')),
            'is_recurring': self._check_if_recurring(incident),
            'knowledge_base_articles': self._get_kb_articles(incident)
        }
        return context
    
    def _calculate_incident_age(self, created_at: str) -> float:
        """Calculate incident age in hours"""
        if not created_at:
            return 0
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = (datetime.utcnow() - created).total_seconds() / 3600
            return round(age, 1)
        except:
            return 0
    
    def _check_if_recurring(self, incident: Dict) -> bool:
        """Check if this is a recurring issue"""
        related = incident.get('related_tickets', [])
        return len(related) > 2 if related else False
    
    def _get_kb_articles(self, incident: Dict) -> List[str]:
        """Get relevant knowledge base articles"""
        # In a real system, this would search a KB
        return [
            'Best Practices for CPU Monitoring',
            'Network Troubleshooting Guide',
            'Database Performance Tuning'
        ]
    
    def _calculate_confidence(self, issues: List, alerts: List, metrics: List) -> float:
        """Calculate overall confidence score"""
        confidence = 50.0
        
        if issues:
            confidence += issues[0].get('probability', 0) * 0.3
        
        if alerts:
            confidence += min(30, len(alerts) * 5)
        
        if metrics:
            confidence += min(20, len(metrics) * 2)
        
        return min(100, confidence)
