#!/usr/bin/env python3
"""
Startup script for FamilySearch Web Search MCP Server
"""
import os
import sys
import asyncio
import structlog
from config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def main():
    """Start the FamilySearch Web Search MCP Server"""
    try:
        logger.info("Starting FamilySearch Web Search MCP Server", 
                   server_name=settings.server_name,
                   server_url=settings.server_url,
                   port=settings.server_port)
        
        # Import and run the server
        from server import proxy
        
        logger.info("Server initialized successfully")
        logger.info("Available tools:", 
                   tools=["search_familysearch_records", "search_census_records", "search_vital_records"])
        
        # Run the server
        proxy.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Failed to start server", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()