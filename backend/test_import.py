#!/usr/bin/env python3

import sys
import traceback

logger.info("Testing imports...")

try:
    logger.info("1. Importing basic modules...")
    import asyncio
    import logging
    import time
    from typing import Dict, List, Optional, Any, Callable, Awaitable
    from urllib.parse import quote
    logger.info("   ✓ Basic modules imported")
    
    logger.info("2. Importing httpx...")
    import httpx
    logger.info("   ✓ httpx imported")
    
    logger.info("3. Importing app schemas...")
    from app.schemas.library import LibraryMetadata, Dependency
    logger.info("   ✓ Schemas imported")
    
    logger.info("4. Importing app models...")
    from app.models.library import RegistryType
    logger.info("   ✓ Models imported")
    
    logger.info("5. Importing metadata fetcher module...")
    import app.services.library_management.metadata_fetcher as mf
    logger.info("   ✓ Module imported")
    logger.info("   Available attributes: {[attr for attr in dir(mf) if not attr.startswith('_')]}")
    
    logger.info("6. Trying to import specific classes...")
    try:
        from app.services.library_management.metadata_fetcher import MetadataFetchError
        logger.info("   ✓ MetadataFetchError imported")
    except Exception as e:
        logger.info("   ✗ MetadataFetchError failed: {e}")
    
    try:
        from app.services.library_management.metadata_fetcher import AsyncCircuitBreaker
        logger.info("   ✓ AsyncCircuitBreaker imported")
    except Exception as e:
        logger.info("   ✗ AsyncCircuitBreaker failed: {e}")
    
    try:
        from app.services.library_management.metadata_fetcher import MetadataFetcher
        logger.info("   ✓ MetadataFetcher imported")
    except Exception as e:
        logger.info("   ✗ MetadataFetcher failed: {e}")
        
except Exception as e:
    logger.info("Error during import: {e}")
    traceback.print_exc()