# copilot_terminal.py - REFACTORED: Can run/debug ANY file from ANYWHERE!
import requests
import json
import sys
import os
import subprocess
from pathlib import Path

# Fix for Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

# ============================================
# FILE MANAGEMENT - NOW HANDLES ANY PATH!
# ============================================

def resolve_file_path(filename):
    """
    Find a file anywhere on the system!
    Searches: current directory, absolute path, relative path
    """
    # If it's an absolute path, check it directly
    if os.path.isabs(filename):
        if os.path.exists(filename):
            return filename
        return None
    
    # Check current directory
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, filename)
    if os.path.exists(full_path):
        return full_path
    
    # Check if it's in the backend folder
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(backend_path):
        return backend_path
    
    # Check if it's in the user's desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    desktop_path = os.path.join(desktop, filename)
    if os.path.exists(desktop_path):
        return desktop_path
    
    # Check if it's in the parent directory
    parent_path = os.path.join(os.path.dirname(os.getcwd()), filename)
    if os.path.exists(parent_path):
        return parent_path
    
    # Try to find it anywhere (slow but thorough)
    for root, dirs, files in os.walk(os.path.expanduser("~")):
        if filename in files:
            return os.path.join(root, filename)
        # Limit search to avoid infinite loops
        break
    
    return None

def list_files(directory=None):
    """List all Python files in a directory"""
    if directory is None:
        directory = os.getcwd()
    
    files = []
    for ext in ['.py', '.js', '.ts', '.html', '.css', '.json', '.sh', '.ps1']:
        for file in Path(directory).glob(f'*{ext}'):
            files.append(str(file))
    return files

# ============================================
# CORE FUNCTIONS
# ============================================

def chat(message, role="architect"):
    """Send a chat message to Copilot"""
    try:
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": message,
            "role": role
        }, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def execute_command(command):
    """Execute a terminal command via Copilot"""
    try:
        response = requests.post(f"{BASE_URL}/debug/execute", json={
            "command": command,
            "cwd": os.getcwd(),
            "timeout": 60
        }, timeout=65)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def clone_repo(url):
    """Clone a repository"""
    try:
        response = requests.post(f"{BASE_URL}/repo/clone", json={
            "repo_url": url,
            "branch": "main"
        }, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def search_code(query):
    """Search code in analyzed repo"""
    try:
        response = requests.post(f"{BASE_URL}/repo/search", json={
            "query": query,
            "n_results": 3
        }, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_code(prompt, language="python"):
    """Generate code from a prompt and save it to a file"""
    print("\n[GENERATING CODE...]")
    
    full_prompt = f"""Generate COMPLETE, WORKING {language} code for the following request.
    Make it production-ready with error handling, comments, and best practices.
    Return ONLY the code, no explanations.
    
    Request: {prompt}
    
    Requirements:
    - Include all necessary imports
    - Add proper error handling
    - Include comments explaining the code
    - Make it runnable as-is
    - Follow {language} best practices
    """
    
    result = chat(full_prompt, "architect")
    
    if "error" in result:
        return {"error": result["error"]}
    
    code = result.get("response", "")
    
    # Extract code from markdown
    if "```" in code:
        lines = code.split("\n")
        in_code = False
        code_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
        if code_lines:
            code = "\n".join(code_lines)
    
    # Determine file extension
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "html": ".html",
        "css": ".css",
        "json": ".json",
        "bash": ".sh",
        "powershell": ".ps1"
    }
    ext = ext_map.get(language.lower(), ".txt")
    
    # Save to file in current directory
    filename = f"generated_code{ext}"
    counter = 1
    while os.path.exists(filename):
        filename = f"generated_code_{counter}{ext}"
        counter += 1
    
    # Save with full path
    full_path = os.path.join(os.getcwd(), filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    return {
        "success": True,
        "filename": full_path,
        "code": code,
        "language": language,
        "message": f"Code saved to {full_path}"
    }

def debug_code(filename):
    """Debug ANY code file from ANYWHERE!"""
    # Find the file
    file_path = resolve_file_path(filename)
    
    if not file_path:
        return {"error": f"File '{filename}' not found. Please provide the full path or ensure the file exists."}
    
    print(f"\n[DEBUGGING: {file_path}]")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"error": f"Could not read file: {e}"}
    
    # Get language from extension
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".sh": "bash",
        ".ps1": "powershell"
    }
    ext = os.path.splitext(file_path)[1]
    language = ext_map.get(ext, "unknown")
    
    # Build debug prompt
    debug_prompt = (
        "Debug this {language} code and fix any issues.\n"
        "Return the COMPLETE FIXED code with explanations of what was wrong.\n\n"
        "Code:\n"
        "```\n"
        "{code}\n"
        "```\n\n"
        "Requirements:\n"
        "- Identify and fix all bugs\n"
        "- Add missing imports\n"
        "- Fix syntax errors\n"
        "- Improve error handling\n"
        "- Return the complete working code"
    ).format(language=language, code=code)
    
    result = chat(debug_prompt, "debug")
    
    if "error" in result:
        return {"error": result["error"]}
    
    fixed_code = result.get("response", "")
    
    # Extract code from markdown
    if "```" in fixed_code:
        lines = fixed_code.split("\n")
        in_code = False
        code_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
        if code_lines:
            fixed_code = "\n".join(code_lines)
    
    # Save fixed code in the same directory as original
    original_dir = os.path.dirname(file_path)
    original_name = os.path.basename(file_path)
    fixed_filename = os.path.join(original_dir, f"fixed_{original_name}")
    
    with open(fixed_filename, "w", encoding="utf-8") as f:
        f.write(fixed_code)
    
    return {
        "success": True,
        "original": file_path,
        "fixed": fixed_filename,
        "code": fixed_code,
        "message": f"Fixed code saved to {fixed_filename}"
    }

def run_code(filename):
    """Run ANY Python file from ANYWHERE!"""
    # Find the file
    file_path = resolve_file_path(filename)
    
    if not file_path:
        return {"error": f"File '{filename}' not found. Please provide the full path or ensure the file exists."}
    
    print(f"\n[RUNNING: {file_path}]")
    
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(file_path)  # Run in the file's directory
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "file": file_path
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout - code took too long to run"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def print_response(data):
    """Pretty print response"""
    if isinstance(data, dict):
        if "error" in data:
            print(f"\n[ERROR] {data['error']}")
        elif "response" in data:
            print("\n" + "="*50)
            print("RESPONSE:")
            print("="*50)
            print(data["response"])
            print("="*50)
        elif "stdout" in data:
            print("\n[OUTPUT]")
            print(data["stdout"])
            if data.get("stderr"):
                print("\n[ERRORS]")
                print(data["stderr"])
        elif "filename" in data:
            print(f"\n[SUCCESS] {data['message']}")
            print("\nCODE PREVIEW:")
            print("-"*40)
            print(data.get("code", "")[:500] + ("..." if len(data.get("code", "")) > 500 else ""))
            print("-"*40)
        elif "fixed" in data:
            print(f"\n[SUCCESS] {data['message']}")
        elif "file" in data:
            print(f"\n[SUCCESS] File: {data['file']}")
        else:
            print(json.dumps(data, indent=2))
    else:
        print(data)

def main():
    print("=" * 50)
    print("FOUNDER COPILOT TERMINAL")
    print("=" * 50)
    print("Commands: chat, exec, clone, search, code, debug, run, help, exit")
    print("=" * 50)
    print("\nNEW! Can run/debug ANY file from ANYWHERE!")
    print("Just type the filename or full path")
    print("=" * 50)
    
    while True:
        try:
            cmd = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        
        if not cmd:
            continue
            
        if cmd == "exit" or cmd == "quit":
            print("Goodbye!")
            break
            
        elif cmd == "help":
            print("""
AVAILABLE COMMANDS:
  chat <message>     - Chat with Copilot
  exec <command>     - Execute terminal command
  clone <repo_url>   - Clone GitHub repo
  search <query>     - Search code
  code <prompt>      - GENERATE working code from description
  debug <filename>   - DEBUG any file (uses full path or filename)
  run <filename>     - RUN any Python file (uses full path or filename)
  ls                 - List Python files in current directory
  help               - Show this help
  exit               - Exit terminal

EXAMPLES:
  code A Python function to calculate Fibonacci numbers
  debug generated_code.py
  debug C:/Users/User/Desktop/my_script.py
  run generated_code.py
  run C:/Users/User/Desktop/my_script.py
  ls
  exec python --version
  chat How do I build a REST API?
            """)
            
        elif cmd == "ls":
            files = list_files()
            if files:
                print("\nPYTHON FILES IN CURRENT DIRECTORY:")
                for f in files:
                    print(f"  - {f}")
            else:
                print("\nNo Python files found in current directory.")
            
        elif cmd.startswith("chat "):
            message = cmd[5:]
            print("\n[Thinking...]")
            result = chat(message)
            print_response(result)
            
        elif cmd.startswith("exec "):
            command = cmd[5:]
            print(f"\n[Running: {command}]")
            result = execute_command(command)
            print_response(result)
            
        elif cmd.startswith("clone "):
            url = cmd[6:]
            print(f"\n[Cloning: {url}]")
            result = clone_repo(url)
            print_response(result)
            
        elif cmd.startswith("search "):
            query = cmd[7:]
            print(f"\n[Searching: {query}]")
            result = search_code(query)
            print_response(result)
            
        elif cmd.startswith("code "):
            prompt = cmd[5:]
            result = generate_code(prompt)
            print_response(result)
            
            if result.get("success"):
                filename = result.get("filename")
                print(f"\nGenerated: {filename}")
                print("Type 'run {filename}' to execute it")
                print("Type 'debug {filename}' to fix any issues")
            
        elif cmd.startswith("debug "):
            filename = cmd[6:].strip()
            result = debug_code(filename)
            print_response(result)
            
        elif cmd.startswith("run "):
            filename = cmd[4:].strip()
            result = run_code(filename)
            print_response(result)
            
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

if __name__ == "__main__":
    main()