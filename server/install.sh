#!/bin/bash

# Weather MCP Server Installation Script
# This script helps resolve dependency conflicts and install the server

set -e

echo "🚀 Installing Weather MCP Server with Dify authorization support..."

# Check if Python 3.12+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.12 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Clean existing packages to avoid conflicts
echo "🧹 Cleaning existing packages..."
pip uninstall -y fastapi httpx mcp uvicorn anyio 2>/dev/null || true

# Install anyio first to resolve version conflicts
echo "📦 Installing anyio..."
pip install "anyio>=4.5"

# Install dependencies with correct versions
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install "mcp>=1.9.0" "fastapi>=0.115.0" "httpx>=0.28.0,<0.29.0" "uvicorn>=0.27.0" "python-dotenv>=1.0.0"
fi

# Verify installation
echo "✅ Verifying installation..."
python -c "
import fastapi
import httpx
import mcp
import uvicorn
import anyio
print(f'✅ FastAPI: {fastapi.__version__}')
print(f'✅ httpx: {httpx.__version__}')
print(f'✅ MCP: {mcp.__version__}')
print(f'✅ uvicorn: {uvicorn.__version__}')
print(f'✅ anyio: {anyio.__version__}')
"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    if [ -f "dify_config_example.env" ]; then
        cp dify_config_example.env .env
        echo "⚠️  Please edit .env file and set your DIFY_API_KEY"
    else
        echo "DIFY_API_KEY=your_api_key_here" > .env
        echo "⚠️  Please edit .env file and set your DIFY_API_KEY"
    fi
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and set your DIFY_API_KEY"
echo "2. Run the server: python weather.py"
echo "3. For development: python weather.py --no-auth"
echo ""
echo "📚 For more information, see DIFY_MCP_SETUP.md"
echo ""
echo "🔧 To activate the virtual environment in the future:"
echo "   source venv/bin/activate"
