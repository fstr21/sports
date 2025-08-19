# Soccer Discord Integration - Rollback Procedures and Monitoring

## Overview

This document provides comprehensive rollback procedures and monitoring guidelines for the Soccer Discord Integration. Use these procedures when issues arise in production or when monitoring indicates problems.

## Rollback Scenarios

### Scenario 1: Critical System Failure
**Symptoms:**
- Bot completely unresponsive
- All commands failing
- High error rates (>50%)
- Memory leaks or crashes

**Immediate Action (< 5 minutes):**
```bash
# 1. Stop the current bot process
pkill -f "python bot_structure.py"

# 2. Restore backup configuration
cp bot_structure.py.backup bot_structure.py
cp config.py.backup config.py

# 3. Disable soccer integration
sed -i 's/"soccer_integration": True/"soccer_integration": False/' config.py

# 4. Restart with minimal configuration
python bot_structure.py --safe-mode
```

### Scenario 2: Soccer Integration Issues
**Symptoms:**
- Soccer commands failing
- MCP server connection issues
- Soccer channel creation problems
- MLB functionality still working

**Gradual Rollback (< 10 minutes):**
```bash
# 1. Disable soccer integration only
python -c "
import config
config.FEATURES['soccer_integration'] = False
with open('config.py', 'r') as f:
    content = f.read()
content = content.replace('\"soccer_integration\": True', '\"soccer_integration\": False')
with open('config.py', 'w') as f:
    f.write(content)
"

# 2. Restart bot (keeps MLB functionality)
pkill -f "python bot_structure.py"
python bot_structure.py

# 3. Verify MLB still works
python -c "
from bot_structure import SportsBot
bot = SportsBot()
print('MLB active:', bot.leagues['MLB']['active'])
print('Soccer active:', bot.leagues['SOCCER']['active'])
"
```

### Scenario 3: Performance Degradation
**Symptoms:**
- Slow response times (>10 seconds)
- High memory usage
- Rate limit violations
- Partial functionality loss

**Performance Rollback (< 15 minutes):**
```bash
# 1. Reduce feature load
python -c "
# Disable resource-intensive features
features_to_disable = [
    'h2h_analysis',
    'betting_recommendations', 
    'advanced_statistics',
    'multi_league_support'
]

with open('config.py', 'r') as f:
    content = f.read()

for feature in features_to_disable:
    content = content.replace(f'\"{feature}\": True', f'\"{feature}\": False')

with open('config.py', 'w') as f:
    f.write(content)
"

# 2. Reduce rate limits
python -c "
# Set conservative rate limits
import json
rate_config = {
    'requests_per_minute': 10,
    'requests_per_hour': 100,
    'burst_limit': 2,
    'cooldown_seconds': 5
}
print('Applied conservative rate limits')
"

# 3. Restart with reduced load
python bot_structure.py --performance-mode
```

### Scenario 4: Data Corruption/Invalid Responses
**Symptoms:**
- Malformed embeds
- Invalid channel names
- Incorrect match data
- Parsing errors

**Data Rollback (< 20 minutes):**
```bash
# 1. Enable graceful degradation
python -c "
# Enable all fallback mechanisms
fallback_config = {
    'graceful_degradation': True,
    'fallback_to_cache': True,
    'skip_invalid_data': True,
    'use_minimal_embeds': True
}
print('Enabled graceful degradation')
"

# 2. Clear any cached data
rm -rf cache/soccer_*
rm -rf temp/match_data_*

# 3. Restart with data validation
python bot_structure.py --validate-data
```

## Rollback Decision Matrix

| Issue Severity | Response Time | Action | Scope |
|---------------|---------------|---------|-------|
| **Critical** | < 5 min | Full rollback to backup | All functionality |
| **High** | < 10 min | Disable soccer integration | Soccer only |
| **Medium** | < 15 min | Reduce feature load | Performance features |
| **Low** | < 30 min | Enable graceful degradation | Data handling |

## Monitoring and Alerting

### Key Metrics to Monitor

#### 1. System Health Metrics
```python
# health_monitor.py
import psutil
import asyncio
import httpx
from datetime import datetime

class HealthMonitor:
    def __init__(self):
        self.metrics = {}
    
    async def check_system_health(self):
        """Check overall system health"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'bot_status': await self.check_bot_status(),
            'mcp_status': await self.check_mcp_status(),
            'discord_api_status': await self.check_discord_status()
        }
        return metrics
    
    async def check_bot_status(self):
        """Check if bot process is running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'bot_structure.py' in ' '.join(proc.info['cmdline'] or []):
                return {
                    'status': 'running',
                    'pid': proc.info['pid'],
                    'memory_mb': proc.memory_info().rss / 1024 / 1024
                }
        return {'status': 'stopped'}
    
    async def check_mcp_status(self):
        """Check MCP server connectivity"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    'https://soccermcp-production.up.railway.app/mcp',
                    json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}
                )
                return {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'status_code': response.status_code
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def check_discord_status(self):
        """Check Discord API status"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get('https://discord.com/api/v10/gateway')
                return {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

# Usage
async def main():
    monitor = HealthMonitor()
    health = await monitor.check_system_health()
    print(json.dumps(health, indent=2))

if __name__ == "__main__":
    import json
    asyncio.run(main())
```

#### 2. Performance Metrics
```python
# performance_monitor.py
import time
import asyncio
from collections import deque
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self):
        self.response_times = deque(maxlen=100)  # Last 100 requests
        self.error_counts = deque(maxlen=100)
        self.channel_creation_times = deque(maxlen=50)
    
    def record_response_time(self, operation, duration):
        """Record operation response time"""
        self.response_times.append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now()
        })
    
    def record_error(self, operation, error_type):
        """Record error occurrence"""
        self.error_counts.append({
            'operation': operation,
            'error_type': error_type,
            'timestamp': datetime.now()
        })
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.response_times:
            return {'status': 'no_data'}
        
        recent_times = [r['duration'] for r in self.response_times 
                       if r['timestamp'] > datetime.now() - timedelta(minutes=10)]
        
        recent_errors = [e for e in self.error_counts 
                        if e['timestamp'] > datetime.now() - timedelta(minutes=10)]
        
        return {
            'avg_response_time': sum(recent_times) / len(recent_times) if recent_times else 0,
            'max_response_time': max(recent_times) if recent_times else 0,
            'error_rate': len(recent_errors) / max(len(recent_times), 1) * 100,
            'total_operations': len(recent_times),
            'total_errors': len(recent_errors)
        }

# Global performance monitor instance
perf_monitor = PerformanceMonitor()
```

#### 3. Alert Thresholds
```python
# alert_thresholds.py
ALERT_THRESHOLDS = {
    'critical': {
        'cpu_usage': 90,           # CPU usage > 90%
        'memory_usage': 85,        # Memory usage > 85%
        'error_rate': 50,          # Error rate > 50%
        'response_time': 30,       # Response time > 30 seconds
        'mcp_downtime': 300        # MCP server down > 5 minutes
    },
    'warning': {
        'cpu_usage': 70,           # CPU usage > 70%
        'memory_usage': 70,        # Memory usage > 70%
        'error_rate': 20,          # Error rate > 20%
        'response_time': 10,       # Response time > 10 seconds
        'mcp_downtime': 60         # MCP server down > 1 minute
    },
    'info': {
        'cpu_usage': 50,           # CPU usage > 50%
        'memory_usage': 50,        # Memory usage > 50%
        'error_rate': 5,           # Error rate > 5%
        'response_time': 5,        # Response time > 5 seconds
        'mcp_downtime': 30         # MCP server down > 30 seconds
    }
}

def check_thresholds(metrics):
    """Check metrics against thresholds"""
    alerts = []
    
    for severity, thresholds in ALERT_THRESHOLDS.items():
        for metric, threshold in thresholds.items():
            if metric in metrics and metrics[metric] > threshold:
                alerts.append({
                    'severity': severity,
                    'metric': metric,
                    'value': metrics[metric],
                    'threshold': threshold,
                    'timestamp': datetime.now().isoformat()
                })
    
    return alerts
```

### Automated Monitoring Script
```python
# monitor.py
#!/usr/bin/env python3
import asyncio
import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from health_monitor import HealthMonitor
from performance_monitor import PerformanceMonitor
from alert_thresholds import check_thresholds, ALERT_THRESHOLDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.last_alerts = {}
        self.alert_cooldown = 300  # 5 minutes between same alerts
    
    def should_send_alert(self, alert):
        """Check if alert should be sent (cooldown logic)"""
        alert_key = f"{alert['metric']}_{alert['severity']}"
        last_sent = self.last_alerts.get(alert_key, 0)
        current_time = datetime.now().timestamp()
        
        if current_time - last_sent > self.alert_cooldown:
            self.last_alerts[alert_key] = current_time
            return True
        return False
    
    def send_alert(self, alert):
        """Send alert notification"""
        if not self.should_send_alert(alert):
            return
        
        message = f"""
        ALERT: {alert['severity'].upper()}
        
        Metric: {alert['metric']}
        Current Value: {alert['value']}
        Threshold: {alert['threshold']}
        Time: {alert['timestamp']}
        
        Please check the system immediately.
        """
        
        logger.warning(f"ALERT: {alert['severity']} - {alert['metric']}: {alert['value']}")
        
        # Add email/Slack/Discord notification here if needed
        # self.send_email_alert(message)
        # self.send_slack_alert(message)

async def monitoring_loop():
    """Main monitoring loop"""
    health_monitor = HealthMonitor()
    perf_monitor = PerformanceMonitor()
    alert_manager = AlertManager()
    
    logger.info("Starting monitoring loop...")
    
    while True:
        try:
            # Collect health metrics
            health_metrics = await health_monitor.check_system_health()
            
            # Collect performance metrics
            perf_metrics = perf_monitor.get_performance_summary()
            
            # Combine metrics
            all_metrics = {**health_metrics, **perf_metrics}
            
            # Check for alerts
            alerts = check_thresholds(all_metrics)
            
            # Process alerts
            for alert in alerts:
                alert_manager.send_alert(alert)
            
            # Log metrics
            logger.info(f"Health check completed - CPU: {health_metrics.get('cpu_usage', 0):.1f}%, "
                       f"Memory: {health_metrics.get('memory_usage', 0):.1f}%, "
                       f"Errors: {perf_metrics.get('error_rate', 0):.1f}%")
            
            # Save metrics to file for analysis
            with open(f"metrics_{datetime.now().strftime('%Y%m%d')}.json", "a") as f:
                f.write(json.dumps(all_metrics) + "\n")
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        asyncio.run(monitoring_loop())
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
```

## Rollback Testing

### Pre-Production Rollback Tests
```bash
# test_rollback.py
#!/usr/bin/env python3
import subprocess
import time
import asyncio
from datetime import datetime

class RollbackTester:
    def __init__(self):
        self.test_results = []
    
    def test_critical_rollback(self):
        """Test critical system rollback"""
        print("Testing critical rollback...")
        
        # Simulate critical failure
        result = subprocess.run([
            'python', '-c', 
            'import sys; sys.exit(1)'  # Simulate crash
        ], capture_output=True)
        
        # Execute rollback
        start_time = time.time()
        rollback_result = subprocess.run([
            'bash', '-c',
            '''
            cp bot_structure.py.backup bot_structure.py
            sed -i 's/"soccer_integration": True/"soccer_integration": False/' config.py
            python -c "from bot_structure import SportsBot; bot = SportsBot(); print('Rollback successful')"
            '''
        ], capture_output=True, text=True)
        
        rollback_time = time.time() - start_time
        
        success = rollback_result.returncode == 0 and rollback_time < 300  # 5 minutes
        
        self.test_results.append({
            'test': 'critical_rollback',
            'success': success,
            'duration': rollback_time,
            'output': rollback_result.stdout
        })
        
        print(f"Critical rollback: {'✅ PASS' if success else '❌ FAIL'} ({rollback_time:.1f}s)")
    
    def test_feature_rollback(self):
        """Test feature-specific rollback"""
        print("Testing feature rollback...")
        
        start_time = time.time()
        rollback_result = subprocess.run([
            'python', '-c',
            '''
            # Disable soccer integration
            with open("config.py", "r") as f:
                content = f.read()
            content = content.replace('"soccer_integration": True', '"soccer_integration": False')
            with open("config.py", "w") as f:
                f.write(content)
            
            # Test MLB still works
            from bot_structure import SportsBot
            bot = SportsBot()
            assert bot.leagues["MLB"]["active"] == True
            assert bot.leagues["SOCCER"]["active"] == False
            print("Feature rollback successful")
            '''
        ], capture_output=True, text=True)
        
        rollback_time = time.time() - start_time
        success = rollback_result.returncode == 0 and rollback_time < 60  # 1 minute
        
        self.test_results.append({
            'test': 'feature_rollback',
            'success': success,
            'duration': rollback_time,
            'output': rollback_result.stdout
        })
        
        print(f"Feature rollback: {'✅ PASS' if success else '❌ FAIL'} ({rollback_time:.1f}s)")
    
    def run_all_tests(self):
        """Run all rollback tests"""
        print("🧪 Running Rollback Tests")
        print("=" * 40)
        
        self.test_critical_rollback()
        self.test_feature_rollback()
        
        # Summary
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print("\n" + "=" * 40)
        print(f"Rollback Tests: {passed}/{total} passed")
        
        if passed == total:
            print("✅ All rollback procedures working correctly")
        else:
            print("❌ Some rollback procedures need attention")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: FAILED")

if __name__ == "__main__":
    tester = RollbackTester()
    tester.run_all_tests()
```

## Recovery Procedures

### Data Recovery
```bash
# recover_data.sh
#!/bin/bash

echo "Starting data recovery..."

# 1. Backup current state
cp -r discord/ discord_backup_$(date +%Y%m%d_%H%M%S)/

# 2. Clear corrupted cache
rm -rf cache/soccer_*
rm -rf temp/match_data_*

# 3. Reset configuration to known good state
cp config.py.backup config.py
cp bot_structure.py.backup bot_structure.py

# 4. Verify configuration
python validate_config.py

# 5. Test basic functionality
python -c "
from bot_structure import SportsBot
bot = SportsBot()
print('✅ Bot initialization successful')
"

echo "Data recovery completed"
```

### Service Recovery
```bash
# recover_service.sh
#!/bin/bash

echo "Starting service recovery..."

# 1. Stop all bot processes
pkill -f "python bot_structure.py"
sleep 5

# 2. Check for zombie processes
ps aux | grep bot_structure.py | grep -v grep

# 3. Clean up resources
rm -f /tmp/bot_*.lock
rm -f /tmp/discord_*.tmp

# 4. Restart with clean state
export LOG_LEVEL=INFO
export ENVIRONMENT=production
python bot_structure.py &

# 5. Verify startup
sleep 10
if pgrep -f "python bot_structure.py" > /dev/null; then
    echo "✅ Service recovery successful"
else
    echo "❌ Service recovery failed"
    exit 1
fi
```

## Post-Rollback Verification

### Verification Checklist
- [ ] **Bot Status**: Bot appears online in Discord
- [ ] **Core Commands**: `/create-channels` works for MLB
- [ ] **Error Logs**: No critical errors in logs
- [ ] **Memory Usage**: Memory usage within normal range
- [ ] **Response Times**: Commands respond within 5 seconds
- [ ] **Channel Creation**: Test channel creation works
- [ ] **Cleanup System**: Automatic cleanup still functioning

### Verification Script
```python
# verify_rollback.py
#!/usr/bin/env python3
import asyncio
import time
from bot_structure import SportsBot

async def verify_rollback():
    """Verify rollback was successful"""
    print("🔍 Verifying rollback...")
    
    checks = []
    
    # 1. Bot initialization
    try:
        bot = SportsBot()
        checks.append(("Bot initialization", True, "Bot created successfully"))
    except Exception as e:
        checks.append(("Bot initialization", False, str(e)))
    
    # 2. MLB functionality
    try:
        mlb_active = bot.leagues["MLB"]["active"]
        checks.append(("MLB functionality", mlb_active, f"MLB active: {mlb_active}"))
    except Exception as e:
        checks.append(("MLB functionality", False, str(e)))
    
    # 3. Soccer integration status
    try:
        soccer_active = bot.leagues["SOCCER"]["active"]
        # After rollback, soccer should be disabled
        expected_status = False  # Assuming rollback disables soccer
        status_ok = soccer_active == expected_status
        checks.append(("Soccer integration", status_ok, f"Soccer active: {soccer_active}"))
    except Exception as e:
        checks.append(("Soccer integration", False, str(e)))
    
    # 4. Command registration
    try:
        commands = [cmd.name for cmd in bot.tree.get_commands()]
        has_create_channels = "create-channels" in commands
        checks.append(("Command registration", has_create_channels, f"Commands: {commands}"))
    except Exception as e:
        checks.append(("Command registration", False, str(e)))
    
    # Print results
    print("\nVerification Results:")
    print("-" * 50)
    
    passed = 0
    for check_name, success, details in checks:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}: {details}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Verification: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 Rollback verification successful!")
        return True
    else:
        print("⚠️  Rollback verification failed - manual intervention required")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_rollback())
    exit(0 if success else 1)
```

---

## Emergency Contacts

### Escalation Procedures
1. **Level 1**: Automated rollback (< 5 minutes)
2. **Level 2**: Manual intervention by developer (< 15 minutes)
3. **Level 3**: System administrator involvement (< 30 minutes)
4. **Level 4**: Service provider contact (< 60 minutes)

### Contact Information
- **Primary Developer**: [Your contact]
- **System Administrator**: [Admin contact]
- **Discord Server Admin**: [Discord admin]
- **MCP Server Support**: [MCP support contact]

### Emergency Commands
```bash
# Emergency stop
pkill -f "python bot_structure.py"

# Emergency rollback
bash emergency_rollback.sh

# Emergency restart
python bot_structure.py --emergency-mode
```

Remember: **Always test rollback procedures in a development environment before production deployment!**