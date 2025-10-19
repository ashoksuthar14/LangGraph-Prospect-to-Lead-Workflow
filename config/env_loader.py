"""
Environment configuration loader for the Prospect to Lead Workflow.
Handles loading and validation of environment variables.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


def load_environment() -> Dict[str, Any]:
    """
    Load environment variables from .env file.
    
    Returns:
        Dictionary containing environment configuration
    """
    # Load .env file
    load_dotenv()
    
    # API Keys
    api_keys = {
        'CLAY_API_KEY': os.getenv('CLAY_API_KEY'),
        'APOLLO_API_KEY': os.getenv('APOLLO_API_KEY'), 
        'EXPLORIUM_API_KEY': os.getenv('EXPLORIUM_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY'),
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'GOOGLE_CREDENTIALS_PATH': os.getenv('GOOGLE_CREDENTIALS_PATH')
    }
    
    # Configuration settings
    config = {
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
        'ENABLE_MOCK_APIS': os.getenv('ENABLE_MOCK_APIS', 'false').lower() == 'true',
        'ENABLE_EMAIL_SENDING': os.getenv('ENABLE_EMAIL_SENDING', 'false').lower() == 'true',
        'ENABLE_DETAILED_LOGGING': os.getenv('ENABLE_DETAILED_LOGGING', 'true').lower() == 'true',
        'DEFAULT_BATCH_SIZE': int(os.getenv('DEFAULT_BATCH_SIZE', '50')),
        'DEFAULT_DELAY_BETWEEN_SENDS': int(os.getenv('DEFAULT_DELAY_BETWEEN_SENDS', '5'))
    }
    
    return {
        'api_keys': api_keys,
        'config': config
    }


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate which API keys are available.
    
    Returns:
        Dictionary showing which API keys are configured
    """
    env = load_environment()
    api_keys = env['api_keys']
    
    validation = {}
    for key, value in api_keys.items():
        validation[key] = bool(value and value != f'your_{key.lower()}_here' and not value.startswith('your_'))
    
    return validation


if __name__ == "__main__":
    # Test environment loading
    env = load_environment()
    validation = validate_api_keys()
    
    print("Environment Configuration:")
    print(f"Environment: {env['config']['ENVIRONMENT']}")
    print(f"Mock APIs: {env['config']['ENABLE_MOCK_APIS']}")
    print(f"Email Sending: {env['config']['ENABLE_EMAIL_SENDING']}")
    
    print("\nAPI Key Status:")
    for key, is_valid in validation.items():
        status = "✓ Configured" if is_valid else "✗ Missing/Invalid"
        print(f"{key}: {status}")