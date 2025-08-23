"""
Terraform command wrapper and execution module.
"""

import subprocess
import shutil
from typing import List, Optional, NamedTuple
from pathlib import Path




class TerraformResult(NamedTuple):
    """Result of a terraform command execution."""
    returncode: int
    stdout: str
    stderr: str
    command: List[str]


class TerraformWrapper:
    """Simple wrapper for executing Terraform commands."""
    
    def __init__(self):
        self.terraform_path = self._find_terraform()
    
    def _find_terraform(self) -> str:
        """Find the terraform binary in PATH."""
        terraform_path = shutil.which("terraform")
        if not terraform_path:
            raise RuntimeError(
                "Terraform not found in PATH. Please install Terraform first.\n"
                "Visit: https://developer.hashicorp.com/terraform/downloads"
            )
        return terraform_path
    
    def execute(self, args: List[str]) -> TerraformResult:
        """
        Execute a terraform command with the given arguments.
        
        Args:
            args: List of arguments to pass to terraform
            
        Returns:
            TerraformResult containing the execution results
        """
        # Build the full command
        command = [self.terraform_path] + args
        
        try:
            # Execute the command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            return TerraformResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=command
            )
            
        except FileNotFoundError:
            raise RuntimeError(f"Terraform binary not found at: {self.terraform_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to execute terraform command: {str(e)}")
    

