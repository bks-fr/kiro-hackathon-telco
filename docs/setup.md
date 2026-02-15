# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the AI-Powered Customer Support System MVP.

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 2GB RAM minimum
- **Disk Space**: 500MB for dependencies
- **Network**: Internet connection for AWS Bedrock API

## AWS Prerequisites

### 1. AWS Account Setup

1. Create an AWS account at https://aws.amazon.com if you don't have one
2. Note your AWS Account ID

### 2. Enable Bedrock Access

1. Log in to AWS Console
2. Navigate to Amazon Bedrock service
3. Go to "Model access" in the left sidebar
4. Click "Manage model access"
5. Select "Anthropic" and check "Claude Sonnet 4.5"
6. Click "Request model access"
7. Wait for approval (usually instant)

### 3. Create IAM User (Recommended)

For security, create a dedicated IAM user:

1. Go to IAM → Users → Add user
2. User name: `bedrock-ticket-routing`
3. Access type: Programmatic access
4. Attach policy: `AmazonBedrockFullAccess`
5. Save the Access Key ID and Secret Access Key

## Installation Steps

### Step 1: Clone or Download Project

```bash
# If using git
git clone <repository-url>
cd ticket-routing-mvp

# Or download and extract ZIP file
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected packages:
- strands-agents (Agent framework)
- boto3 (AWS SDK)
- python-dotenv (Environment variables)
- pydantic (Data validation)

### Step 4: Configure AWS Credentials

Choose one of these methods:

#### Method 1: AWS CLI (Recommended)

```bash
# Install AWS CLI if not already installed
# macOS: brew install awscli
# Linux: sudo apt-get install awscli
# Windows: Download from AWS website

# Configure credentials
aws configure
```

Enter when prompted:
- AWS Access Key ID: `<your-access-key>`
- AWS Secret Access Key: `<your-secret-key>`
- Default region name: `us-east-1`
- Default output format: `json`

#### Method 2: Environment Variables

**macOS/Linux:**
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1
```

**Windows:**
```cmd
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_key_here
set AWS_REGION=us-east-1
```

#### Method 3: .env File

```bash
cp .env.example .env
```

Edit `.env`:
```
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-v2
```

Note: AWS credentials should still be configured via AWS CLI or environment variables.

### Step 5: Verify Installation

Test your setup:

```bash
# Check Python version
python --version  # Should be 3.9+

# Check installed packages
pip list | grep strands-agents
pip list | grep boto3
pip list | grep pydantic

# Test AWS credentials
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/bedrock-ticket-routing"
}
```

## Configuration

### Bedrock Region Selection

Claude Sonnet 4.5 is available in these regions:
- `us-east-1` (US East - N. Virginia) - Recommended
- `us-west-2` (US West - Oregon)
- `eu-west-1` (Europe - Ireland)
- `ap-southeast-1` (Asia Pacific - Singapore)

Edit `src/config.py` to change region:
```python
BEDROCK_REGION = 'us-west-2'  # Change as needed
```

### Agent Configuration

Customize agent behavior in `src/config.py`:

```python
AGENT_CONFIG = {
    'temperature': 0.1,      # Lower = more consistent (0.0-1.0)
    'max_tokens': 4096,      # Maximum response length
    'max_iterations': 10,    # Maximum tool calls per ticket
    'timeout_seconds': 30    # Request timeout
}
```

### Confidence Threshold

Adjust when tickets are flagged for manual review:

```python
CONFIDENCE_THRESHOLD = 0.7  # 70% confidence minimum
```

## Testing Your Setup

### Quick Test

```bash
python -c "from src.models import Ticket; print('Models loaded successfully')"
python -c "import boto3; print('Boto3 loaded successfully')"
```

### Full Test (After Implementation)

```bash
python src/main.py
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'strands'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "NoCredentialsError: Unable to locate credentials"

**Solution:**
```bash
# Configure AWS credentials
aws configure

# Or check environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### Issue: "AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel"

**Solution:**
1. Ensure Bedrock model access is enabled (see AWS Prerequisites)
2. Check IAM user has `AmazonBedrockFullAccess` policy
3. Wait a few minutes after requesting model access

### Issue: "ValidationException: The model ID is invalid"

**Solution:**
- Verify model ID in `src/config.py` matches available models
- Check model availability in your region
- Try: `anthropic.claude-sonnet-4-5-v2`

### Issue: Python version too old

**Solution:**
```bash
# Check version
python --version

# Install Python 3.9+ from python.org
# Or use pyenv:
pyenv install 3.11
pyenv local 3.11
```

## Development Setup

### Install Development Dependencies

```bash
pip install pytest pytest-cov black flake8
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

## Next Steps

After successful setup:

1. Review `docs/README.md` for usage instructions
2. Examine `mock_data.py` to understand sample data
3. Run the application: `python src/main.py`
4. Review results in `results/routing_decisions.json`
5. Customize configuration as needed

## Getting Help

- **AWS Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **Strands Framework**: Check package documentation
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Python boto3**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
