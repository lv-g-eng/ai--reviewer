#!/usr/bin/env python3

import sys
import traceback

print("Testing imports...")

try:
    print("1. Importing basic modules...")
    import asyncio
    import logging
    import time
    from typing import Dict, List, Optional, Any, Callable, Awaitable
    from urllib.parse import quote
    print("   ✓ Basic modules imported")
    
    print("2. Importing httpx...")
    import httpx
    print("   ✓ httpx imported")
    
    print("3. Importing app schemas...")
    from app.schemas.library import LibraryMetadata, Dependency
    print("   ✓ Schemas imported")
    
    print("4. Importing app models...")
    from app.models.library import RegistryType
    print("   ✓ Models imported")
    
    print("5. Importing metadata fetcher module...")
    import app.services.library_management.metadata_fetcher as mf
    print("   ✓ Module imported")
    print(f"   Available attributes: {[attr for attr in dir(mf) if not attr.startswith('_')]}")
    
    print("6. Trying to import specific classes...")
    try:
        from app.services.library_management.metadata_fetcher import MetadataFetchError
        print("   ✓ MetadataFetchError imported")
    except Exception as e:
        print(f"   ✗ MetadataFetchError failed: {e}")
    
    try:
        from app.services.library_management.metadata_fetcher import AsyncCircuitBreaker
        print("   ✓ AsyncCircuitBreaker imported")
    except Exception as e:
        print(f"   ✗ AsyncCircuitBreaker failed: {e}")
    
    try:
        from app.services.library_management.metadata_fetcher import MetadataFetcher
        print("   ✓ MetadataFetcher imported")
    except Exception as e:
        print(f"   ✗ MetadataFetcher failed: {e}")
        
except Exception as e:
    print(f"Error during import: {e}")
    traceback.print_exc()