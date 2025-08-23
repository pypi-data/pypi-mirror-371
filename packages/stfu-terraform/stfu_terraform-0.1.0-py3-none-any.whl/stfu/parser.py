"""Parser for Terraform plan output structure."""

import re
from typing import Dict, Any, List, Optional


class TerraformOutputParser:
    """Parser that converts terraform plan output into nested dictionaries."""
    
    def __init__(self):
        # Patterns for parsing terraform plan structure
        self.patterns = {
            "resource_header": re.compile(r'^\s*#\s+(.+?)\s+will be (created|destroyed|updated)\s*$'),
            "resource_start": re.compile(r'^\s*([+~-])\s+resource\s+"([^"]+)"\s+"([^"]+)"\s*\{?\s*$'),
            "attribute": re.compile(r'^\s*([+~-]?)\s*([^=]+?)\s*=\s*(.+)$'),
            "block_start": re.compile(r'^\s*([+~-]?)\s*([^{]+?)\s*\{\s*$'),
            "block_end": re.compile(r'^\s*\}\s*$'),
            "plan_summary": re.compile(r'Plan:\s*(\d+)\s*to\s*add,\s*(\d+)\s*to\s*change,\s*(\d+)\s*to\s*destroy'),
        }
    
    def parse_plan_output(self, output: str) -> Dict[str, Any]:
        """Parse terraform plan output into structured nested dictionaries."""
        result = {
            "resources": [],
            "summary": {"add": 0, "change": 0, "destroy": 0}
        }
        
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Check for resource start
            resource_match = self.patterns["resource_start"].search(line)
            if resource_match:
                action_symbol = resource_match.group(1)
                resource_type = resource_match.group(2)
                resource_name = resource_match.group(3)
                
                # Determine action
                action = {"+": "create", "~": "update", "-": "destroy"}.get(action_symbol, "unknown")
                
                # Parse resource block
                resource_data, i = self._parse_resource_block(lines, i + 1)
                
                result["resources"].append({
                    "action": action,
                    "type": resource_type,
                    "name": resource_name,
                    "address": f"{resource_type}.{resource_name}",
                    "attributes": resource_data
                })
                continue
            
            # Check for plan summary
            summary_match = self.patterns["plan_summary"].search(line)
            if summary_match:
                result["summary"]["add"] = int(summary_match.group(1))
                result["summary"]["change"] = int(summary_match.group(2))
                result["summary"]["destroy"] = int(summary_match.group(3))
            
            i += 1
        
        return result
    
    def _parse_resource_block(self, lines: List[str], start_index: int) -> tuple[Dict[str, Any], int]:
        """Parse a resource block starting from start_index, return (attributes, next_index)."""
        attributes = {}
        i = start_index
        brace_count = 1  # We already opened one brace
        
        while i < len(lines) and brace_count > 0:
            line = lines[i].rstrip()
            
            # Skip empty lines and comments
            if not line or line.strip().startswith('#'):
                i += 1
                continue
            
            # Check for closing brace
            if self.patterns["block_end"].search(line):
                brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
                continue
            
            # Check for nested block start
            block_match = self.patterns["block_start"].search(line)
            if block_match:
                block_name = block_match.group(2).strip()
                nested_block, i = self._parse_nested_block(lines, i + 1)
                
                # Handle multiple blocks with same name (convert to list)
                if block_name in attributes:
                    if not isinstance(attributes[block_name], list):
                        attributes[block_name] = [attributes[block_name]]
                    attributes[block_name].append(nested_block)
                else:
                    attributes[block_name] = nested_block
                continue
            
            # Check for attribute
            attr_match = self.patterns["attribute"].search(line)
            if attr_match:
                attr_name = attr_match.group(2).strip()
                attr_value = attr_match.group(3).strip()
                
                # Clean up the value (remove quotes, handle special values)
                attr_value = self._clean_attribute_value(attr_value)
                attributes[attr_name] = attr_value
            
            i += 1
        
        return attributes, i
    
    def _parse_nested_block(self, lines: List[str], start_index: int) -> tuple[Dict[str, Any], int]:
        """Parse a nested block (like backend, cdn_policy, etc.)."""
        block_data = {}
        i = start_index
        brace_count = 1
        
        while i < len(lines) and brace_count > 0:
            line = lines[i].rstrip()
            
            if not line or line.strip().startswith('#'):
                i += 1
                continue
            
            if self.patterns["block_end"].search(line):
                brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
                continue
            
            # Handle nested attributes
            attr_match = self.patterns["attribute"].search(line)
            if attr_match:
                attr_name = attr_match.group(2).strip()
                attr_value = attr_match.group(3).strip()
                attr_value = self._clean_attribute_value(attr_value)
                block_data[attr_name] = attr_value
            
            i += 1
        
        return block_data, i
    
    def _clean_attribute_value(self, value: str) -> str:
        """Clean up attribute values (remove quotes, handle special terraform values)."""
        value = value.strip()
        
        # Remove surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        
        # Handle terraform special values
        if value == "(known after apply)":
            return None
        
        # Handle boolean values
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"
        
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        return value
