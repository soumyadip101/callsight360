import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from datetime import datetime

from .api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CallSight360",
    description="""
    CallSight360 - Transform your call center calls into actionable insights.
    
    ## Key Features
    
    * **Smart Transcription**: Instantly convert call recordings into accurate text transcripts
    * **Call Intelligence**: Understand customer emotions, intent, and call outcomes automatically
    * **Agent Performance**: Measure call quality, satisfaction, and interaction patterns
    * **Call Insights**: Generate concise summaries and key findings
    * **Bulk Analysis**: Process hundreds of calls at once for comprehensive insights
    
    ## How It Works
    
    1. **Upload Calls**: Support for all common audio formats
    2. **Instant Analysis**: Local processing without cloud dependencies
    3. **Smart Insights**: Comprehensive call analysis using proven algorithms
    4. **Actionable Results**: Detailed metrics and recommendations for improvement
    
    ## Why Choose CallSight360?
    
    * ✅ **Secure & Private**: Your call data stays on your servers
    * ✅ **Lightning Fast**: Get insights in seconds, not hours
    * ✅ **Works Offline**: No internet dependency or cloud costs
    * ✅ **Always Accurate**: Consistent results you can trust
    """,
    version="2.0.0",
    contact={
        "name": "CallSight360",
        "email": "support@callsight360.com",
    },
)

# Add CORS middleware - Allow all origins for Azure deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Azure App Service handles HTTPS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["audio-analysis"])

# Serve static files (React build) - Azure deployment
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
if os.path.exists(static_dir):
    logger.info(f"Serving static files from: {static_dir}")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Serve React app for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all routes that don't start with /api or /docs"""
        # Skip API routes and docs
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve index.html for all frontend routes
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        else:
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head><title>CallSight360</title></head>
            <body>
                <h1>CallSight360 - Setup Required</h1>
                <p>Frontend build not found. Please run the build process.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
            </html>
            """)
else:
    logger.warning(f"Static directory not found: {static_dir}")
    
    # Fallback root endpoint when static files are not available
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with API documentation"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CallSight360 - Call Center Analytics</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
                .container { max-width: 1000px; margin: 0 auto; background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.2); min-height: 100vh; }
                .header { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 40px; text-align: center; }
                .content { padding: 40px; }
                h1 { margin: 0; font-size: 2.5em; font-weight: 700; }
                .subtitle { font-size: 1.2em; opacity: 0.9; margin-top: 10px; }
                h2 { color: #374151; margin-top: 40px; margin-bottom: 20px; font-size: 1.8em; border-bottom: 3px solid #4f46e5; padding-bottom: 10px; }
                .feature { background: #f8fafc; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #4f46e5; transition: transform 0.2s; }
                .feature:hover { transform: translateX(5px); }
                .endpoint { background: #ecfdf5; padding: 15px; margin: 10px 0; border-radius: 8px; font-family: 'Courier New', monospace; border: 1px solid #10b981; }
                .endpoint-method { color: #059669; font-weight: bold; }
                a { color: #4f46e5; text-decoration: none; font-weight: 500; }
                a:hover { text-decoration: underline; }
                .status { background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; }
                .workflow { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .workflow-step { background: white; border: 2px solid #e5e7eb; border-radius: 10px; padding: 20px; text-align: center; transition: all 0.3s; }
                .workflow-step:hover { border-color: #4f46e5; transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
                .workflow-number { background: #4f46e5; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: bold; font-size: 1.2em; }
                .benefits { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; margin: 20px 0; }
                .benefit { background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #0ea5e9; }
                .benefit-icon { color: #10b981; font-size: 1.2em; margin-right: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📞 CallSight360</h1>
                    <div class="subtitle">Transform Call Center Calls into Actionable Insights</div>
                    <div class="status" style="margin-top: 20px;">✅ API Online and Ready</div>
                </div>
                
                <div class="content">
                    <h2>🚀 How It Works</h2>
                    <div class="workflow">
                        <div class="workflow-step">
                            <div class="workflow-number">1</div>
                            <strong>Upload Calls</strong>
                            <p>Support for all common call recording formats</p>
                        </div>
                        <div class="workflow-step">
                            <div class="workflow-number">2</div>
                            <strong>Transcribe</strong>
                            <p>Convert call recordings into readable text instantly</p>
                        </div>
                        <div class="workflow-step">
                            <div class="workflow-number">3</div>
                            <strong>Analyze</strong>
                            <p>Understand customer emotions and call outcomes</p>
                        </div>
                        <div class="workflow-step">
                            <div class="workflow-number">4</div>
                            <strong>Insights</strong>
                            <p>Get actionable recommendations for improvement</p>
                        </div>
                    </div>

                    <h2>📊 Powerful Features</h2>
                    <div class="feature">
                        <strong>😊 Customer Satisfaction:</strong> Understand customer emotions and satisfaction levels throughout the call
                    </div>
                    <div class="feature">
                        <strong>🎯 Call Intelligence:</strong> Automatically identify call purposes and customer intent (billing, support, complaints, etc.)
                    </div>
                    <div class="feature">
                        <strong>📈 Agent Performance:</strong> Measure agent effectiveness, response quality, and customer interaction patterns
                    </div>
                    <div class="feature">
                        <strong>⭐ Call Outcomes:</strong> Track resolution rates, escalation risks, and overall call success metrics
                    </div>
                    <div class="feature">
                        <strong>📝 Smart Insights:</strong> Generate key findings, call summaries, and actionable recommendations
                    </div>

                    <h2>🔗 API Endpoints</h2>
                    <div class="endpoint">
                        <span class="endpoint-method">POST</span> /api/v1/upload-and-analyze - Complete workflow: upload, transcribe, and analyze
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method">POST</span> /api/v1/transcribe - Audio transcription only
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method">POST</span> /api/v1/analyze-transcript - Analyze existing transcript text
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method">POST</span> /api/v1/batch-analyze - Batch process multiple audio files
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method">GET</span> /api/v1/supported-formats - List supported audio formats
                    </div>
                    <div class="endpoint">
                        <span class="endpoint-method">GET</span> /api/v1/health - System health check
                    </div>

                    <h2>📚 Documentation</h2>
                    <p>
                        <a href="/docs">📖 Interactive API Documentation (Swagger UI)</a><br>
                        <a href="/redoc">📋 Alternative Documentation (ReDoc)</a>
                    </p>

                    <h2>💡 Quick Start</h2>
                    <p>Upload an audio file to the main endpoint:</p>
                    <pre style="background: #f8fafc; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #e5e7eb;">
curl -X POST "https://CTS-VibeAppca3602-1.azurewebsites.net/api/v1/upload-and-analyze" \
     -F "file=@your_audio_file.wav" \
     -F "call_id=test_call_001"
                    </pre>

                    <p style="margin-top: 40px; text-align: center; color: #6b7280;">
                        <small>CallSight360 v2.0.0 - Deployed on Azure App Services</small>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting CallSight360 on Azure App Services...")
    logger.info("Initializing call transcription and analytics services...")
    logger.info("API is ready to process call recordings")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down CallSight360...")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 