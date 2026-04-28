"""
Deployment wrapper — serves the React frontend as static files
alongside the FastAPI backend, all from a single process and port.

This file does NOT modify any existing application code.
It simply imports the existing FastAPI app and mounts the
pre-built React frontend on top of it.
"""

import os
from api_server import app
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# SPA fallback: serve index.html for all non-API 404s so React Router works
@app.exception_handler(404)
async def _spa_fallback(request, exc):
    if not request.url.path.startswith("/api"):
        index = os.path.join(_static, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
    return JSONResponse({"detail": "Not found"}, status_code=404)

# Mount React build output — API routes defined in api_server.py take precedence
if os.path.isdir(_static):
    app.mount("/", StaticFiles(directory=_static, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
