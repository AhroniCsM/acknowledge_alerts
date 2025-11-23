#!/usr/bin/env python3
"""
Script to acknowledge Coralogix incidents with filtering options
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class CoralogixAlertsManager:
    """Manages Coralogix alerts/incidents via gRPC API"""
    
    # Coralogix gRPC endpoints by region
    REGIONS = {
        'us1': 'ng-api-grpc.us1.coralogix.com:443',
        'us2': 'ng-api-grpc.us2.coralogix.com:443',
        'eu1': 'ng-api-grpc.eu1.coralogix.com:443',
        'eu2': 'ng-api-grpc.eu2.coralogix.com:443',
        'ap1': 'ng-api-grpc.ap1.coralogix.com:443',
        'ap2': 'ng-api-grpc.ap2.coralogix.com:443',
        'ap3': 'ng-api-grpc.ap3.coralogix.com:443',
    }
    
    def __init__(self, api_key: str, region: str = 'eu1'):
        self.api_key = api_key
        self.endpoint = self.REGIONS.get(region)
        
        if not self.endpoint:
            raise ValueError(f"Invalid region: {region}. Must be one of: {', '.join(self.REGIONS.keys())}")
        
        # Check if grpcurl is installed
        try:
            subprocess.run(['grpcurl', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: grpcurl is not installed")
            print("Install: brew install grpcurl")
            sys.exit(1)
    
    def _call_grpc(self, service_method: str, data: Dict) -> Dict:
        cmd = [
            'grpcurl',
            '-max-msg-sz', '52428800',
            '-H', f'Authorization: Bearer {self.api_key}',
            '-d', json.dumps(data),
            self.endpoint,
            f'com.coralogixapis.incidents.v1.IncidentsService/{service_method}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout:
                return json.loads(result.stdout)
            return {}
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            raise
    
    def list_incidents(self) -> List[Dict]:
        all_incidents = []
        page_token = None
        
        while True:
            request_data = {}
            if page_token:
                request_data['page_token'] = page_token
            
            response = self._call_grpc('ListIncidents', request_data)
            incidents = response.get('incidents', [])
            all_incidents.extend(incidents)
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        return all_incidents
    
    def acknowledge_incidents(self, incident_ids: List[str]) -> bool:
        if not incident_ids:
            return True
        
        request_data = {'incident_ids': incident_ids}
        
        try:
            self._call_grpc('AcknowledgeIncidents', request_data)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def show_recent_alerts_summary(self, hours: int = 24):
        """Show summary of recent unacknowledged alerts grouped by alert name"""
        print(f"Fetching incidents from the last {hours} hours...")
        
        all_incidents = self.list_incidents()
        
        # Filter: triggered state, unacknowledged status, recent
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_unack = []
        for inc in all_incidents:
            if inc.get('state') != 'INCIDENT_STATE_TRIGGERED':
                continue
            if inc.get('status') != 'INCIDENT_STATUS_TRIGGERED':
                continue
            
            created = inc.get('createdAt', '')
            try:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                if created_dt.replace(tzinfo=None) >= cutoff_time:
                    recent_unack.append(inc)
            except:
                pass
        
        if not recent_unack:
            print(f"\nNo unacknowledged incidents in the last {hours} hours!")
            return None
        
        # Group by alert name
        by_alert = defaultdict(list)
        for inc in recent_unack:
            alert_name = inc.get('contextualLabels', {}).get('alert_name', 'Unknown')
            by_alert[alert_name].append(inc)
        
        print(f"\n{'='*80}")
        print(f"Found {len(recent_unack)} unacknowledged incidents from {len(by_alert)} unique alerts:")
        print(f"{'='*80}\n")
        
        for i, (alert_name, incidents) in enumerate(sorted(by_alert.items()), 1):
            severity = incidents[0].get('severity', 'Unknown')
            print(f"[{i}] {alert_name}")
            print(f"    Severity: {severity}")
            print(f"    Incidents: {len(incidents)}")
            print(f"    Latest: {incidents[0].get('createdAt', 'Unknown')}")
            print()
        
        return by_alert


def main():
    # ========================================
    # CONFIGURATION - UPDATE THESE VALUES
    # ========================================
    DEFAULT_API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your Coralogix API key
    DEFAULT_REGION = 'eu1'  # Change to your region: us1, us2, eu1, eu2, ap1, ap2, ap3
    # ========================================
    
    api_key = os.getenv('CORALOGIX_API_KEY', DEFAULT_API_KEY)
    region = os.getenv('CORALOGIX_REGION', DEFAULT_REGION)
    
    print("=" * 80)
    print("Coralogix Alert Acknowledgment Script (Filtered)")
    print("=" * 80)
    print(f"Region: {region}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        manager = CoralogixAlertsManager(api_key, region)
        
        # Show summary of recent alerts
        by_alert = manager.show_recent_alerts_summary(hours=24)
        
        if not by_alert:
            sys.exit(0)
        
        print("=" * 80)
        choice = input("Do you want to acknowledge ALL these incidents? (yes/no): ")
        
        if choice.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            sys.exit(0)
        
        # Collect all incident IDs
        all_ids = []
        for incidents in by_alert.values():
            all_ids.extend([inc.get('id') for inc in incidents if inc.get('id')])
        
        print(f"\nAcknowledging {len(all_ids)} incidents...")
        
        # Process in batches
        batch_size = 50
        success_count = 0
        
        for i in range(0, len(all_ids), batch_size):
            batch = all_ids[i:i + batch_size]
            if manager.acknowledge_incidents(batch):
                success_count += len(batch)
                print(f"  ✓ Acknowledged {len(batch)} incidents (Total: {success_count}/{len(all_ids)})")
            else:
                print(f"  ✗ Failed batch")
        
        print(f"\n{'='*80}")
        print(f"Successfully acknowledged: {success_count}")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

