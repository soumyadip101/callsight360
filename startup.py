#!/usr/bin/env python3
"""
Startup script for CallSight360 Azure App Service deployment
This script serves as the entry point for the Azure Python web app
"""

import os
import sys
import logging

# Configure logging for Azure
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

logger.info("Python path configured for Azure App Service")
logger.info(f"Backend path: {backend_path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")

# Set environment variables for Azure
os.environ.setdefault('PYTHONPATH', os.path.dirname(__file__))
os.environ.setdefault('PYTHONUNBUFFERED', '1')

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import fastapi
        logger.info(f"FastAPI version: {fastapi.__version__}")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
        logger.info(f"Uvicorn version: {uvicorn.__version__}")
    except ImportError:
        missing_deps.append("uvicorn")
    
    if missing_deps:
        logger.error(f"Missing required dependencies: {missing_deps}")
        logger.error("Try installing with: pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    try:
        # Check dependencies first
        if not check_dependencies():
            logger.error("Dependency check failed. Attempting to continue...")
        
        import uvicorn
        from backend.app.main import app
        
        # Get port from Azure environment variable
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"Starting CallSight360 on port {port}")
        logger.info("Application ready to serve requests")
        
        # Start the application
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True,
            # Add timeout settings for Azure
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("This usually means dependencies are not installed properly")
        logger.error("Check the deployment logs and requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1) 