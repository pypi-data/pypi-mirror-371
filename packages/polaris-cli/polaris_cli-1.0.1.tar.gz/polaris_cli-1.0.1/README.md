# 🚀 Polaris CLI

A beautiful and powerful command-line interface for cloud resource management with a stunning terminal UI, smart resource discovery, and streamlined instance deployment.

[![PyPI version](https://badge.fury.io/py/polaris-cli.svg)](https://badge.fury.io/py/polaris-cli)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**🎉 Now available on PyPI! Install with:** `pip install polaris-cli`

## 🏃‍♀️ Get Started in 30 seconds

```bash
# Install
pip install polaris-cli

# Verify installation
polaris --help

# Login 
polaris auth login --api-key pk_admin_your_key_here

# List resources
polaris resources list

# Create instance
polaris instances create my-instance --resource-id comp_001 --template-id pytorch-training
```

## ✨ Features

- **🔐 Token-based Authentication** - Secure API key management with multi-profile support
- **🖥️ Smart Resource Discovery** - Find and filter GPU/CPU resources by provider, specs, and availability  
- **📋 Rich Template System** - Pre-configured environments for ML, development, and production
- **⚡ Instance Management** - Complete lifecycle management with resource validation
- **🎨 Beautiful Interface** - Rich terminal UI with animations, loading spinners, and formatted tables
- **🔍 Advanced Filtering** - Search resources by type, memory, region, and availability
- **📊 Requirement Validation** - Smart template matching with resource compatibility checks

## 📦 Installation

### Quick Install from PyPI (Recommended)

Install Polaris CLI directly from PyPI:

```bash
pip install polaris-cli
```

**Verify installation:**

```bash
polaris --help
```

You should see the Polaris CLI help screen with all available commands. That's it! The `polaris` command is now available globally.

### Development Installation (For Contributors)

If you want to contribute or modify the CLI:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bigideaafrica/polariscloud-cli
   cd polaris-cli
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv polaris-env
   
   # Windows
   .\polaris-env\Scripts\activate
   
   # Linux/macOS
   source polaris-env/bin/activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .
   ```

## 🚀 Quick Start

After installing with `pip install polaris-cli`:

```bash
# 1. Verify installation
polaris --help

# 2. Login with your API token
polaris auth login --api-key pk_admin_your_api_key_here

# 3. Browse available resources
polaris resources list

# 4. Check available templates  
polaris templates list

# 5. Create instance with resource ID and template
polaris instances create my-training \
  --resource-id comp_001 \
  --template-id pytorch-training

# 6. Check instance status
polaris instances get inst_my_training
```

## 🔐 Authentication

Polaris CLI uses API tokens for secure authentication:

```bash
# Login with API key
polaris auth login --api-key pk_prod_your_sample_token_here

# Check authentication status  
polaris auth status

# Logout when done
polaris auth logout
```

## 🗂️ Command Structure

```
polaris [command] [subcommand] [options]
```

**Available Commands:**
- `auth` - Authentication and session management
- `resources` - Resource discovery and filtering
- `instances` - Instance lifecycle management  
- `templates` - Template browsing and management
- `ssh` - SSH key management and connections
- `status` - System status and monitoring
- `billing` - Usage and billing information
- `config` - Configuration management

Use `polaris [command] --help` for detailed usage information.

## ⚙️ Configuration

Configuration is stored in `~/.polaris/config.json` with secure token management:

```bash
# View current configuration
polaris config show

# Set configuration values
polaris config set default_region us-west-1
polaris config set output_format table

# Reset configuration
polaris config reset
```

## 📚 Examples

### Resource Discovery
```bash
# List all available resources
polaris resources list

# Filter GPU resources by provider  
polaris resources gpu-list --provider nvidia

# Filter by memory requirements
polaris resources gpu-list --memory 24gb+

# Search with natural language
polaris resources search "nvidia gpu 24gb singapore"

# Show only available resources
polaris resources list --available-only
```

### Template Management
```bash
# Browse all templates
polaris templates list

# Filter templates by category
polaris templates list --category "Machine Learning"

# Search for specific templates
polaris templates list --search pytorch

# Get detailed template information
polaris templates get pytorch-training
```

### Instance Creation (Step-by-Step)
```bash
# 1. Find an available resource
polaris resources list --available-only

# 2. Choose a template
polaris templates list

# 3. Create instance with both resource ID and template ID
polaris instances create my-training \
  --resource-id comp_001 \
  --template-id pytorch-training \
  --disk-size 100

# 4. Check instance details
polaris instances get inst_my_training

# 5. Connect to instance
polaris ssh connect inst_my_training
```

### Advanced Usage
```bash
# Get help for creating instances
polaris instances create-help

# List running instances
polaris instances list --status running

# Monitor system status
polaris status overview

# View billing information
polaris billing overview
```

## 📋 Available Templates

Our CLI includes pre-configured templates for various use cases:

| Template ID | Category | Description | Requirements |
|-------------|----------|-------------|--------------|
| `pytorch-training` | Machine Learning | PyTorch with CUDA support | GPU: 8GB, RAM: 8GB |
| `tensorflow-jupyter` | Machine Learning | TensorFlow + Jupyter Lab | CPU+GPU, RAM: 4GB |
| `stable-diffusion` | AI Art | Automatic1111 WebUI | GPU Required, RAM: 16GB |
| `fastapi-serve` | Deployment | FastAPI inference server | CPU Only, RAM: 2GB |
| `vscode-remote` | Development | VS Code remote environment | CPU Only, RAM: 2GB |
| `ubuntu-desktop` | OS | Full Ubuntu desktop via VNC | CPU+GPU, RAM: 4GB |
| `jupyter-datascience` | Data Science | Complete data science stack | CPU+GPU, RAM: 4GB |

## 🛠️ Features Highlights

### Smart Resource Filtering
- **GPU Provider Filtering**: `--provider nvidia` or `--provider amd`
- **Memory Requirements**: `--memory 24gb+` or `--memory 8gb-32gb`  
- **Availability Status**: `--available-only` shows only free resources
- **Resource IDs**: Clear identifiers like `comp_001`, `comp_002`

### Rich Terminal UI
- **Loading Spinners**: Beautiful animations during API calls
- **Formatted Tables**: Clean, readable resource and template listings
- **Error Handling**: Clear error messages with helpful suggestions
- **Authentication Required**: Secure API access with token validation

### Template System
- **Requirement Validation**: Automatic compatibility checking
- **Resource Requirements**: Clear RAM, storage, and GPU requirements
- **Clickable Docker Links**: Direct access to Docker Hub repositories
- **Category Organization**: OS, Development, Machine Learning, etc.

## 🚨 Troubleshooting

### Common Issues

**Authentication Error:**
```bash
❌ Authentication required!
Please login first: polaris auth login
```
Solution: Run `polaris auth login --api-key YOUR_TOKEN`

**Resource Not Found:**
```bash
❌ Resource 'comp_999' not found!
💡 List available resources: polaris resources list
```
Solution: Use `polaris resources list` to find valid resource IDs

**Resource In Use:**
```bash
❌ Resource 'comp_001' is currently in use!
💡 Find available resources: polaris resources list --available-only
```
Solution: Choose a different resource or wait for it to become available

**Template Not Found:**
```bash
❌ Template 'invalid-template' not found!
💡 List available templates: polaris templates list  
```
Solution: Use `polaris templates list` to find valid template IDs

### Getting Help
```bash
# General help
polaris --help

# Command-specific help
polaris instances --help
polaris instances create --help

# Step-by-step instance creation guide
polaris instances create-help
```

### Dependencies
- **typer**: CLI framework
- **rich**: Beautiful terminal output
- **httpx**: HTTP client for API calls
- **keyring**: Secure token storage
- **pydantic**: Data validation

## 📄 License

MIT License - see LICENSE file for details.
