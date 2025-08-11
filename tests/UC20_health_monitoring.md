# UC20: System Health Monitoring

## Feature: Real-time Health Monitoring
As a system administrator
I want to monitor system health in real-time
So that I can detect and resolve issues proactively

## Background
Given health monitoring is configured
And metrics are collected continuously

## Scenario 1: Component Health Check
```gherkin
Given system components:
  | Component | Expected Status |
  | API Gateway | healthy |
  | Search Service | healthy |
  | Download Service | healthy |
  | Account Manager | healthy |
  | Cache Service | healthy |
When performing health check
Then return aggregated status
And alert if any component unhealthy
```

## Scenario 2: Performance Metrics
```gherkin
Given performance thresholds:
  | Metric | Warning | Critical |
  | Response Time | >2s | >5s |
  | Error Rate | >1% | >5% |
  | CPU Usage | >70% | >90% |
  | Memory Usage | >80% | >95% |
When metrics exceed thresholds
Then trigger appropriate alerts
And log to monitoring system
```

## Scenario 3: Auto-Recovery
```gherkin
Given a service becomes unhealthy
When detected by health monitor
Then:
  - Attempt automatic restart
  - If restart fails, try fallback
  - If fallback fails, alert admin
  - Log all recovery attempts
```

## Implementation Requirements

### 1. Health Check Endpoints
```python
class HealthCheck:
    async def check_api(self) -> Dict:
        return {
            'status': 'healthy',
            'latency': 45,
            'version': '1.0.0'
        }
    
    async def check_database(self) -> Dict:
        return {
            'status': 'healthy',
            'connections': 5,
            'pool_size': 10
        }
```

### 2. Metrics Collection
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'errors_total': 0,
            'response_time_ms': [],
            'active_connections': 0
        }
```

### 3. Alert System
```python
class AlertManager:
    def check_thresholds(self, metrics):
        alerts = []
        if metrics['error_rate'] > 0.05:
            alerts.append(Alert('CRITICAL', 'High error rate'))
        return alerts
```

## Success Criteria
- ✅ All components monitored
- ✅ Metrics updated every 10s
- ✅ Alerts triggered <30s
- ✅ Auto-recovery success >80%
- ✅ Dashboard shows real-time status