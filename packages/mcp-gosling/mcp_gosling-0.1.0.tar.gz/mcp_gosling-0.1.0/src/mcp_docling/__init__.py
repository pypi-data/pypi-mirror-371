import argparse
from .server import mcp

def main():
    """MCP Docling Server: Advanced document processing using IBM's Docling library."""
    parser = argparse.ArgumentParser(
        description="MCP server providing document processing capabilities with Docling"
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
