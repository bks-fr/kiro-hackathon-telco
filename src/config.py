"""
Configuration settings for AI-Powered Customer Support System MVP.

Contains Bedrock configuration, agent settings, and system constants.
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Tuple

from .models import Team, PriorityLevel


# Bedrock Configuration
BEDROCK_REGION = 'eu-central-1'
# Using global inference profile for Claude Haiku 4.5 (works across all regions)
BEDROCK_MODEL_ID = 'global.anthropic.claude-haiku-4-5-20251001-v1:0'

# Agent Configuration
AGENT_CONFIG = {
    'temperature': 0.1,
    'max_tokens': 4096,
    'max_iterations': 10,
    'timeout_seconds': 30
}

# Confidence Threshold
CONFIDENCE_THRESHOLD = 0.7

# Agent Tools Configuration
# Set to True to use AI-powered tools (Claude Haiku), False to use mock tools
USE_AGENT_TOOLS = os.environ.get('USE_AGENT_TOOLS', 'false').lower() == 'true'

# Teams (from enum)
TEAMS = [team.value for team in Team]

# Priority Levels (from enum)
PRIORITY_LEVELS = [level.value for level in PriorityLevel]

# Priority Score Thresholds
PRIORITY_THRESHOLDS = {
    'P0': 80,
    'P1': 60,
    'P2': 40,
    'P3': 0
}


def validate_aws_credentials() -> Tuple[bool, str]:
    """
    Validate that AWS credentials are configured.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Try to create a boto3 session and get credentials
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            return False, "AWS credentials not found. Please configure credentials using 'aws configure' or environment variables."
        
        # Check if credentials are frozen (available)
        frozen_credentials = credentials.get_frozen_credentials()
        if not frozen_credentials.access_key:
            return False, "AWS access key not found in credentials."
        
        return True, ""
        
    except NoCredentialsError:
        return False, "AWS credentials not found. Please configure credentials using 'aws configure' or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
    
    except PartialCredentialsError as e:
        return False, f"Incomplete AWS credentials: {str(e)}"
    
    except Exception as e:
        return False, f"Error validating AWS credentials: {str(e)}"


def validate_bedrock_region() -> Tuple[bool, str]:
    """
    Check Bedrock region availability.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # List of regions where Bedrock is available
        bedrock_regions = [
            'us-east-1', 'us-west-2', 'eu-central-1', 'eu-west-1', 
            'eu-west-2', 'eu-west-3', 'ap-southeast-1', 'ap-southeast-2',
            'ap-northeast-1', 'ca-central-1', 'sa-east-1'
        ]
        
        if BEDROCK_REGION not in bedrock_regions:
            return False, f"Region '{BEDROCK_REGION}' may not support Bedrock. Supported regions: {', '.join(bedrock_regions)}"
        
        # Try to create a Bedrock client to verify access
        try:
            client = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
            # We don't make an actual API call here to avoid costs
            return True, ""
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'AccessDeniedException':
                return False, f"Access denied to Bedrock in region '{BEDROCK_REGION}'. Please enable Bedrock access in your AWS account."
            return False, f"Error accessing Bedrock in region '{BEDROCK_REGION}': {str(e)}"
        
    except Exception as e:
        return False, f"Error validating Bedrock region: {str(e)}"


def validate_environment_variables() -> Tuple[bool, str]:
    """
    Verify required environment variables.
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check for AWS credentials in environment variables (optional, can also use ~/.aws/credentials)
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # If environment variables are set, validate they're not empty
    if aws_access_key is not None and not aws_access_key.strip():
        return False, "AWS_ACCESS_KEY_ID environment variable is set but empty."
    
    if aws_secret_key is not None and not aws_secret_key.strip():
        return False, "AWS_SECRET_ACCESS_KEY environment variable is set but empty."
    
    # Check for optional AWS_REGION override
    aws_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    if aws_region and aws_region != BEDROCK_REGION:
        print(f"⚠️  Warning: AWS_REGION environment variable ('{aws_region}') differs from configured BEDROCK_REGION ('{BEDROCK_REGION}'). Using BEDROCK_REGION.")
    
    return True, ""


def validate_configuration() -> Tuple[bool, list]:
    """
    Validate all configuration settings.
    
    Returns:
        Tuple[bool, list]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate AWS credentials
    creds_valid, creds_error = validate_aws_credentials()
    if not creds_valid:
        errors.append(f"AWS Credentials: {creds_error}")
    
    # Validate Bedrock region
    region_valid, region_error = validate_bedrock_region()
    if not region_valid:
        errors.append(f"Bedrock Region: {region_error}")
    
    # Validate environment variables
    env_valid, env_error = validate_environment_variables()
    if not env_valid:
        errors.append(f"Environment Variables: {env_error}")
    
    is_valid = len(errors) == 0
    return is_valid, errors
