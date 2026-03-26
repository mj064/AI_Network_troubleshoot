"""
Advanced Analytics Module
Trending, baselines, anomaly detection, and predictive analytics
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict


class AnalyticsService:
    """Service for network analytics and insights"""
    
    @staticmethod
    def calculate_trend(values: List[float], metric_name: str = '') -> Dict:
        """
        Calculate trend from metric values
        
        Returns:
            Dictionary with trend direction and slope
        """
        if len(values) < 2:
            return {'trend': 'stable', 'slope': 0, 'direction': 'none'}
        
        # Simple linear regression
        n = len(values)
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': round(slope, 4),
            'direction': 'up' if slope > 0 else 'down' if slope < 0 else 'stable'
        }
    
    @staticmethod
    def detect_anomalies(values: List[float], threshold_sigma: float = 2.0) -> List[int]:
        """
        Detect anomalous values using standard deviation
        
        Returns:
            List of indices of anomalous values
        """
        if len(values) < 3:
            return []
        
        mean = statistics.mean(values)
        try:
            stdev = statistics.stdev(values)
        except:
            return []
        
        if stdev == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold_sigma:
                anomalies.append(i)
        
        return anomalies
    
    @staticmethod
    def predict_failure(values: List[float], threshold: float, lookback_days: int = 7) -> Dict:
        """
        Predict if metric will exceed threshold based on trend
        
        Returns:
            Dictionary with prediction and estimated time
        """
        if len(values) < 2:
            return {'predicted_failure': False, 'days_until_threshold': None}
        
        trend_info = AnalyticsService.calculate_trend(values)
        current_value = values[-1]
        slope = trend_info['slope']
        
        if slope <= 0:
            return {'predicted_failure': False, 'days_until_threshold': None}
        
        # Estimate days until threshold
        if slope == 0:
            return {'predicted_failure': False, 'days_until_threshold': None}
        
        days_to_threshold = (threshold - current_value) / slope
        
        if days_to_threshold > 0 and days_to_threshold <= lookback_days:
            return {
                'predicted_failure': True,
                'days_until_threshold': round(days_to_threshold, 1),
                'confidence': 'moderate'
            }
        
        return {'predicted_failure': False, 'days_until_threshold': round(days_to_threshold, 1) if days_to_threshold > 0 else None}
    
    @staticmethod
    def calculate_baseline(historical_values: List[float], period_hours: int = 24) -> Dict:
        """Calculate baseline (normal range) for a metric"""
        if not historical_values:
            return {'baseline_min': 0, 'baseline_max': 100, 'baseline_mean': 50}
        
        return {
            'baseline_min': min(historical_values),
            'baseline_max': max(historical_values),
            'baseline_mean': round(statistics.mean(historical_values), 2),
            'baseline_stdev': round(statistics.stdev(historical_values), 2) if len(historical_values) > 1 else 0,
            'period_hours': period_hours
        }
    
    @staticmethod
    def detect_deviation(current_value: float, baseline: Dict, threshold_stdev: float = 2.0) -> Dict:
        """Detect if current value deviates from baseline"""
        baseline_mean = baseline.get('baseline_mean', 50)
        baseline_stdev = baseline.get('baseline_stdev', 1)
        
        if baseline_stdev == 0:
            deviation_percent = 0
        else:
            deviation_percent = abs((current_value - baseline_mean) / baseline_stdev) * 100
        
        is_anomaly = deviation_percent > (threshold_stdev * 100)
        
        return {
            'is_anomaly': is_anomaly,
            'deviation_percent': round(deviation_percent, 1),
            'baseline_mean': baseline_mean,
            'current_value': current_value
        }
    
    @staticmethod
    def identify_correlated_metrics(metrics_data: Dict[str, List[float]]) -> List[Tuple[str, str, float]]:
        """
        Identify correlated metrics
        
        Returns:
            List of (metric1, metric2, correlation) tuples
        """
        correlations = []
        metric_names = list(metrics_data.keys())
        
        for i, metric1 in enumerate(metric_names):
            for metric2 in metric_names[i+1:]:
                correlation = AnalyticsService._calculate_correlation(
                    metrics_data[metric1],
                    metrics_data[metric2]
                )
                
                if abs(correlation) > 0.7:  # Strong correlation threshold
                    correlations.append((metric1, metric2, round(correlation, 3)))
        
        return sorted(correlations, key=lambda x: abs(x[2]), reverse=True)
    
    @staticmethod
    def _calculate_correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            mean_x = sum(x) / len(x)
            mean_y = sum(y) / len(y)
            
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            denominator = (
                sum((x[i] - mean_x) ** 2 for i in range(len(x))) *
                sum((y[i] - mean_y) ** 2 for i in range(len(y)))
            ) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        except:
            return 0.0
    
    @staticmethod
    def generate_health_score(metrics_status: Dict[str, str]) -> float:
        """
        Generate overall health score from metric statuses
        
        Args:
            metrics_status: Dictionary mapping metric names to status (OK/WARNING/CRITICAL)
            
        Returns:
            Health score 0-100
        """
        if not metrics_status:
            return 100.0
        
        total_metrics = len(metrics_status)
        
        critical_count = sum(1 for status in metrics_status.values() if status == 'CRITICAL')
        warning_count = sum(1 for status in metrics_status.values() if status == 'WARNING')
        
        # Scoring: Each critical = -20 points, each warning = -5 points
        score = 100.0
        score -= critical_count * 20
        score -= warning_count * 5
        
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def identify_top_issues(metrics: List[Dict], limit: int = 10) -> List[Dict]:
        """Identify top problem metrics"""
        # Sort by severity and value
        problem_metrics = [
            m for m in metrics 
            if m.get('status') in ['WARNING', 'CRITICAL']
        ]
        
        problem_metrics.sort(key=lambda x: (
            1 if x.get('status') == 'CRITICAL' else 2,
            -(x.get('metric_value', 0))
        ))
        
        return problem_metrics[:limit]
    
    @staticmethod
    def calculate_mttr(incidents: List[Dict]) -> Dict:
        """Calculate Mean Time To Recover"""
        if not incidents:
            return {'mttr_hours': 0, 'mttr_minutes': 0, 'sample_size': 0}
        
        resolved_incidents = [
            i for i in incidents 
            if i.get('status') == 'RESOLVED' and i.get('resolved_at')
        ]
        
        if not resolved_incidents:
            return {'mttr_hours': 0, 'mttr_minutes': 0, 'sample_size': 0}
        
        durations = []
        for incident in resolved_incidents:
            try:
                # Parse timestamps
                created = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))
                resolved = datetime.fromisoformat(incident['resolved_at'].replace('Z', '+00:00'))
                duration = (resolved - created).total_seconds() / 3600  # Convert to hours
                durations.append(duration)
            except:
                continue
        
        if durations:
            mttr_hours = statistics.mean(durations)
            return {
                'mttr_hours': round(mttr_hours, 2),
                'mttr_minutes': round(mttr_hours * 60, 0),
                'sample_size': len(durations)
            }
        
        return {'mttr_hours': 0, 'mttr_minutes': 0, 'sample_size': 0}
    
    @staticmethod
    def calculate_availability(incidents: List[Dict], total_device_hours: float) -> Dict:
        """Calculate service availability percentage"""
        if not incidents:
            return {
                'availability_percent': 100.0,
                'downtime_hours': 0,
                'uptime_hours': total_device_hours
            }
        
        total_downtime = 0
        for incident in incidents:
            try:
                created = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))
                resolved = datetime.fromisoformat(incident['resolved_at'].replace('Z', '+00:00')) if incident.get('resolved_at') else datetime.utcnow()
                duration = (resolved - created).total_seconds() / 3600
                total_downtime += duration
            except:
                continue
        
        uptime_hours = total_device_hours - total_downtime
        availability = (uptime_hours / total_device_hours * 100) if total_device_hours > 0 else 100
        
        return {
            'availability_percent': round(availability, 2),
            'downtime_hours': round(total_downtime, 2),
            'uptime_hours': round(uptime_hours, 2)
        }
