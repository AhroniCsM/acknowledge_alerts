#!/usr/bin/env python3
"""
Script to automatically resolve all incidents/alerts in Coralogix using gRPC API
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Optional
from datetime import datetime


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
        """
        Initialize Coralogix Alerts Manager

        Args:
            api_key: Coralogix API key (Alerts, Rules and Tags API Key)
            region: Coralogix region (default: eu1)
        """
        self.api_key = api_key
        self.endpoint = self.REGIONS.get(region)

        if not self.endpoint:
            raise ValueError(f"Invalid region: {region}. Must be one of: {', '.join(self.REGIONS.keys())}")

        # Check if grpcurl is installed
        try:
            subprocess.run(['grpcurl', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: grpcurl is not installed or not in PATH")
            print("Please install grpcurl:")
            print("  macOS: brew install grpcurl")
            print("  Linux: https://github.com/fullstorydev/grpcurl/releases")
            sys.exit(1)

    def _call_grpc(self, service_method: str, data: Dict) -> Dict:
        """
        Call a gRPC method using grpcurl

        Args:
            service_method: The gRPC service method (e.g., 'ListIncidents')
            data: The request data as a dictionary

        Returns:
            Response data as dictionary
        """
        cmd = [
            'grpcurl',
            '-max-msg-sz', '52428800',  # 50MB max message size
            '-H', f'Authorization: Bearer {self.api_key}',
            '-d', json.dumps(data),
            self.endpoint,
            f'com.coralogixapis.incidents.v1.IncidentsService/{service_method}'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout:
                return json.loads(result.stdout)
            return {}

        except subprocess.CalledProcessError as e:
            print(f"Error calling gRPC method {service_method}:")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing gRPC response: {e}")
            print(f"  Response: {result.stdout}")
            raise

    def list_incidents(self) -> List[Dict]:
        """
        List all incidents from Coralogix

        Returns:
            List of incident dictionaries
        """
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
        """
        Acknowledge multiple incidents

        Args:
            incident_ids: List of incident IDs to acknowledge

        Returns:
            True if successful, False otherwise
        """
        if not incident_ids:
            return True

        request_data = {
            'incident_ids': incident_ids
        }

        try:
            response = self._call_grpc('AcknowledgeIncidents', request_data)
            return True
        except Exception as e:
            print(f"Error acknowledging incidents: {e}")
            return False

    def resolve_incidents(self, incident_ids: List[str]) -> bool:
        """
        Resolve multiple incidents

        Args:
            incident_ids: List of incident IDs to resolve

        Returns:
            True if successful, False otherwise
        """
        if not incident_ids:
            return True

        request_data = {
            'incident_ids': incident_ids
        }

        try:
            response = self._call_grpc('ResolveIncidents', request_data)
            return True
        except Exception as e:
            print(f"Error resolving incidents: {e}")
            return False

    def process_all_incidents(self, action: str = "acknowledge", state_filter: str = "INCIDENT_STATE_TRIGGERED") -> Dict[str, int]:
        """
        Process (acknowledge or resolve) all incidents that match the state filter

        Args:
            action: Action to perform - "acknowledge" or "resolve" (default: "acknowledge")
            state_filter: State to filter (default: "INCIDENT_STATE_TRIGGERED")

        Returns:
            Dictionary with counts of successful and failed operations
        """
        action_verb = "acknowledge" if action == "acknowledge" else "resolve"
        action_verb_ing = "acknowledging" if action == "acknowledge" else "resolving"
        action_verb_past = "acknowledged" if action == "acknowledge" else "resolved"

        print(f"Fetching all incidents with state: {state_filter}...")

        try:
            all_incidents = self.list_incidents()
        except Exception as e:
            print(f"Failed to list incidents: {e}")
            return {'successful': 0, 'failed': 0}

        # Filter incidents by state
        filtered_incidents = [
            inc for inc in all_incidents
            if inc.get('state') == state_filter
        ]

        # For acknowledge action, only show unacknowledged incidents (status = INCIDENT_STATUS_TRIGGERED)
        if action == "acknowledge":
            filtered_incidents = [
                inc for inc in filtered_incidents
                if inc.get('status') == 'INCIDENT_STATUS_TRIGGERED'
            ]

        print(f"Found {len(filtered_incidents)} incidents to {action_verb}")

        if len(filtered_incidents) == 0:
            print(f"No incidents to {action_verb}!")
            return {'successful': 0, 'failed': 0}

        # Print first 10 incident details
        print(f"\nShowing first 10 incidents:")
        for i, incident in enumerate(filtered_incidents[:10], 1):
            incident_id = incident.get('id')
            alert_name = incident.get('contextualLabels', {}).get('alert_name', 'Unknown')
            created_at = incident.get('createdAt', '')

            print(f"\n[{i}] Incident Details:")
            print(f"  ID: {incident_id}")
            print(f"  Alert Name: {alert_name}")
            print(f"  Created: {created_at}")
            print(f"  State: {incident.get('state', 'Unknown')}")

        if len(filtered_incidents) > 10:
            print(f"\n... and {len(filtered_incidents) - 10} more incidents")

        # Ask for confirmation
        print(f"\n{'='*60}")
        response = input(f"Do you want to {action_verb} all {len(filtered_incidents)} incidents? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled by user.")
            return {'successful': 0, 'failed': 0}

        print(f"\n{'='*60}")
        print(f"{action_verb_ing.capitalize()} incidents...")

        # Process in batches of 10
        batch_size = 10
        results = {'successful': 0, 'failed': 0}

        for i in range(0, len(filtered_incidents), batch_size):
            batch = filtered_incidents[i:i + batch_size]
            incident_ids = [inc.get('id') for inc in batch if inc.get('id')]

            batch_num = (i // batch_size) + 1
            total_batches = (len(filtered_incidents) + batch_size - 1) // batch_size

            print(f"\n[Batch {batch_num}/{total_batches}] {action_verb_ing.capitalize()} {len(incident_ids)} incidents...")

            # Call the appropriate method
            if action == "acknowledge":
                success = self.acknowledge_incidents(incident_ids)
            else:
                success = self.resolve_incidents(incident_ids)

            if success:
                results['successful'] += len(incident_ids)
                print(f"  ✓ Successfully {action_verb_past} {len(incident_ids)} incidents")
            else:
                results['failed'] += len(incident_ids)
                print(f"  ✗ Failed to {action_verb} {len(incident_ids)} incidents")

        return results


def main():
    """Main entry point for the script"""

    # Check for help
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("Coralogix Alert Management Script")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 acknowledge_alerts.py [api-key] [region] [action]")
        print("\nArguments:")
        print("  api-key  : Coralogix API key (default: preconfigured)")
        print("  region   : Coralogix region - us1, us2, eu1, eu2, ap1, ap2, ap3")
        print("             (default: eu1)")
        print("  action   : 'acknowledge' or 'resolve' (default: acknowledge)")
        print("\nExamples:")
        print("  Acknowledge all incidents (default):")
        print("    python3 acknowledge_alerts.py")
        print("\n  Resolve all incidents:")
        print("    python3 acknowledge_alerts.py '' '' resolve")
        print("\n  Use custom API key:")
        print("    python3 acknowledge_alerts.py 'your-api-key' 'eu1' 'acknowledge'")
        print("\nEnvironment Variables:")
        print("  CORALOGIX_API_KEY   : Override default API key")
        print("  CORALOGIX_REGION    : Override default region")
        print("  CORALOGIX_ACTION    : Override default action")
        print("\nDifference between acknowledge and resolve:")
        print("  - acknowledge: Marks incident as acknowledged (keeps it open)")
        print("  - resolve: Closes the incident completely")
        print("=" * 60)
        sys.exit(0)

    # ========================================
    # CONFIGURATION - UPDATE THESE VALUES
    # ========================================
    DEFAULT_API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your Coralogix API key
    DEFAULT_REGION = 'eu1'  # Change to your region: us1, us2, eu1, eu2, ap1, ap2, ap3
    DEFAULT_ACTION = 'acknowledge'  # Options: 'acknowledge' or 'resolve'
    # ========================================

    # Get configuration from environment variables (can override defaults)
    api_key = os.getenv('CORALOGIX_API_KEY', DEFAULT_API_KEY)
    region = os.getenv('CORALOGIX_REGION', DEFAULT_REGION)
    action = os.getenv('CORALOGIX_ACTION', DEFAULT_ACTION)

    # Allow command-line override
    # Usage: python acknowledge_alerts.py [api-key] [region] [action]
    if len(sys.argv) > 1 and sys.argv[1]:
        api_key = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2]:
        region = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3]:
        action = sys.argv[3]

    # Validate action
    if action not in ['acknowledge', 'resolve']:
        print(f"ERROR: Invalid action '{action}'. Must be 'acknowledge' or 'resolve'")
        print("Run 'python3 acknowledge_alerts.py --help' for usage information")
        sys.exit(1)

    action_title = "Acknowledgment" if action == "acknowledge" else "Resolution"
    action_verb_past = "acknowledged" if action == "acknowledge" else "resolved"

    print("=" * 60)
    print(f"Coralogix Alert {action_title} Script")
    print("=" * 60)
    print(f"Region: {region}")
    print(f"Action: {action}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    try:
        # Initialize manager
        manager = CoralogixAlertsManager(api_key, region)

        # Process all triggered incidents
        results = manager.process_all_incidents(action=action)

        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Successfully {action_verb_past}: {results['successful']}")
        print(f"Failed to {action}: {results['failed']}")
        print(f"Total processed: {results['successful'] + results['failed']}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        if results['failed'] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
