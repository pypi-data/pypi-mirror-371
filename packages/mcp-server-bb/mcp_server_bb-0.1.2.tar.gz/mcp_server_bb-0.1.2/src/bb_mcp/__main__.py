from .bb_mcp import mcp, BB_BASE_URL

def main():
    print("BB_BASE_URL: ", BB_BASE_URL)
    print("Starting BB MCP server...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()