# backend/services/debug_service.py
"""
TERMINAL DEBUGGER - Run commands and fix errors automatically!
Your Copilot can now execute commands and debug like a pro!
"""

import subprocess
import asyncio
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import shlex

class TerminalDebugger:
    """The ultimate debugging engine for your Copilot"""
    
    def __init__(self):
        self.command_history = []
        self.error_patterns = {
            # Python errors
            "ModuleNotFoundError": "Missing Python package. Run: pip install [package_name]",
            "ImportError": "Import issue. Check module name and path.",
            "SyntaxError": "Syntax error in code. Check the line number.",
            "TypeError": "Type mismatch. Check the data types.",
            "ValueError": "Invalid value. Check the input.",
            "KeyError": "Dictionary key not found. Check the key exists.",
            "IndexError": "List index out of range. Check the list length.",
            "AttributeError": "Object has no attribute. Check the object type.",
            "FileNotFoundError": "File not found. Check the file path.",
            "PermissionError": "Permission denied. Run as administrator or check permissions.",
            "ConnectionError": "Connection failed. Check your network.",
            "TimeoutError": "Operation timed out. Increase timeout or check performance.",
            
            # npm/Node errors
            "npm ERR!": "NPM error. Check package.json and node_modules.",
            "cannot find module": "Module not found. Run: npm install",
            "command not found": "Command not installed. Install globally or locally.",
            "ERESOLVE": "Dependency resolution error. Try: npm install --legacy-peer-deps",
            "ENOENT": "File/directory not found. Check the path.",
            "EACCES": "Permission error. Run with sudo or fix permissions.",
            
            # Docker errors
            "Cannot connect to the Docker daemon": "Docker not running. Start Docker service.",
            "No such container": "Container doesn't exist. Check container name.",
            "Image not found": "Docker image not found. Build or pull the image.",
            "port is already allocated": "Port in use. Change the port mapping.",
            "Error response from daemon": "Docker daemon error. Check Docker logs.",
            
            # Git errors
            "fatal: not a git repository": "Not in a git repo. Initialize with: git init",
            "fatal: Authentication failed": "Git auth failed. Check your credentials.",
            "fatal: ambiguous argument": "Invalid git reference. Check the branch/tag.",
            "merge conflict": "Git merge conflict. Resolve conflicts manually.",
            "Your branch is ahead of": "Local branch has changes. Push or reset.",
            
            # System errors
            "Permission denied": "Permission issue. Run with appropriate privileges.",
            "No such file or directory": "File missing. Check the path.",
            "Is a directory": "Expected file but got directory.",
            "Not a directory": "Expected directory but got file.",
            "Invalid argument": "Invalid command argument. Check the syntax.",
            "Address already in use": "Port/address already in use. Use different port.",
            "Connection refused": "Service not running. Start the service.",
            "Network is unreachable": "Network issue. Check connection.",
            
            # General build errors
            "failed to build": "Build failed. Check logs for details.",
            "compilation error": "Compiler error. Check the syntax.",
            "runtime error": "Runtime error. Debug the code.",
        }
    
    async def execute(self, command: str, cwd: str = None, timeout: int = 60) -> Dict:
        """
        Execute a shell command and capture all output!
        Example: await debugger.execute("npm install")
        """
        start_time = datetime.now()
        result = {
            "command": command,
            "cwd": cwd or str(Path.cwd()),
            "success": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "errors": [],
            "fix_suggestions": [],
            "execution_time": 0,
            "timestamp": start_time.isoformat()
        }
        
        try:
            # Execute the command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=result["cwd"]
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                stdout, stderr = await process.communicate()
                result["errors"].append({
                    "type": "TimeoutError",
                    "message": f"Command timed out after {timeout} seconds",
                    "severity": "high"
                })
            
            # Decode output
            stdout = stdout.decode('utf-8', errors='ignore')
            stderr = stderr.decode('utf-8', errors='ignore')
            
            result["stdout"] = stdout
            result["stderr"] = stderr
            result["exit_code"] = process.returncode
            result["success"] = process.returncode == 0
            
            # Analyze for errors
            if not result["success"] or stderr:
                result["errors"] = self._analyze_errors(stderr + stdout)
                result["fix_suggestions"] = self._generate_fixes(result["errors"])
            
        except Exception as e:
            result["errors"].append({
                "type": type(e).__name__,
                "message": str(e),
                "severity": "critical"
            })
            result["success"] = False
        
        result["execution_time"] = (datetime.now() - start_time).total_seconds()
        self.command_history.append(result)
        
        return result
    
    def _analyze_errors(self, output: str) -> List[Dict]:
        """Analyze command output to find errors"""
        errors = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for known error patterns
            for pattern, description in self.error_patterns.items():
                if pattern.lower() in line_lower:
                    errors.append({
                        "type": pattern,
                        "message": line.strip(),
                        "description": description,
                        "line_number": i + 1,
                        "severity": "high"
                    })
                    break
            else:
                # Check for generic error indicators
                if any(word in line_lower for word in ['error', 'fail', 'fatal', 'exception', 'traceback']):
                    errors.append({
                        "type": "GenericError",
                        "message": line.strip(),
                        "description": "Unknown error occurred",
                        "line_number": i + 1,
                        "severity": "medium"
                    })
        
        return errors
    
    def _generate_fixes(self, errors: List[Dict]) -> List[Dict]:
        """Generate fix suggestions based on errors"""
        fixes = []
        
        for error in errors:
            error_type = error.get("type", "")
            error_msg = error.get("message", "").lower()
            
            fix = {
                "error_type": error_type,
                "error_message": error.get("message", ""),
                "suggestions": [],
                "commands": []
            }
            
            # Specific fixes by error type
            if "ModuleNotFoundError" in error_type or "No module named" in error_msg:
                # Extract package name
                import re
                package_match = re.search(r"named ['\"]([^'\"]+)['\"]", error_msg)
                package = package_match.group(1) if package_match else "unknown"
                fix["suggestions"].append(f"Install the missing package: {package}")
                fix["commands"].append(f"pip install {package}")
                
            elif "ImportError" in error_type:
                fix["suggestions"].append("Check the import statement")
                fix["suggestions"].append("Ensure the module exists")
                fix["commands"].append("pip list")  # Check installed packages
                
            elif "SyntaxError" in error_type:
                fix["suggestions"].append("Check the syntax at the indicated line")
                fix["suggestions"].append("Look for missing parentheses, brackets, or quotes")
                
            elif "TypeError" in error_type:
                fix["suggestions"].append("Check the data type of variables")
                fix["suggestions"].append("Use print() to debug variable types")
                
            elif "FileNotFoundError" in error_type:
                fix["suggestions"].append("Check the file path exists")
                fix["suggestions"].append("Create the file if needed")
                
            elif "npm" in error_type.lower() or "npm ERR" in error_msg:
                fix["suggestions"].append("Check package.json")
                fix["suggestions"].append("Clear node_modules and reinstall")
                fix["commands"].append("npm install")
                fix["commands"].append("npm cache clean --force")
                
            elif "permission denied" in error_msg:
                fix["suggestions"].append("Run with elevated privileges")
                if "cmd" in error_msg or "C:\\" in error_msg:
                    fix["commands"].append("Run as Administrator")
                else:
                    fix["commands"].append("sudo " + self._extract_command(error_msg))
                    
            elif "docker" in error_type.lower() or "docker" in error_msg:
                fix["suggestions"].append("Check Docker daemon is running")
                fix["suggestions"].append("Check Dockerfile syntax")
                fix["commands"].append("docker ps")  # Test Docker connection
                
            elif "git" in error_type.lower() or "git" in error_msg:
                if "not a git repository" in error_msg:
                    fix["suggestions"].append("Initialize a git repository")
                    fix["commands"].append("git init")
                elif "Authentication failed" in error_msg:
                    fix["suggestions"].append("Check your git credentials")
                    fix["commands"].append("git config --list")
                    
            elif "timeout" in error_msg:
                fix["suggestions"].append("Increase the timeout")
                fix["suggestions"].append("Check network connection")
                fix["suggestions"].append("Optimize the operation")
                
            elif "connection refused" in error_msg:
                fix["suggestions"].append("Check if the service is running")
                fix["suggestions"].append("Check the port number")
                fix["commands"].append("netstat -ano | findstr :PORT")
            
            else:
                # Generic fix
                fix["suggestions"].append("Check the error message for details")
                fix["suggestions"].append("Run the command with --help for options")
                fix["suggestions"].append("Search the error online")
            
            # Add generic debugging commands if no specific commands
            if not fix["commands"]:
                fix["commands"].append("echo 'Debugging...'")
                fix["commands"].append("echo 'Check the error above'")
            
            fixes.append(fix)
        
        return fixes
    
    def _extract_command(self, error_msg: str) -> str:
        """Extract the failing command from error message"""
        # Try to find the command in the error
        words = error_msg.split()
        for i, word in enumerate(words):
            if any(cmd in word for cmd in ['pip', 'npm', 'docker', 'git', 'python']):
                return ' '.join(words[i:i+3])
        return ""
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get command execution history"""
        return self.command_history[-limit:]
    
    def get_summary(self) -> Dict:
        """Get debugging statistics"""
        total = len(self.command_history)
        successful = sum(1 for cmd in self.command_history if cmd["success"])
        failed = total - successful
        
        # Count error types
        error_types = {}
        for cmd in self.command_history:
            for error in cmd.get("errors", []):
                error_type = error.get("type", "Unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_commands": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "N/A",
            "error_types": dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            "last_command": self.command_history[-1] if self.command_history else None
        }
    
    def clear_history(self):
        """Clear command history"""
        self.command_history = []

# Create global instance
debugger = TerminalDebugger()