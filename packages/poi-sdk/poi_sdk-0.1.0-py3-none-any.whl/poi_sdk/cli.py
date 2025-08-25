"""
Command-line interface for the Proof-of-Intent SDK.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from .generator import PoIGenerator
from .validator import PoIValidator
from .receipt import PoIReceipt
from .config import PoIConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Proof-of-Intent (PoI) SDK Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a receipt
  poi-cli generate --agent-id "my_agent" --action "data_read" \\
                   --resource "user_database" --objective "Read user profile"
  
  # Validate a receipt from file
  poi-cli validate --receipt-file receipt.json
  
  # Generate receipt with custom expiration
  poi-cli generate --agent-id "temp_agent" --action "api_call" \\
                   --resource "https://api.example.com" \\
                   --objective "Temporary API access" \\
                   --expiration-hours 0.5
  
  # Generate receipt with additional context
  poi-cli generate --agent-id "workflow_agent" --action "file_upload" \\
                   --resource "s3://bucket/files/" \\
                   --objective "Upload processed data" \\
                   --context '{"workflow_id": "wf_123", "priority": "high"}'
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a new PoI receipt')
    generate_parser.add_argument('--agent-id', required=True, help='Agent identifier')
    generate_parser.add_argument('--action', required=True, help='Action being performed')
    generate_parser.add_argument('--resource', required=True, help='Target resource')
    generate_parser.add_argument('--objective', required=True, help='Declared objective')
    generate_parser.add_argument('--expiration-hours', type=float, default=1.0, 
                               help='Expiration time in hours (default: 1.0)')
    generate_parser.add_argument('--risk-context', choices=['low', 'medium', 'high', 'critical'],
                               default='medium', help='Risk context (default: medium)')
    generate_parser.add_argument('--context', help='Additional context as JSON string')
    generate_parser.add_argument('--output', help='Output file path (default: stdout)')
    generate_parser.add_argument('--config', help='Configuration file path')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a PoI receipt')
    validate_parser.add_argument('--receipt-file', required=True, help='Receipt file to validate')
    validate_parser.add_argument('--config', help='Configuration file path')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show SDK information')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'generate':
            generate_receipt(args)
        elif args.command == 'validate':
            validate_receipt(args)
        elif args.command == 'info':
            show_info()
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_receipt(args: argparse.Namespace):
    """Generate a new PoI receipt."""
    # Load configuration
    config = PoIConfig(args.config) if args.config else PoIConfig()
    
    # Parse additional context
    additional_context = {}
    if args.context:
        try:
            additional_context = json.loads(args.context)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in context: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create generator
    generator = PoIGenerator(config=config)
    
    # Generate receipt
    receipt = generator.generate_receipt(
        agent_id=args.agent_id,
        action=args.action,
        target_resource=args.resource,
        declared_objective=args.objective,
        expiration_hours=args.expiration_hours,
        risk_context=args.risk_context,
        additional_context=additional_context
    )
    
    # Output receipt
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(receipt.to_dict(), f, indent=2)
        print(f"Receipt generated and saved to: {args.output}")
    else:
        print(json.dumps(receipt.to_dict(), indent=2))
    
    # Show summary
    print(f"\nReceipt Summary:")
    print(f"  ID: {receipt.receipt_id}")
    print(f"  Agent: {receipt.agent_id}")
    print(f"  Action: {receipt.action}")
    print(f"  Resource: {receipt.target_resource}")
    print(f"  Expires: {receipt.expiration_time}")
    print(f"  Risk: {receipt.risk_context}")


def validate_receipt(args: argparse.Namespace):
    """Validate a PoI receipt."""
    # Check if receipt file exists
    receipt_path = Path(args.receipt_file)
    if not receipt_path.exists():
        print(f"Error: Receipt file not found: {args.receipt_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load configuration
    config = PoIConfig(args.config) if args.config else PoIConfig()
    
    # Load receipt
    try:
        with open(receipt_path, 'r') as f:
            receipt_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in receipt file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create receipt object
    try:
        receipt = PoIReceipt(**receipt_data)
    except Exception as e:
        print(f"Error: Invalid receipt format: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create validator
    validator = PoIValidator(config=config)
    
    # Validate receipt
    try:
        is_valid = validator.validate_receipt(receipt)
        
        if is_valid:
            print("✅ Receipt is VALID")
        else:
            print("❌ Receipt is INVALID")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
    
    # Show detailed information if verbose
    if args.verbose:
        print(f"\nReceipt Details:")
        print(f"  ID: {receipt.receipt_id}")
        print(f"  Timestamp: {receipt.timestamp}")
        print(f"  Agent: {receipt.agent_id}")
        print(f"  Action: {receipt.action}")
        print(f"  Resource: {receipt.target_resource}")
        print(f"  Objective: {receipt.declared_objective}")
        print(f"  Risk Context: {receipt.risk_context}")
        print(f"  Expiration: {receipt.expiration_time}")
        print(f"  Version: {receipt.version}")
        
        if receipt.signature:
            print(f"  Signature: {receipt.signature[:50]}...")
            print(f"  Algorithm: {receipt.signature_algorithm}")
        
        if receipt.additional_context:
            print(f"  Additional Context: {json.dumps(receipt.additional_context, indent=2)}")
        
        # Check expiration
        if receipt.is_expired():
            print("  ⚠️  Status: EXPIRED")
        else:
            time_left = receipt.time_until_expiration()
            if time_left:
                print(f"  ✅ Status: VALID (expires in {time_left:.0f} seconds)")
            else:
                print("  ✅ Status: VALID")


def show_info():
    """Show SDK information."""
    print("Proof-of-Intent (PoI) SDK")
    print("=" * 40)
    print(f"Version: {PoIReceipt.__module__.split('.')[0]}")
    print(f"Description: A cryptographic framework for creating trustworthy AI agent transactions")
    print()
    print("Core Components:")
    print("  • PoIReceipt: Receipt data structure")
    print("  • PoIGenerator: Receipt generation and signing")
    print("  • PoIValidator: Receipt validation and verification")
    print("  • PoIConfig: Configuration management")
    print()
    print("For more information, visit:")
    print("  https://github.com/giovannypietro/poi")
    print()
    print("Use 'poi-cli --help' to see available commands.")


if __name__ == '__main__':
    main()
