"""
Offline document processor for Gosling - works without external model downloads.
Uses PyPDF2, python-docx, and other offline libraries for document processing.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json

class OfflineDocumentProcessor:
    """Simple offline document processor that works without external dependencies."""
    
    def __init__(self):
        """Initialize the offline processor."""
        self.supported_formats = {'.pdf', '.txt', '.md', '.json'}
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported."""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def process_pdf(self, file_path: str) -> str:
        """Process PDF files using PyPDF2."""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append(f"## Page {page_num}\n\n{page_text}\n")
                    except Exception as e:
                        text_content.append(f"## Page {page_num}\n\n*Error extracting text: {str(e)}*\n")
                
                return "\n".join(text_content)
                
        except ImportError:
            return "Error: PyPDF2 not installed. Install with: pip install PyPDF2"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
    
    def process_text_file(self, file_path: str) -> str:
        """Process plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return f"# {Path(file_path).name}\n\n{content}"
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                    return f"# {Path(file_path).name}\n\n{content}"
            except Exception as e:
                return f"Error reading file: {str(e)}"
        except Exception as e:
            return f"Error processing text file: {str(e)}"
    
    def process_markdown(self, file_path: str) -> str:
        """Process markdown files."""
        return self.process_text_file(file_path)
    
    def process_json(self, file_path: str) -> str:
        """Process JSON files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                return f"# {Path(file_path).name}\n\n```json\n{formatted_json}\n```"
        except Exception as e:
            return f"Error processing JSON file: {str(e)}"
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and return results."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "content": None,
                "metadata": {"source": str(file_path)}
            }
        
        if not self.is_supported(str(file_path)):
            return {
                "success": False,
                "error": f"Unsupported file format: {file_path.suffix}",
                "content": None,
                "metadata": {"source": str(file_path)}
            }
        
        try:
            # Process based on file extension
            suffix = file_path.suffix.lower()
            
            if suffix == '.pdf':
                content = self.process_pdf(str(file_path))
            elif suffix in ['.txt', '.text']:
                content = self.process_text_file(str(file_path))
            elif suffix in ['.md', '.markdown']:
                content = self.process_markdown(str(file_path))
            elif suffix == '.json':
                content = self.process_json(str(file_path))
            else:
                return {
                    "success": False,
                    "error": f"No processor for format: {suffix}",
                    "content": None,
                    "metadata": {"source": str(file_path)}
                }
            
            # Get file metadata
            stat = file_path.stat()
            metadata = {
                "source": str(file_path),
                "title": file_path.name,
                "format": suffix,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": stat.st_mtime
            }
            
            return {
                "success": True,
                "error": None,
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "content": None,
                "metadata": {"source": str(file_path)}
            }
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a document without full processing."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            stat = file_path.stat()
            metadata = {
                "file_info": {
                    "path": str(file_path.absolute()),
                    "name": file_path.name,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "format": file_path.suffix.lower(),
                    "modified": stat.st_mtime,
                    "supported": self.is_supported(str(file_path))
                }
            }
            
            # Add format-specific metadata
            if file_path.suffix.lower() == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        metadata["document_structure"] = {
                            "page_count": len(pdf_reader.pages),
                            "has_metadata": bool(pdf_reader.metadata),
                            "encrypted": pdf_reader.is_encrypted
                        }
                        
                        if pdf_reader.metadata:
                            metadata["pdf_metadata"] = {
                                "title": pdf_reader.metadata.get('/Title'),
                                "author": pdf_reader.metadata.get('/Author'),
                                "subject": pdf_reader.metadata.get('/Subject'),
                                "creator": pdf_reader.metadata.get('/Creator'),
                                "producer": pdf_reader.metadata.get('/Producer')
                            }
                except ImportError:
                    metadata["note"] = "PyPDF2 not available for detailed PDF metadata"
                except Exception as e:
                    metadata["pdf_error"] = str(e)
            
            return metadata
            
        except Exception as e:
            return {"error": f"Metadata extraction failed: {str(e)}"}
