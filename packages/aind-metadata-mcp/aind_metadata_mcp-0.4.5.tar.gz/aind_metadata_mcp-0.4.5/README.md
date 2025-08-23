# AIND Metadata access MCP server

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-94.1%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)
![Python](https://img.shields.io/badge/python->=3.11-blue?logo=python)

## Server Overview

The AIND metadata MCP allows users to access and communicate with the metadata within their preferred IDE. This server consists of tools that allows an LLM agent to access records in DocDB, as well as provide the user context with how the AIND Data Schema is structured. It also consists of resources to give the model additional context on how to structure responses using the `aind-data-access` API, as well as, how the schema is structured. Note that due to the nature of MCP servers, users will have to explicitly ask the agent to use the available resources for additional context.

## Setting up your desktop for installing MCP servers

1. Downloading UV to your desktop
   ( Unsure about the necessity of this step but it definitely helps having the package configured locally)

- on Mac Terminal

```bash
brew install uv

# Or, alternatively:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- on Windows Powershell

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

In order to ensure that the MCP server runs in your preferred client, you will have to download the `aind-metadata-mcp` package to your console. However, note that the installation is quite large. If space is an issue, please set `UV_CACHE_DIR` and `UV_TOOL_DIR` to locations that have capacity before proceeding with the next step.

1. Simpler version of install
   Run `uv tool install aind-metadata-mcp` on your terminal and proceed below to configuring your MCP clients. The `uvx` command should ideally take 3 minutes to start up without errors.
2. If the above step didn't work:

Create virtual environment with python 3.11 in IDE

```bash
# Instructions for Conda
conda create -n <my_env> python=3.11
conda activate <my_env>

# Instructions for virtual environment
py -3.11 -m venv .venv
# Windows startup
.venv\Scripts\Activate.ps1 
# Mac/ Linux startup
source .venv/bin/activate 
```

Run the following commands in your IDE terminal. The `uvx` command should ideally take 3 minutes to start up without errors.

```bash
pip install uv
uvx aind-metadata-mcp
```

If all goes well, and you see the following notice - `Starting MCP server 'aind_data_access' with transport 'stdio'`-, you should be good for the set up in your client of choice!

## Instructions for use in MCP clients

JSON Config files to add MCP servers in clients should be structured like this

```bash
{
    "mcpServers": {

    }
}
```

Insert the following lines into the mcpServers dictionary

```bash

"aind_data_access": {
    "command": "uvx",
    "args": ["aind-metadata-mcp"]
}

```

Note that after configuring the JSON files, it will take a few minutes for the serve to populate in the client.

### Claude Desktop App

- Click the three lines at the top left of the screen.
- File > Settings > Developer > Edit config

### Cline in VSCode

- Ensure that Cline is downloaded to VScode
- Click the three stacked rectangles at the top right of the Cline window
- Installed > Configure MCP Servers
- Close and reopen VSCode

### Github Copilot in VSCode

- Command palette (ctr shift p)
- Search for MCP: Add server
- Select `Manual Install` / `stdio`
- When prompted for a command, input `uvx aind-data-access`
- Name your server
- Close and reopen VSCode
- In Copilot chat -> Select agent mode -> Click the three stacked rectangles to configure tools
- In order to enable the agent to reply with context of the AIND API, you'll have to manually add the .txt files (under resources) in this repository

### For use in Code Ocean

* Locate the [following capsule](https://codeocean.allenneuraldynamics.org/capsule/7008682/tree), to spin up Cline and Co-pilot with the aind-metadata-mcp pre-installed.
* Refer the the [code ocean MCP server](https://github.com/codeocean/codeocean-mcp-server) for additional support
* Either pin version 4.2, or 4.4
