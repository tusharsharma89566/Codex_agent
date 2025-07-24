import subprocess
import tempfile
import os
import sys
from typing import Dict, Any

class SafeCodeExecutor:
    def __init__(self):
        self.supported_languages = {
            'python': self.execute_python,
            'java': self.execute_java,
            'cpp': self.execute_cpp,
            'javascript': self.execute_javascript
        }
    
    def execute_code(self, code: str, language: str) -> Dict[str, Any]:
        """Execute code safely and return results"""
        if language.lower() not in self.supported_languages:
            return {
                "success": False,
                "output": f"Language {language} not supported",
                "error": "Unsupported language"
            }
        
        try:
            return self.supported_languages[language.lower()](code)
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def execute_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        finally:
            os.unlink(temp_file)
    
    def execute_java(self, code: str) -> Dict[str, Any]:
        """Execute Java code"""
        # Extract class name from code
        class_name = "Main"
        if "public class" in code:
            import re
            match = re.search(r'public class (\w+)', code)
            if match:
                class_name = match.group(1)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Compile
            compile_result = subprocess.run(
                ['javac', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "error": compile_result.stderr
                }
            
            # Execute
            class_file = temp_file.replace('.java', '.class')
            result = subprocess.run(
                ['java', '-cp', os.path.dirname(temp_file), class_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        finally:
            os.unlink(temp_file)
            class_file = temp_file.replace('.java', '.class')
            if os.path.exists(class_file):
                os.unlink(class_file)
    
    def execute_cpp(self, code: str) -> Dict[str, Any]:
        """Execute C++ code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        executable = temp_file.replace('.cpp', '')
        
        try:
            # Compile
            compile_result = subprocess.run(
                ['g++', temp_file, '-o', executable],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "error": compile_result.stderr
                }
            
            # Execute
            result = subprocess.run(
                [executable],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        finally:
            os.unlink(temp_file)
            if os.path.exists(executable):
                os.unlink(executable)
    
    def execute_javascript(self, code: str) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        finally:
            os.unlink(temp_file)
