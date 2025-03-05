import json
import os
import base64
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('curl_generator')

class CURLGenerator:
    """
    Class for generating curl commands for API calls
    """
    
    def __init__(self, api_endpoint: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the CURL generator
        
        Args:
            api_endpoint: API endpoint URL
            username: Basic auth username (optional)
            password: Basic auth password (optional)
        """
        self.api_endpoint = api_endpoint
        self.username = username
        self.password = password
    
    def generate_curl_commands(self, transformed_data: Dict[str, Any]) -> List[str]:
        """
        Generate curl commands for transformed data
        
        Args:
            transformed_data: Transformed data in API-ready format
            
        Returns:
            List of curl commands as strings
        """
        if "Document" not in transformed_data or not transformed_data["Document"]:
            logger.warning("No documents found in transformed data")
            return []
            
        # Format the whole document into one API call
        return [self._generate_single_curl_command(transformed_data)]
    
    def _generate_single_curl_command(self, data: Dict[str, Any]) -> str:
        """
        Generate a single curl command for the given data
        
        Args:
            data: Data for a single API call
            
        Returns:
            Curl command as string
        """
        # Prepare the curl command
        curl_command = [
            "curl",
            f"--url '{self.api_endpoint}'",
            "-X POST",
            "-H 'Content-Type: application/json'"
        ]
        
        # Add basic auth if provided
        if self.username and self.password:
            auth_string = f"{self.username}:{self.password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            curl_command.append(f"-H 'Authorization: Basic {encoded_auth}'")
        
        # Add data with proper indentation for readability
        # Format JSON with 2 spaces of indentation
        json_data = json.dumps(data, indent=2)
        
        # Format the data part to be more readable in the curl command
        # Replace newlines with newline + spaces for proper shell script formatting
        formatted_data = json_data.replace('\n', '\n  ')
        
        # Add the data part to the curl command
        curl_command.append(f"--data '{formatted_data}'")
        
        return " \\\n  ".join(curl_command)
    
    def save_curl_commands(self, commands: List[str], output_path: str) -> None:
        """
        Save curl commands to a file
        
        Args:
            commands: List of curl commands
            output_path: Path to save the commands
            
        Raises:
            IOError: If unable to write to the file
        """
        if not commands:
            logger.warning("No commands to save")
            return
            
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            logger.info(f"Saving curl commands to: {output_path}")
            with open(output_path, 'w') as f:
                # Add shebang and header
                f.write("#!/bin/bash\n")
                f.write("# Generated API calls\n\n")
                
                # Add each command with a separator
                for i, command in enumerate(commands):
                    f.write(f"# API Call {i+1}\n")
                    f.write(f"{command}\n\n")
                    
            # Make the file executable
            os.chmod(output_path, 0o755)
            
            logger.info(f"Successfully saved {len(commands)} curl commands to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving curl commands to file: {e}")
            raise IOError(f"Failed to save curl commands to file: {e}")


if __name__ == "__main__":
    # Example usage
    generator = CURLGenerator(
        api_endpoint="https://api.example.com/endpoint",
        username="user",
        password="pass"
    )
    
    # Example data
    example_data = {
        "Document": [
            {
                "applicationName": "ENGINE",
                "formName": "ENGINE_FIELD_SETTINGS",
                "phase": "",
                "locale": "en",
                "Fields": [
                    {
                        "fieldName": "ENGINE_FIELD_NAME",
                        "Values": ["FIELD_VALUE"]
                    }
                ]
            }
        ]
    }
    
    try:
        # Generate curl commands
        commands = generator.generate_curl_commands(example_data)
        
        # Print the first command
        if commands:
            print("Generated CURL command:")
            print(commands[0])
            
    except Exception as e:
        print(f"Error: {e}")
