"""
Main CLI entry point for STFU - Terraform wrapper.
"""

import sys
import json
import click

from .terraform import TerraformWrapper
from .parser import TerraformOutputParser


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
        allow_interspersed_args=True,
    ),
    help="""STFU - Simple Terraform Frontend Utility
    
    A drop-in replacement for terraform with enhanced parsing capabilities.
    
    Examples:
      stfu init
      stfu plan
      stfu plan --json-output plan.json
      stfu apply
      stfu destroy
    """
)
@click.option('--json-output', '-j', type=click.Path(), help='Save parsed output to JSON file instead of displaying')
@click.pass_context
def main(ctx: click.Context, json_output: str) -> None:
    # Get all arguments passed to the command
    args = ctx.params.get('args', []) + ctx.args
    
    # If no arguments provided, show help
    if not args:
        print(ctx.get_help())
        ctx.exit()
    
    # Initialize components
    terraform = TerraformWrapper()
    parser = TerraformOutputParser()
    
    # Extract the terraform subcommand
    subcommand = args[0] if args else None
    
    try:
        # Execute terraform command and capture output
        result = terraform.execute(args)
        
        # Parse the output into structured data
        if subcommand == 'plan':
            parsed_data = parser.parse_plan_output(result.stdout)
            
            if json_output:
                # Save to JSON file
                with open(json_output, 'w') as f:
                    json.dump(parsed_data, f, indent=2)
                print(f"Parsed plan data saved to {json_output}")
            else:
                # Print structured data to console
                print(json.dumps(parsed_data, indent=2))
        else:
            # For other commands, just pass through the output
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        
        # Exit with the same code as terraform
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)





if __name__ == "__main__":
    main()
