from fastmcp.server.server import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
import asyncio
import uvicorn
from dotenv import load_dotenv ; load_dotenv()
import os
from starlette.requests import Request
from fastmcp.server.dependencies import get_http_request
# from mcp.server.fastmcp import Context #Context only works with the original fastmcp SDK
from typing import Any
import json
from fastmcp import Client, Context, FastMCP
from mcp import LoggingLevel
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastmcp.tools import Tool
import yaml
from pathlib import Path
import base64
import httpx
from contextlib import asynccontextmanager
from boto3 import Session
import botocore.config
from typing import Optional


@asynccontextmanager
async def boto3_lifespan(server: FastMCP,aws_access_key_id: str, aws_secret_access_key: str, region_name: str, session_token: Optional[str] = None):
    server.aws_session = Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name=region_name , aws_session_token=session_token)
    server.region_name = region_name
    server.session_config = botocore.config.Config(connect_timeout=10, read_timeout=30)
    yield


mcp_server = FastMCP(name="AWSMcpServer" ,
                     on_duplicate_tools = "warn",  # Options: "warn", "error", "ignore"
                     on_duplicate_resources = "warn",
                     on_duplicate_prompts = "warn",
                     mask_error_details = True,
                     lifespan=lambda server: boto3_lifespan(server, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                                                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                                                                region_name=os.getenv("AWS_REGION" , default="us-east-1"),
                                                                session_token=os.getenv("AWS_SESSION_TOKEN")),
)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Print incoming request details
        body = await request.body()
        print(f"INCOMING REQUEST: {request.method} {request.url.path}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {body.decode(errors='replace')}")
        
        # Process the request and get the response
        response = await call_next(request)
        
        # Print outgoing response details
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        print(f"OUTGOING RESPONSE: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {resp_body.decode(errors='replace')}")
        
        # Rebuild the response since we've consumed the body_iterator
        from starlette.responses import Response
        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

# @mcp_server.custom_route(path, methods=["GET"])
# async def custom_route(request: Request):
#     return JSONResponse({"message": f"route {path}"})

from tools.CloudFormation.script import list_resources
mcp_server.tool( name_or_fn = list_resources )

from tools.documentation.script import *
mcp_server.tool( name_or_fn = read_documentation )
mcp_server.tool( name_or_fn = search_documentation )
mcp_server.tool( name_or_fn = recommend )

mcp_app = mcp_server.http_app(path="/mcp" , transport="streamable-http")

#Health Check
async def status(request):
    return JSONResponse({"status": "ok"})

# Compose the main Starlette app, mounting the MCP app
app = Starlette(
    debug=True,
    routes=[
            Route("/status", status , name="Health Check"),
            Mount("/", mcp_app , name="MCP Server"),  # MCP server available at /mcp                
        ], 
    lifespan=mcp_app.lifespan
    )

#CORS and logging middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)


# Run background jobs after a response is sent (e.g., sending emails, logging).
# async def after_response():
#     print("Background task running!")

# async def my_route(request):
#     return JSONResponse({"ok": True}, background=BackgroundTask(after_response))

def server():
    config = uvicorn.Config(app=app, host="0.0.0.0", port="5000", lifespan="on" , log_level="debug") #lifespan can be included here
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    asyncio.run(server())


# Command to run the server:
# gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:2020