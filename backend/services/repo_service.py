# backend/services/repo_service.py
import os
import git
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import time

class RepositoryIntelligence:
    def __init__(self):
        self.data_dir = Path("./data")
        self.repos_dir = self.data_dir / "repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔄 Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded!")
        
        self.chroma_client = chromadb.PersistentClient(path="./data/chromadb")
        self.collection_name = "code_embeddings"
        
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            print(f"✅ Loaded existing vector database with {self.collection.count()} embeddings")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Created new vector database!")
        
        self.current_repo_path = None
        self.current_repo = None
        self.stats = {"total_files": 0, "total_chunks": 0, "languages": {}, "last_analysis": None}
        
        self.parsers = {
            '.py': self._parse_python,
            '.js': self._parse_javascript,
            '.jsx': self._parse_javascript,
            '.ts': self._parse_typescript,
            '.tsx': self._parse_typescript,
            '.go': self._parse_go,
            '.java': self._parse_java,
            '.c': self._parse_c,
            '.cpp': self._parse_cpp,
            '.rs': self._parse_rust,
            '.rb': self._parse_ruby,
            '.php': self._parse_php,
            '.cs': self._parse_csharp,
            '.swift': self._parse_swift,
            '.kt': self._parse_kotlin,
        }
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> Dict:
        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = self.repos_dir / repo_name
            
            if repo_path.exists():
                print(f"📂 Updating existing repository...")
                repo = git.Repo(repo_path)
                repo.remotes.origin.pull()
                action = "updated"
            else:
                print(f"📥 Cloning {repo_url}...")
                repo = git.Repo.clone_from(repo_url, repo_path, branch=branch)
                action = "cloned"
            
            self.current_repo_path = repo_path
            self.current_repo = repo
            
            return {
                "success": True,
                "action": action,
                "repo_path": str(repo_path),
                "repo_name": repo_name,
                "message": f"Repository {action} successfully!"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_codebase(self) -> Dict:
        if not self.current_repo_path:
            return {"success": False, "error": "No repository loaded. Use clone_repository() first."}
        
        print(f"🔍 Analyzing codebase...")
        self.stats = {"total_files": 0, "total_chunks": 0, "languages": {}, "last_analysis": datetime.now().isoformat()}
        
        files_analyzed = []
        total_chunks = 0
        
        for file_path in Path(self.current_repo_path).rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix
                if ext in self.parsers and not file_path.name.startswith('.'):
                    try:
                        result = self._analyze_file(str(file_path))
                        if result:
                            files_analyzed.append(result)
                            total_chunks += result.get('chunks', 0)
                            self.stats["total_files"] += 1
                            lang = ext[1:] if ext.startswith('.') else ext
                            self.stats["languages"][lang] = self.stats["languages"].get(lang, 0) + 1
                    except Exception as e:
                        print(f"⚠️ Error analyzing {file_path}: {e}")
        
        self.stats["total_chunks"] = total_chunks
        print(f"✅ Analysis complete! Processed {self.stats['total_files']} files, {total_chunks} chunks")
        
        return {
            "success": True,
            "files_analyzed": len(files_analyzed),
            "total_chunks": total_chunks,
            "statistics": self.stats,
            "message": f"Analyzed {len(files_analyzed)} files!"
        }
    
    def _analyze_file(self, file_path: str) -> Optional[Dict]:
        ext = Path(file_path).suffix
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if not content.strip():
            return None
        
        parser_func = self.parsers[ext]
        parsed = parser_func(content)
        chunks = self._chunk_code(content)
        if not chunks:
            return None
        
        embeddings = self.embedder.encode(chunks).tolist()
        file_hash = hashlib.md5(content.encode()).hexdigest()
        rel_path = os.path.relpath(file_path, self.current_repo_path)
        
        doc_ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=[{
                    "file_path": rel_path,
                    "file_type": ext,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "functions": json.dumps(parsed.get('functions', [])[:5]),
                    "classes": json.dumps(parsed.get('classes', [])[:5]),
                } for i in range(len(chunks))],
                ids=doc_ids
            )
        except Exception as e:
            print(f"⚠️ Error storing embeddings for {file_path}: {e}")
            return None
        
        return {
            "file_path": rel_path,
            "file_type": ext,
            "chunks": len(chunks),
            "functions": parsed.get('functions', [])[:10],
            "classes": parsed.get('classes', [])[:10],
        }
    
    def search_code(self, query: str, n_results: int = 5) -> List[Dict]:
        if self.collection.count() == 0:
            return [{"content": "No code analyzed yet. Use analyze_codebase() first.", "metadata": {"file_path": "system"}, "similarity": 0}]
        
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=n_results, include=["documents", "metadatas", "distances"])
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            similarity = 1 - results['distances'][0][i]
            formatted_results.append({
                "content": results['documents'][0][i][:500] + ("..." if len(results['documents'][0][i]) > 500 else ""),
                "metadata": results['metadatas'][0][i],
                "similarity": round(similarity, 3)
            })
        return formatted_results
    
    def get_architecture_summary(self) -> Dict:
        if not self.current_repo_path:
            return {"success": False, "error": "No repository loaded"}
        
        all_files = list(Path(self.current_repo_path).rglob('*'))
        file_types = {}
        folder_structure = {}
        
        for f in all_files:
            if f.is_file():
                ext = f.suffix
                file_types[ext] = file_types.get(ext, 0) + 1
                rel_path = os.path.relpath(f.parent, self.current_repo_path)
                if rel_path == '.':
                    rel_path = 'root'
                folder_structure[rel_path] = folder_structure.get(rel_path, 0) + 1
        
        main_files = []
        for pattern in ['main.py', 'index.js', 'main.go', 'App.js', 'app.py']:
            matches = list(Path(self.current_repo_path).rglob(pattern))
            main_files.extend([str(m.relative_to(self.current_repo_path)) for m in matches])
        
        return {
            "success": True,
            "total_files": len(all_files),
            "code_files": len([f for f in all_files if f.suffix in self.parsers]),
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            "main_files": main_files[:5],
            "statistics": self.stats
        }
    
    def get_code_context(self, question: str, max_results: int = 3) -> str:
        if self.collection.count() == 0:
            return "No code has been analyzed yet."
        
        results = self.search_code(question, max_results)
        if not results or results[0].get('content') == "No code analyzed yet.":
            return "No relevant code found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"""
--- Relevant Code #{i} ---
File: {result['metadata']['file_path']}
Similarity: {result['similarity']}
```code
{result['content']}
```""")
        return "\n".join(context_parts)
    
    def _chunk_code(self, content: str, chunk_size: int = 500) -> List[str]:
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        for line in lines:
            if not current_chunk and not line.strip():
                continue
            current_chunk.append(line)
            current_size += len(line)
            if current_size > chunk_size and line.strip():
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return chunks
    
    def _parse_python(self, content: str) -> Dict:
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'^(?:import|from)\s+(\w+)', content, re.MULTILINE)
        return {'functions': functions, 'classes': classes, 'imports': imports[:20]}
    
    def _parse_javascript(self, content: str) -> Dict:
        functions = re.findall(r'(?:function|const)\s+(\w+)\s*[=\(]', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', content)
        return {'functions': functions, 'classes': classes, 'imports': imports[:20]}
    
    def _parse_typescript(self, content: str) -> Dict:
        return self._parse_javascript(content)
    
    def _parse_go(self, content: str) -> Dict:
        functions = re.findall(r'func\s+(\w+)\s*\(', content)
        types = re.findall(r'type\s+(\w+)\s+struct', content)
        imports = re.findall(r'import\s+[\'"](.+?)[\'"]', content)
        return {'functions': functions, 'classes': types, 'imports': imports[:20]}
    
    def _parse_java(self, content: str) -> Dict:
        classes = re.findall(r'(?:public|private|protected)?\s*(?:class|interface|enum)\s+(\w+)', content)
        methods = re.findall(r'(?:public|private|protected)?\s+.*?\s+(\w+)\s*\(', content)
        imports = re.findall(r'import\s+(.+?);', content)
        return {'functions': methods, 'classes': classes, 'imports': imports[:20]}
    
    def _parse_c(self, content: str) -> Dict:
        functions = re.findall(r'^.*?\s+(\w+)\s*\(.*?\)\s*\{', content, re.MULTILINE)
        return {'functions': functions, 'classes': [], 'imports': []}
    
    def _parse_cpp(self, content: str) -> Dict:
        functions = re.findall(r'^.*?\s+(\w+)\s*\(.*?\)\s*\{', content, re.MULTILINE)
        classes = re.findall(r'class\s+(\w+)', content)
        return {'functions': functions, 'classes': classes, 'imports': []}
    
    def _parse_rust(self, content: str) -> Dict:
        functions = re.findall(r'fn\s+(\w+)\s*\(', content)
        structs = re.findall(r'struct\s+(\w+)', content)
        return {'functions': functions, 'classes': structs, 'imports': []}
    
    def _parse_ruby(self, content: str) -> Dict:
        methods = re.findall(r'def\s+(\w+)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        return {'functions': methods, 'classes': classes, 'imports': []}
    
    def _parse_php(self, content: str) -> Dict:
        functions = re.findall(r'function\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        return {'functions': functions, 'classes': classes, 'imports': []}
    
    def _parse_csharp(self, content: str) -> Dict:
        classes = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', content)
        methods = re.findall(r'(?:public|private|protected)?\s+.*?\s+(\w+)\s*\(', content)
        return {'functions': methods, 'classes': classes, 'imports': []}
    
    def _parse_swift(self, content: str) -> Dict:
        functions = re.findall(r'func\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        return {'functions': functions, 'classes': classes, 'imports': []}
    
    def _parse_kotlin(self, content: str) -> Dict:
        functions = re.findall(r'fun\s+(\w+)\s*\(', content)
        classes = re.findall(r'(?:class|interface|object)\s+(\w+)', content)
        return {'functions': functions, 'classes': classes, 'imports': []}

repo_service = RepositoryIntelligence()