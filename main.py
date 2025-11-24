"""
Main entry point for the FastAPI application.
Run this to start the REST API server.
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Customer Order Integration API...")
    print("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
