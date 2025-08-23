#!/bin/bash
cd "$(dirname "$0")"
exec uv run bitbucket_mcp_server.py
