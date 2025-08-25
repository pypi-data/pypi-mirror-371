
```markdown
# EC2 Simple connect

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A powerful CLI tool for managing and connecting to AWS EC2 instances with automatic security group management and configuration handling.

## Features

- 🚀 Easy connection to EC2 instances
- 🔒 Automatic security group management
- ⚙️ Persistent configuration management
- 🌍 Region selection and management
- 💻 Instance state handling (start/stop)
- 🔑 SSH key management
- 🛡️ Secure credential handling
- 📝 Comprehensive logging

## Installation

```bash
pip install ec2-simple-connect
```

## Prerequisites

1. Python 3.7 or higher
2. AWS Account and credentials
3. SSH key pairs for your EC2 instances

## Quick Start

1. Configure your AWS credentials:
```bash
aws configure
```

2. Run EC2 Manager:
```bash
ec2-simple-connect
```

On first run, the tool will guide you through configuration setup.

## Configuration

The tool creates a configuration file at `~/.ec2manager/config.ini` with the following settings:

```ini
[DEFAULT]
ssh_key_path = ~/.ssh
default_region = us-east-1
default_username = ec2-user
security_group_protocol = tcp
security_group_port = 22
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| ssh_key_path | Path to SSH keys directory | ~/.ssh |
| default_region | Default AWS region | us-east-1 |
| default_username | Default SSH username | ec2-user |
| security_group_protocol | Security group protocol | tcp |
| security_group_port | Security group port | 22 |

## Usage

### Basic Usage

1. Start the tool:
```bash
ec2-manager
```

2. Select a region from the displayed list

3. Choose an instance to connect to

4. Enter username (or press Enter for default)

### Features in Detail

#### Region Selection
- Lists all available AWS regions
- Remembers last used region
- Easy switching between regions

#### Instance Management
- Lists all instances with details:
  - Instance ID
  - Name
  - Status
  - Public IP
- Supports starting stopped instances
- Handles instance state transitions

#### Security Group Management
- Automatically manages security group rules
- Adds rules for your current IP
- Removes rules when disconnecting
- Supports custom protocols and ports

#### SSH Connection
- Automatic SSH key selection
- Custom username support
- Handles different instance states
- Secure connection settings

## Security

- Configurations stored in protected directory (`~/.ec2manager`)
- Secure file permissions (600 for config files)
- Temporary security group rules
- No storage of sensitive credentials

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ec2-manager.git
cd ec2-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Check style
flake8 src tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Common Issues and Solutions

### Issue: "Unable to locate credentials"
- Ensure AWS credentials are configured: `aws configure`
- Check `~/.aws/credentials` exists and has valid credentials

### Issue: "Permission denied (publickey)"
- Verify SSH key exists in configured path
- Check key permissions (should be 600)
- Confirm correct username for instance

### Issue: "Connection timed out"
- Verify security group rules
- Check instance public IP is accessible
- Ensure instance is running

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- AWS SDK for Python (Boto3)
- The AWS CLI team for inspiration
- All contributors and users

## Support

If you encounter any issues or need support, please:

1. Check the [Common Issues](#common-issues-and-solutions) section
2. Search existing GitHub issues
3. Create a new issue if needed


## Project Status

Active development - Accepting contributions

## Author

Meraj (meru.meraj64@gmail.com)

---

Made with ❤️ by meraj64


