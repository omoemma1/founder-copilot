# backend/main.py - COMPLETE WORKING VERSION WITH GROQ!
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

# ============================================
# IMPORT SERVICES
# ============================================
try:
    from services.groq_service import groq
    print("✅ Groq service loaded")
except Exception as e:
    print(f"⚠️ Groq service not loaded: {e}")
    groq = None

try:
    from services.repo_service import repo_service
    print("✅ Repository service loaded")
except Exception as e:
    print(f"⚠️ Repository service not loaded: {e}")
    repo_service = None

try:
    from services.debug_service import debugger
    print("✅ Debugger service loaded")
except Exception as e:
    print(f"⚠️ Debugger service not loaded: {e}")
    debugger = None

try:
    from services.memory_service import memory
    print("✅ Memory service loaded")
except Exception as e:
    print(f"⚠️ Memory service not loaded: {e}")
    memory = None

# ============================================
# LOAD ENVIRONMENT
# ============================================
load_dotenv()

# ============================================
# CREATE FASTAPI APP - THIS MUST BE FIRST!
# ============================================
app = FastAPI(
    title="Founder Copilot",
    description="Your AI software development assistant with Groq AI",
    version="0.4.0"
)

# ============================================
# CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# DATA MODELS
# ============================================
class ChatRequest(BaseModel):
    message: str
    role: str = "architect"
    context: Optional[Dict] = {}

class ChatResponse(BaseModel):
    response: str
    role: str
    timestamp: str

class CloneRequest(BaseModel):
    repo_url: str
    branch: str = "main"

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5

class ChatWithCodeRequest(BaseModel):
    message: str
    role: str = "architect"

class CommandRequest(BaseModel):
    command: str
    cwd: Optional[str] = None
    timeout: int = 60

# ============================================
# BASE ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return {
        "name": "Founder Copilot API",
        "version": "0.4.0",
        "status": "running",
        "ai_provider": "groq" if groq and groq.enabled else "offline",
        "services": {
            "chat": True,
            "repository": repo_service is not None,
            "debugger": debugger is not None,
            "memory": memory is not None
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_available": groq is not None and groq.enabled if groq else False,
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# CHAT ENDPOINT - USING GROQ!
# ============================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with AI using Groq (FREE!)"""
    try:
        if groq and groq.enabled:
            response = await groq.chat(
                message=request.message,
                role=request.role,
                context=request.context
            )
        else:
            response = "Groq AI is not configured. Please add GROQ_API_KEY to .env file."
        
        return {
            "response": response,
            "role": request.role,
            "provider": "groq" if groq and groq.enabled else "offline",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# REPOSITORY ENDPOINTS
# ============================================
if repo_service:
    @app.post("/repo/clone")
    async def clone_repository(request: CloneRequest):
        try:
            result = repo_service.clone_repository(request.repo_url, request.branch)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/repo/analyze")
    async def analyze_codebase():
        try:
            result = repo_service.analyze_codebase()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/repo/search")
    async def search_codebase(request: SearchRequest):
        try:
            results = repo_service.search_code(request.query, request.n_results)
            return {"success": True, "query": request.query, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/repo/summary")
    async def get_summary():
        try:
            result = repo_service.get_architecture_summary()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/repo/chat")
    async def chat_with_code(request: ChatWithCodeRequest):
        try:
            context = repo_service.get_code_context(request.message)
            if groq and groq.enabled:
                response = await groq.chat(
                    message=f"{request.message}\n\nCode context:\n{context}",
                    role=request.role
                )
            else:
                response = "Groq AI is not configured"
            return {"success": True, "response": response, "role": request.role}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/repo/status")
    async def get_repo_status():
        try:
            return {
                "success": True,
                "has_repo": repo_service.current_repo_path is not None,
                "repo_path": str(repo_service.current_repo_path) if repo_service.current_repo_path else None,
                "embeddings_count": repo_service.collection.count()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================
# DEBUGGER ENDPOINTS
# ============================================
if debugger:
    @app.post("/debug/execute")
    async def execute_command(request: CommandRequest):
        try:
            result = await debugger.execute(
                command=request.command,
                cwd=request.cwd,
                timeout=request.timeout
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/debug/history")
    async def get_debug_history(limit: int = 10):
        try:
            return {
                "success": True,
                "commands": debugger.get_history(limit),
                "total": len(debugger.command_history)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/debug/summary")
    async def get_debug_summary():
        try:
            return {
                "success": True,
                "summary": debugger.get_summary()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.delete("/debug/history")
    async def clear_debug_history():
        try:
            debugger.clear_history()
            return {"success": True, "message": "History cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/debug/analyze")
    async def analyze_output(request: dict):
        try:
            output = request.get("output", "")
            errors = debugger._analyze_errors(output)
            fixes = debugger._generate_fixes(errors)
            return {
                "success": True,
                "errors": errors,
                "fixes": fixes
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🚀 FOUNDER COPILOT STARTING...")
    print("=" * 50)
    print(f"📡 API Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/health")
    if groq and groq.enabled:
        print(f"🤖 AI Provider: Groq (FREE!)")
    else:
        print(f"⚠️ AI Provider: Offline (Set GROQ_API_KEY)")
    print("=" * 50)
    print("Press CTRL+C to stop")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8000
    )