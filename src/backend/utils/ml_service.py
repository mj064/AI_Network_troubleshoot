"""
Machine Learning Module
Anomaly detection, pattern recognition, predictive maintenance
"""

from typing import List, Dict, Tuple
import statistics
from datetime import datetime, timedelta


class AnomalyDetector:
    """Detect anomalies in network metrics using ML techniques"""
    
    @staticmethod
    def isolation_forest_lite(values: List[float], contamination: float = 0.1) -> List[int]:
        """
        Simplified anomaly detection (lightweight alternative to sklearn)
        Detects outliers using isolation scoring
        
        Returns:
            List of indices of anomalous values
        """
        if len(values) < 3:
            return []
        
        anomalies = []
        
        # Method 1: Z-score (standard deviation)
        mean = statistics.mean(values)
        try:
            stdev = statistics.stdev(values)
        except:
            return []
        
        threshold_sigma = 3.0  # 3-sigma rule
        for i, val in enumerate(values):
            if stdev > 0:
                z_score = abs((val - mean) / stdev)
                if z_score > threshold_sigma:
                    anomalies.append(i)
        
        # Method 2: IQR (Interquartile Range)
        if len(values) >= 4:
            sorted_vals = sorted(values)
            q1_idx = len(sorted_vals) // 4
            q3_idx = (3 * len(sorted_vals)) // 4
            
            q1 = sorted_vals[q1_idx]
            q3 = sorted_vals[q3_idx]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for i, val in enumerate(values):
                if val < lower_bound or val > upper_bound:
                    if i not in anomalies:
                        anomalies.append(i)
        
        return sorted(list(set(anomalies)))
    
    @staticmethod
    def seasonal_decomposition(values: List[float], season_length: int = 24) -> Dict:
        """
        Simple seasonal decomposition for time-series data
        
        Returns:
            Dictionary with trend, seasonality, and residual components
        """
        if len(values) < season_length * 2:
            return {
                'trend': values,
                'seasonal': [0] * len(values),
                'residual': [0] * len(values)
            }
        
        # Calculate trend using moving average
        trend = []
        for i in range(len(values)):
            start = max(0, i - season_length // 2)
            end = min(len(values), i + season_length // 2)
            trend.append(statistics.mean(values[start:end]))
        
        # Calculate seasonal component
        seasonal = []
        for i in range(len(values)):
            season_idx = i % season_length
            seasonal_sum = sum(
                values[j] - trend[j]
                for j in range(season_idx, len(values), season_length)
                if j < len(values)
            )
            seasonal_count = (len(values) - season_idx - 1) // season_length + 1
            seasonal_avg = seasonal_sum / seasonal_count if seasonal_count > 0 else 0
            seasonal.append(seasonal_avg)
        
        # Calculate residual
        residual = [
            values[i] - trend[i] - seasonal[i]
            for i in range(len(values))
        ]
        
        return {
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual
        }


class PatternRecognition:
    """Recognize patterns in network behavior"""
    
    @staticmethod
    def identify_patterns(metrics: List[Dict], lookback_days: int = 30) -> List[Dict]:
        """
        Identify recurring patterns in metrics
        
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in metrics:
            name = metric.get('metric_name')
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric)
        
        # Analyze patterns for each metric
        for metric_name, metric_list in metrics_by_name.items():
            values = [m.get('metric_value', 0) for m in metric_list]
            
            # Check for daily pattern
            if len(metric_list) >= 24:
                hourly_avg = PatternRecognition._get_hourly_averages(metric_list)
                variance = statistics.variance(hourly_avg) if len(hourly_avg) > 1 else 0
                
                if variance > statistics.mean(hourly_avg) * 0.1:  # Significant variance
                    patterns.append({
                        'type': 'daily_cycle',
                        'metric': metric_name,
                        'confidence': 0.8,
                        'description': f'{metric_name} shows daily variation pattern'
                    })
            
            # Check for weekly pattern
            if len(metric_list) >= 168:  # One week
                weekly_avg = PatternRecognition._get_day_averages(metric_list)
                variance = statistics.variance(weekly_avg) if len(weekly_avg) > 1 else 0
                
                if variance > statistics.mean(weekly_avg) * 0.15:
                    patterns.append({
                        'type': 'weekly_cycle',
                        'metric': metric_name,
                        'confidence': 0.75,
                        'description': f'{metric_name} shows weekly variation pattern'
                    })
        
        return patterns
    
    @staticmethod
    def _get_hourly_averages(metrics: List[Dict]) -> List[float]:
        """Get average metric value by hour of day"""
        hourly_values = [[] for _ in range(24)]
        
        for metric in metrics:
            try:
                timestamp = datetime.fromisoformat(metric.get('timestamp', '').replace('Z', '+00:00'))
                hour = timestamp.hour
                value = metric.get('metric_value', 0)
                hourly_values[hour].append(value)
            except:
                continue
        
        return [
            statistics.mean(vals) if vals else 0
            for vals in hourly_values
        ]
    
    @staticmethod
    def _get_day_averages(metrics: List[Dict]) -> List[float]:
        """Get average metric value by day of week"""
        day_values = [[] for _ in range(7)]
        
        for metric in metrics:
            try:
                timestamp = datetime.fromisoformat(metric.get('timestamp', '').replace('Z', '+00:00'))
                day = timestamp.weekday()
                value = metric.get('metric_value', 0)
                day_values[day].append(value)
            except:
                continue
        
        return [
            statistics.mean(vals) if vals else 0
            for vals in day_values
        ]
    
    @staticmethod
    def find_similar_incidents(incident: Dict, all_incidents: List[Dict], similarity_threshold: float = 0.7) -> List[Dict]:
        """Find similar past incidents to current one"""
        similar = []
        
        current_keywords = set(incident.get('title', '').lower().split())
        current_devices = set(incident.get('affected_devices', []))
        
        for past_incident in all_incidents:
            if past_incident.get('id') == incident.get('id'):
                continue
            
            past_keywords = set(past_incident.get('title', '').lower().split())
            past_devices = set(past_incident.get('affected_devices', []))
            
            # Calculate similarity
            keyword_similarity = len(current_keywords & past_keywords) / max(len(current_keywords | past_keywords), 1)
            device_similarity = len(current_devices & past_devices) / max(len(current_devices | past_devices), 1)
            
            combined_similarity = (keyword_similarity + device_similarity) / 2
            
            if combined_similarity >= similarity_threshold:
                similar.append({
                    'incident': past_incident,
                    'similarity': round(combined_similarity, 2),
                    'resolution_time': past_incident.get('resolution_time'),
                    'resolution_steps': past_incident.get('resolution_steps')
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)


class PredictiveAnalytics:
    """Predictive maintenance and forecasting"""
    
    @staticmethod
    def predict_device_failure(device: Dict, historical_metrics: List[Dict], warning_days: int = 7) -> Dict:
        """
        Predict if device will fail based on metrics trend
        
        Returns:
            Dictionary with prediction and confidence score
        """
        if not historical_metrics:
            return {'will_fail': False, 'confidence': 0, 'days_to_failure': None}
        
        # Get most recent critical metrics
        critical_metrics = [
            m for m in historical_metrics
            if m.get('status') == 'CRITICAL'
        ]
        
        if not critical_metrics:
            return {'will_fail': False, 'confidence': 0.2, 'days_to_failure': None}
        
        # Analyze trend of critical metrics
        days_with_critical = len(set(
            datetime.fromisoformat(m.get('timestamp', '').replace('Z', '+00:00')).date()
            for m in critical_metrics
        ))
        
        total_days = warning_days
        critical_ratio = days_with_critical / total_days
        
        # If more than 30% of days have critical metrics, predict failure
        will_fail = critical_ratio > 0.3
        confidence = min(critical_ratio, 1.0)
        
        return {
            'will_fail': will_fail,
            'confidence': round(confidence, 2),
            'days_to_failure': warning_days - days_with_critical if will_fail else None,
            'critical_metrics_count': len(critical_metrics),
            'recommendation': 'Schedule maintenance' if will_fail else 'Monitor closely' if confidence > 0.3 else 'All clear'
        }
    
    @staticmethod
    def forecast_capacity(historical_values: List[float], lookforward_days: int = 30) -> Dict:
        """
        Forecast when metrics will exceed capacity/threshold
        
        Returns:
            Forecast data with projected values
        """
        if len(historical_values) < 2:
            return {'forecast': None, 'days_to_threshold': None}
        
        # Simple linear extrapolation
        x_values = list(range(len(historical_values)))
        y_mean = sum(historical_values) / len(historical_values)
        x_mean = sum(x_values) / len(x_values)
        
        numerator = sum((x_values[i] - x_mean) * (historical_values[i] - y_mean) for i in range(len(x_values)))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Project values for next N days
        forecast = []
        for day in range(lookforward_days):
            projected_value = slope * (len(historical_values) + day) + intercept
            forecast.append({
                'day': day + 1,
                'projected_value': round(projected_value, 2)
            })
        
        return {
            'forecast': forecast,
            'trend': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'slope': round(slope, 4)
        }
