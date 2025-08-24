from .server import serve


def main():
    """MCP Software Company Server - MetaGPT integration for MCP"""
    import asyncio
    asyncio.run(serve())


if __name__ == "__main__":
    main()
