# ShipBoss MCP Server

An MCP server that provides shipping and logistics capabilities through AI conversations. Connect to FedEx, UPS, and DHL to get rates, create labels, track packages, and manage freight shipments.

> **🔑 Important**: You'll need a ShipBoss API token to use this server. Get one from your [ShipBoss Admin → API Integrations](https://ship.shipboss.io/customer-admin/api-integrations).

## 🚀 Quick Setup (5 Minutes)

### Prerequisites
- **Python 3.9+** installed
- **ShipBoss account** with API token (get one in the admin section at [ship.shipboss.io](https://ship.shipboss.io))

### Step-by-Step Installation

**Step 1: Get Your ShipBoss API Token** 🔑
This is required for the server to communicate with ShipBoss APIs.

1. Go to [ShipBoss](https://ship.shipboss.io) and log in
2. Navigate to your Admin section → [API Integrations](https://ship.shipboss.io/customer-admin/api-integrations)
3. Generate a new API token and copy it
4. **Keep this token secure** - you'll need it in the next step

**Step 2: Install the Package**
```bash
# Install from PyPI (recommended)
pip install shipboss-mcp-server

# Or install in a virtual environment
python -m venv shipboss_env

# Windows:
shipboss_env\Scripts\activate
# macOS/Linux:
source shipboss_env/bin/activate

pip install shipboss-mcp-server
```

**Step 3: Configure MCP Server** ⚙️
The server needs your API token to authenticate with ShipBoss. Choose one of these methods:

#### Option A: .env File (Simplest - Automatic) 📁
```bash
# Option 1: Create environment file manually
echo "SHIPBOSS_API_TOKEN=your_api_token_here" > .env

# Option 2: Use the provided template (copy and modify)
cp example.env .env  # Then edit .env with your actual token
```

Then use this simple configuration (the .env file will be loaded automatically):
```json
{
  "mcpServers": {
    "shipboss-mcp": {
      "command": "shipboss-mcp-server"
    }
  }
}
```

**Note**: Place the `.env` file in the working directory of your MCP client (e.g., Claude Desktop's working directory).

#### Option B: Command-Line Argument
Add this to your MCP client configuration:
```json
{
  "mcpServers": {
    "shipboss-mcp": {
      "command": "shipboss-mcp-server",
      "args": ["--api-token", "your_api_token_here"]
    }
  }
}
```

#### Option C: Environment Variable in Config
Use this configuration with the token in the env section:
```json
{
  "mcpServers": {
    "shipboss-mcp": {
      "command": "shipboss-mcp-server",
      "env": {
        "SHIPBOSS_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

**Step 4: Test Your Setup** 🧪
Restart your MCP client and try these commands:
- *"Get shipping rates from New York to Los Angeles for a 2lb package"*
- *"Create a FedEx Ground label from 123 Main St, New York, NY to 456 Oak Ave, Los Angeles, CA"*

**Quick verification**: Before restarting your MCP client, test the server directly:
```bash
# Test with your API token
shipboss-mcp-server --api-token your_actual_token_here
# Should start without "API token required" error
```

## Available Tools

- **ping** - Health check
- **get_parcel_rates** - Get parcel shipping rates
- **create_parcel_label** - Create parcel shipping labels with direct download URLs
- **track_parcel** - Track parcel shipments
- **create_pickup** - Schedule carrier pickups
- **cancel_pickup** - Cancel scheduled pickups
- **get_freight_rates** - Get freight shipping quotes
- **track_freight** - Track freight shipments

## Troubleshooting

### Common Issues:

1. **"API token required" error** 🔐: Make sure you have your API token configured using one of these methods:
   - **Easiest**: Create a `.env` file with `SHIPBOSS_API_TOKEN=your_token` (automatically loaded)
   - Add `--api-token your_token` to the args in your MCP config
   - Set `SHIPBOSS_API_TOKEN` in the env section of your MCP config
   - **Verify your token**: Make sure it's from [ShipBoss API Integrations](https://ship.shipboss.io/customer-admin/api-integrations)

2. **".env file not found"**: The `.env` file should be in your current working directory when running the `shipboss-mcp-server` command.
   - Check if the file exists: `ls -la .env`
   - Verify the token format: `cat .env` (should show `SHIPBOSS_API_TOKEN=your_token_here`)

3. **"Unexpected token" errors**: Make sure the package is properly installed with `pip install shipboss-mcp-server`.

4. **Command not found**: Ensure the package is installed and the `shipboss-mcp-server` command is available in your PATH.

5. **Permission errors**: The installed package should have proper permissions. Try running with `python -m shipboss_mcp_server` if the command fails.

### Debug Mode:
Run the server directly to test:
```bash
# Using the installed command:
shipboss-mcp-server --api-token your_token

# Or using python module:
python -m shipboss_mcp_server --api-token your_token
```
