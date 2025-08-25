#!/usr/bin/env python3

"""
EC2 Manager - A tool to manage and connect to AWS EC2 instances
"""

import boto3
import subprocess
from requests import get
import os
import sys
from botocore.exceptions import ClientError
import logging
import configparser
import json
from pathlib import Path
import time

# Setup logging
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EC2Manager:
    def __init__(self):
        # Setup config directory and file paths
        self.config_dir = os.path.join(str(Path.home()), '.ec2simpleconnet')
        self.config_file = os.path.join(self.config_dir, 'config.ini')
        
        # Load or create configuration
        self.config = self.load_config()
        self.ec2_client = None
        self.current_region = None
        self.key_path = self.config.get('DEFAULT', 'ssh_key_path')

    def get_user_config(self):
        """Prompt user for configuration values"""
        print("\nPlease provide default configuration values:")
        
        # Get SSH key path
        default_key_path = os.path.join(str(Path.home()), '.ssh')
        ssh_key_path = input(f"SSH key path [{default_key_path}]: ").strip()
        ssh_key_path = ssh_key_path if ssh_key_path else default_key_path

        # Get default region
        default_region = 'us-east-1'
        region = input(f"Default AWS region [{default_region}]: ").strip()
        region = region if region else default_region

        # Get default username
        default_username = 'ec2-user'
        username = input(f"Default EC2 username [{default_username}]: ").strip()
        username = username if username else default_username

        # Get default security group protocol
        default_protocol = 'tcp'
        protocol = input(f"Default security group protocol [{default_protocol}]: ").strip()
        protocol = protocol if protocol else default_protocol

        # Get default security group port
        default_port = '22'
        port = input(f"Default security group port [{default_port}]: ").strip()
        port = port if port else default_port

        return {
            'ssh_key_path': ssh_key_path,
            'default_region': region,
            'default_username': username,
            'security_group_protocol': protocol,
            'security_group_port': port
        }

    def load_config(self):
        """Load configuration from config file or create new one"""
        config = configparser.ConfigParser()
        
        # Create config directory if it doesn't exist
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            # Set directory permissions to 700 (rwx------)
            os.chmod(self.config_dir, 0o700)
        except Exception as e:
            logger.error(f"Failed to create config directory: {e}")
            sys.exit(1)

        # Check if config file exists
        if not os.path.exists(self.config_file):
            logger.info("No configuration file found. Creating new one...")
            
            # Get configuration from user
            user_config = self.get_user_config()
            
            # Create new config
            config['DEFAULT'] = user_config
            
            # Save configuration
            try:
                with open(self.config_file, 'w') as f:
                    config.write(f)
                # Set file permissions to 600 (rw-------)
                os.chmod(self.config_file, 0o600)
                logger.info(f"Configuration saved to {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to save configuration: {e}")
                sys.exit(1)
        else:
            try:
                config.read(self.config_file)
            except Exception as e:
                logger.error(f"Failed to read configuration: {e}")
                sys.exit(1)

        # Validate configuration
        required_keys = ['ssh_key_path', 'default_region', 'default_username', 
                        'security_group_protocol', 'security_group_port']
        for key in required_keys:
            if key not in config['DEFAULT']:
                logger.error(f"Missing required configuration key: {key}")
                # Backup existing config
                if os.path.exists(self.config_file):
                    backup_file = f"{self.config_file}.bak"
                    os.rename(self.config_file, backup_file)
                    logger.info(f"Existing configuration backed up to {backup_file}")
                
                # Get new configuration
                user_config = self.get_user_config()
                config['DEFAULT'] = user_config
                
                # Save new configuration
                with open(self.config_file, 'w') as f:
                    config.write(f)
                os.chmod(self.config_file, 0o600)
                logger.info(f"New configuration saved to {self.config_file}")
                break

        return config

    def get_regions(self):
        """Get list of AWS regions"""
        try:
            client = boto3.client('ec2')
            response = client.describe_regions()
            return response['Regions']
        except ClientError as e:
            logger.error(f"Error getting regions: {e}")
            sys.exit(1)

    def select_region(self):
        """Let user select a region"""
        regions = self.get_regions()
        print("\nAvailable Regions:")
        for idx, region in enumerate(regions, 1):
            print(f"{idx}) {region['RegionName']}")

        while True:
            try:
                choice = int(input('\nPlease select a region number: '))
                if 1 <= choice <= len(regions):
                    selected_region = regions[choice-1]['RegionName']
                    self.ec2_client = boto3.client('ec2', region_name=selected_region)
                    self.current_region = selected_region
                    return
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def get_instances(self):
        """Get list of EC2 instances"""
        try:
            response = self.ec2_client.describe_instances()
            if not response['Reservations']:
                logger.info("No instances found in this region")
                return None
            return response['Reservations']
        except ClientError as e:
            logger.error(f"Error getting instances: {e}")
            return None

    def display_instances(self, reservations):
        """Display EC2 instances"""
        if not reservations:
            return None

        print("\nAvailable Instances:")
        for idx, reservation in enumerate(reservations, 1):
            instance = reservation['Instances'][0]
            status = instance['State']['Name']
            instance_id = instance['InstanceId']
            
            # Get instance name from tags
            name = "no-name"
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']
                    break

            # Get public IP if available
            public_ip = instance.get('PublicIpAddress', 'No public IP')

            print(f"{idx}) Instance ID: {instance_id} | Name: {name} | Status: {status} | IP: {public_ip}")
        return True

    def update_security_group(self, instance, current_ip):
        """Update security group rules"""
        try:
            sg_id = instance['SecurityGroups'][0]['GroupId']
            logger.info(f"Updating security group: {sg_id}")

            protocol = self.config.get('DEFAULT', 'security_group_protocol')
            port = int(self.config.get('DEFAULT', 'security_group_port'))

            # Get current security group rules
            sg_response = self.ec2_client.describe_security_groups(GroupIds=[sg_id])
            sg_rules = sg_response['SecurityGroups'][0]['IpPermissions']

            # Check if our IP is already allowed
            ip_already_allowed = False
            for rule in sg_rules:
                if (rule.get('IpProtocol') == protocol and 
                    rule.get('FromPort') == port and 
                    rule.get('ToPort') == port):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range['CidrIp'] == f"{current_ip}/32":
                            ip_already_allowed = True
                            break

            if not ip_already_allowed:
                # Add new rule for current IP
                try:
                    self.ec2_client.authorize_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[
                            {
                                'IpProtocol': protocol,
                                'FromPort': port,
                                'ToPort': port,
                                'IpRanges': [
                                    {
                                        'CidrIp': f"{current_ip}/32",
                                        'Description': f'Temporary {protocol.upper()} access from EC2SimpleConnect'
                                    }
                                ]
                            }
                        ]
                    )
                    logger.info(f"Added new security group rule for IP: {current_ip}")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'InvalidPermission.Duplicate':
                        raise

        except ClientError as e:
            logger.error(f"Error updating security group: {e}")
            return False
        return True

    def cleanup_security_group(self, instance):
        """Clean up temporary security group rules"""
        try:
            sg_id = instance['SecurityGroups'][0]['GroupId']
            
            # Get current security group rules
            sg_response = self.ec2_client.describe_security_groups(GroupIds=[sg_id])
            
            # Find and remove rules created by this tool
            for rule in sg_response['SecurityGroups'][0]['IpPermissions']:
                if rule.get('IpRanges'):
                    for ip_range in rule['IpRanges']:
                        if ip_range.get('Description', '').startswith('Temporary'):
                            self.ec2_client.revoke_security_group_ingress(
                                GroupId=sg_id,
                                IpPermissions=[rule]
                            )
                            logger.info(f"Removed temporary security group rule: {ip_range['CidrIp']}")
        
        except ClientError as e:
            logger.error(f"Error cleaning up security group: {e}")

    def wait_for_instance(self, instance_id, target_state):
        """Wait for instance to reach desired state"""
        logger.info(f"Waiting for instance {instance_id} to become {target_state}...")
        try:
            waiter = self.ec2_client.get_waiter(f'instance_{target_state}')
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 40}
            )
            return True
        except Exception as e:
            logger.error(f"Error waiting for instance: {e}")
            return False

    def connect_to_instance(self, instance, username=None):
        """Connect to EC2 instance via SSH"""
        try:
            # Get instance details
            instance_id = instance['InstanceId']
            public_ip = instance.get('PublicIpAddress')
            key_name = instance.get('KeyName')

            if not all([public_ip, key_name]):
                logger.error("Instance missing required connection details")
                return False

            # Construct key path
            key_path = os.path.expanduser(f"{self.key_path}/{key_name}.pem")
            if not os.path.exists(key_path):
                logger.error(f"Key file not found: {key_path}")
                return False

            # Get username
            if not username:
                username = self.config.get('DEFAULT', 'default_username')

            # Check instance state and start if needed
            if instance['State']['Name'] == 'stopped':
                logger.info(f"Starting instance {instance_id}")
                self.ec2_client.start_instances(InstanceIds=[instance_id])
                if not self.wait_for_instance(instance_id, 'running'):
                    return False
                
                # Wait for status checks
                logger.info("Waiting for instance status checks...")
                time.sleep(30)  # Give additional time for SSH to become available

            # Connect via SSHSSH
            logger.info(f"Connecting to {public_ip} as {username}")
            ssh_command = [
                'ssh',
                '-i', key_path,
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f"{username}@{public_ip}"
            ]
            subprocess.run(ssh_command, check=True)
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"SSH connection failed: {e}")
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return False

    def run(self):
        """Main execution flow"""
        selected_instance = None
        try:
            # Select region
            self.select_region()

            # Get and display instances
            reservations = self.get_instances()
            if not self.display_instances(reservations):
                return

            # Get instance selection
            while True:
                try:
                    choice = int(input('\nSelect instance number to connect: '))
                    if 1 <= choice <= len(reservations):
                        selected_instance = reservations[choice-1]['Instances'][0]
                        break
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")

            # Get current IP
            try:
                current_ip = get('https://api.ipify.org').text
                logger.info(f"Current IP: {current_ip}")
            except Exception as e:
                logger.error(f"Failed to get current IP: {e}")
                return

            # Update security group
            if not self.update_security_group(selected_instance, current_ip):
                return

            # Get username
            username = input('Enter username (press Enter for default): ').strip() or None

            # Connect to instance
            self.connect_to_instance(selected_instance, username)

        except KeyboardInterrupt:
            logger.info("\nOperation cancelled by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            # Cleanup security group rules if instance was selected
            if selected_instance:
                self.cleanup_security_group(selected_instance)
def main():
    """Main entry point"""
    try:
        manager = EC2Manager()
        manager.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()