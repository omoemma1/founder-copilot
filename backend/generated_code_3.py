# Import necessary libraries
import json
import os
from typing import Dict

# Define a class for WebsiteConfig
class WebsiteConfig:
    def __init__(self, config_file: str = 'website_config.json'):
        """
        Initialize the WebsiteConfig class.

        Args:
        - config_file (str): The path to the website configuration file. Defaults to 'website_config.json'.
        """
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """
        Load the website configuration from the JSON file.

        Returns:
        - Dict: The website configuration.
        """
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # If the file does not exist, create a default configuration
            return {
                'company_name': '',
                'color_scheme': {
                    'primary': '',
                    'secondary': ''
                },
                'services': []
            }
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            print(f"Error loading configuration: {e}")
            return {
                'company_name': '',
                'color_scheme': {
                    'primary': '',
                    'secondary': ''
                },
                'services': []
            }

    def update_config(self) -> None:
        """
        Update the website configuration.
        """
        # Update the company name
        self.config['company_name'] = 'FounderTech Solutions'

        # Update the color scheme
        self.config['color_scheme'] = {
            'primary': 'blue',
            'secondary': 'gold'
        }

        # Add a new service
        self.config['services'].append({
            'name': 'AI Development Services',
            'description': 'We offer custom AI development services to help you achieve your business goals.'
        })

        # Save the updated configuration
        self.save_config()

    def save_config(self) -> None:
        """
        Save the website configuration to the JSON file.
        """
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=4)
        except Exception as e:
            # Handle any errors during saving
            print(f"Error saving configuration: {e}")

    def print_config(self) -> None:
        """
        Print the current website configuration.
        """
        print(json.dumps(self.config, indent=4))

def main() -> None:
    """
    The main function.
    """
    website_config = WebsiteConfig()
    website_config.update_config()
    website_config.print_config()

if __name__ == "__main__":
    main()