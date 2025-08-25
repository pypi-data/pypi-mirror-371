"""Command-line interface for EC2 Manager."""

from ec2simpleconnect.manager import EC2Manager
import logging
import sys

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the CLI."""
    try:
        manager = EC2Manager()
        manager.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
