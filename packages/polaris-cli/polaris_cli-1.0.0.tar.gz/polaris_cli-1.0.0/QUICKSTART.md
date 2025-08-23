# Polaris CLI - Quick Start Guide

Get up and running with the Polaris CLI in minutes!

## 🚀 Installation

### Option 1: Development Setup (Recommended)
```bash
# Clone or navigate to the project
cd polaris-cli

# Run setup script
python setup.py

# Verify installation
poetry run polaris --help
```

### Option 2: Direct Run
```bash
# Install dependencies manually
pip install typer rich rich-click pydantic httpx keyring tabulate python-dateutil pyfiglet colorama alive-progress

# Run directly
python run.py --help
```

## 🔐 Authentication

### Login with Sample Token
```bash
# Use one of the sample tokens
polaris auth login --api-key pk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0

# Check status
polaris auth status
```

### Available Sample Tokens
- **Production**: `pk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`
- **Staging**: `pk_stg_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0`
- **Development**: `pk_dev_f6e5d4c3b2a1z0y9x8w7v6u5t4s3r2q1p0o9n8m7`
- **Testing**: `pk_test_9i8h7g6f5e4d3c2b1a0z9y8x7w6v5u4t3s2r1q0p`

## 🎯 Essential Commands

### View the Banner
```bash
polaris --banner
```

### Resource Discovery
```bash
# List all resources
polaris resources list

# Find NVIDIA GPUs with 24GB+ memory
polaris resources gpu-list --provider nvidia --memory 24gb+

# Compare GPU models
polaris resources gpu-compare rtx4090 a100

# Search for resources
polaris resources search "machine learning gpu"
```

### Instance Management
```bash
# List instances
polaris instances list

# Create instance
polaris instances create my-workload --machine-type gpu-nvidia-a100-80gb

# Get instance details
polaris instances get inst_001

# Start/stop instances
polaris instances start inst_001
polaris instances stop inst_001
```

### Billing & Monitoring
```bash
# Billing overview
polaris billing overview

# System status
polaris status overview

# Usage details
polaris billing usage
```

### Configuration
```bash
# Show config
polaris config show

# Update settings
polaris config set default_region us-west-1
polaris config set output_format json
```

## 🎬 Run the Demo

```bash
# Run complete demo
python examples/demo.py

# Or run individual demo steps
polaris auth login --api-key pk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
polaris resources list --type gpu
polaris instances create demo-workload
polaris billing overview
```

## 📁 Project Structure

```
polaris-cli/
├── polaris_cli/           # Main CLI package
│   ├── auth/             # Authentication system
│   ├── commands/         # Command modules
│   ├── config/           # Configuration management
│   ├── data/             # Dummy data layer
│   ├── ui/               # Beautiful UI components
│   └── utils/            # Utilities and helpers
├── examples/             # Demo scripts and samples
├── README.md            # Full documentation
├── QUICKSTART.md        # This file
└── pyproject.toml       # Package configuration
```

## 🔧 Development

### Adding New Commands
1. Create command module in `polaris_cli/commands/`
2. Import in `polaris_cli/main.py`
3. Add dummy data in `polaris_cli/data/dummy_data.py`

### Customizing UI
- Modify `polaris_cli/ui/banner.py` for branding
- Update `polaris_cli/ui/tables.py` for table formatting
- Customize colors and styles throughout

### Adding Data
- Add new dummy data in `polaris_cli/data/dummy_data.py`
- Update search and filter functions
- Add new data types as needed

## 💡 Tips

1. **Use Tab Completion**: Enable with `argcomplete` (auto-detected)
2. **JSON Output**: Add `--output json` to most commands
3. **Help System**: Use `--help` on any command for detailed info
4. **Profiles**: Set up multiple authentication profiles for different environments
5. **Configuration**: Customize defaults with `polaris config set`

## 🐛 Troubleshooting

### Common Issues

**"Command not found"**
- Use `poetry run polaris` or `python run.py`
- Ensure Python 3.9+ is installed

**"Authentication required"**
- Run `polaris auth login --api-key <token>`
- Check status with `polaris auth status`

**"Module not found"**
- Install dependencies: `poetry install` or `pip install -r requirements.txt`
- Check Python path includes project directory

## 🌟 Features

✅ **Token-based Authentication** - Secure API key management
✅ **Beautiful Terminal UI** - Rich formatting and animations  
✅ **Resource Discovery** - Find and compare cloud resources
✅ **Instance Management** - Full lifecycle control
✅ **Cluster Operations** - Multi-node deployments
✅ **Cost Tracking** - Billing and usage monitoring
✅ **Configuration System** - Customizable settings
✅ **Dummy Data Layer** - Realistic test data
✅ **Profile Management** - Multiple environment support

---

**Ready to explore?** Start with `polaris --banner` and dive into the cloud! 🚀
