"""Docling toolkit for Goose - Document processing and conversion."""

import os
import ssl
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

import certifi
from goose.toolkit.base import Toolkit, tool


class DoclingToolkit(Toolkit):
    """A toolkit for processing documents using Docling.
    
    Supports processing of multiple document formats including:
    - PDF files
    - Microsoft Office documents (DOCX, PPTX, XLSX)
    - HTML files
    - Images (PNG, JPEG, TIFF, etc.)
    - Audio files (WAV, MP3) with speech recognition
    
    All documents are converted to clean Markdown format optimized for AI analysis.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Docling toolkit."""
        super().__init__(*args, **kwargs)
        self._docling_converter: Optional[Any] = None
        self._ensure_docling_available()

    def _ensure_docling_available(self) -> None:
        """Ensure Docling is available, with offline fallback."""
        try:
            # Configure SSL before importing Docling
            import os
            import certifi
            os.environ['SSL_CERT_FILE'] = certifi.where()
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            os.environ['CURL_CA_BUNDLE'] = certifi.where()
            
            # Try to import Docling
            from docling.document_converter import DocumentConverter
            self._docling_converter = DocumentConverter()
            self._use_offline_fallback = False
            print("✅ Docling initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Docling initialization failed: {str(e)}")
            print("🔄 Falling back to offline processor...")
            
            # Import and initialize offline processor
            from .offline_processor import OfflineDocumentProcessor
            self._offline_processor = OfflineDocumentProcessor()
            self._use_offline_fallback = True
            self._docling_converter = None
            print("✅ Offline processor initialized successfully")

    def _is_url(self, path: str) -> bool:
        """Check if a path is a URL."""
        parsed = urllib.parse.urlparse(path)
        return parsed.scheme in ('http', 'https', 'ftp')

    def _get_file_size(self, path: str) -> int:
        """Get file size in bytes. For URLs, try to get from headers."""
        if self._is_url(path):
            try:
                # Create SSL context using certifi bundle
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                req = urllib.request.Request(path, method='HEAD')
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    size_header = response.headers.get('Content-Length')
                    return int(size_header) if size_header else 0
            except Exception:
                # If we can't get size from headers, we'll check after download
                return 0
        else:
            return Path(path).stat().st_size

    def _download_url(self, url: str) -> str:
        """Download a URL to a temporary file and return the path."""
        try:
            # Create SSL context using certifi bundle
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(url, context=ssl_context) as response:
                # Create a temporary file with appropriate extension
                parsed_url = urllib.parse.urlparse(url)
                path_parts = Path(parsed_url.path)
                suffix = path_parts.suffix if path_parts.suffix else '.tmp'
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(response.read())
                    return tmp_file.name
        except Exception as e:
            raise RuntimeError(f"Failed to download {url}: {str(e)}")

    def _validate_file_size(self, path: str, max_size_mb: int = 20) -> None:
        """Validate that file size is within limits."""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if self._is_url(path):
            # For URLs, we'll check size after download if possible
            size = self._get_file_size(path)
            if size > 0 and size > max_size_bytes:
                raise ValueError(
                    f"File at {path} is {size / (1024*1024):.1f}MB, "
                    f"which exceeds the {max_size_mb}MB limit"
                )
        else:
            # For local files, check size directly
            if not Path(path).exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            size = self._get_file_size(path)
            if size > max_size_bytes:
                raise ValueError(
                    f"File {path} is {size / (1024*1024):.1f}MB, "
                    f"which exceeds the {max_size_mb}MB limit"
                )

    def _process_single_document(self, path: str) -> Dict[str, Any]:
        """Process a single document and return results."""
        original_path = path
        temp_file = None
        
        try:
            # Validate file size first
            self._validate_file_size(path)
            
            # Download if URL
            if self._is_url(path):
                temp_file = self._download_url(path)
                path = temp_file
                # Validate downloaded file size
                self._validate_file_size(path)
            
            # Use offline processor if Docling is not available
            if self._use_offline_fallback:
                return self._offline_processor.process_document(path)
            
            # Process with Docling
            result = self._docling_converter.convert(path)
            
            # Extract markdown content
            markdown_content = result.document.export_to_markdown()
            
            # Get document metadata
            metadata = {
                "source": original_path,
                "title": getattr(result.document, 'title', None) or Path(original_path).name,
                "num_pages": len(result.document.pages) if hasattr(result.document, 'pages') else None,
                "format": Path(original_path).suffix.lower(),
            }
            
            return {
                "success": True,
                "content": markdown_content,
                "metadata": metadata,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "metadata": {"source": original_path},
                "error": str(e)
            }
        finally:
            # Clean up temporary file
            if temp_file and Path(temp_file).exists():
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass  # Ignore cleanup errors

    @tool
    def process_document(
        self, 
        path: str, 
        max_size_mb: int = 20
    ) -> str:
        """Process a document using Docling and return clean Markdown content.
        
        Supports multiple formats including PDF, DOCX, PPTX, XLSX, HTML, images, 
        and audio files. Audio files are transcribed using speech recognition.
        
        Args:
            path: Path to document file (local path or URL)
            max_size_mb: Maximum file size in MB (default: 20MB)
            
        Returns:
            Processed document content in Markdown format, or error message if processing fails.
        """
        if not path:
            return "Error: No file path provided"
        
        try:
            result = self._process_single_document(path)
            
            if result["success"]:
                metadata = result["metadata"]
                content = result["content"]
                
                # Build response with metadata
                response_parts = []
                
                # Add document info header
                response_parts.append(f"# Document: {metadata['title']}")
                response_parts.append(f"**Source:** {metadata['source']}")
                if metadata.get('format'):
                    response_parts.append(f"**Format:** {metadata['format']}")
                if metadata.get('num_pages'):
                    response_parts.append(f"**Pages:** {metadata['num_pages']}")
                
                response_parts.append("\n---\n")
                response_parts.append(content)
                
                return "\n".join(response_parts)
            else:
                return f"Error processing document '{path}': {result['error']}"
                
        except Exception as e:
            return f"Unexpected error processing '{path}': {str(e)}"

    @tool
    def batch_process(
        self, 
        paths: List[str], 
        max_size_mb: int = 20
    ) -> str:
        """Process multiple documents using Docling and return combined Markdown content.
        
        Args:
            paths: List of document paths (local paths or URLs)
            max_size_mb: Maximum file size in MB per document (default: 20MB)
            
        Returns:
            Combined document content in Markdown format with clear document separators.
        """
        if not paths:
            return "Error: No file paths provided"
        
        if len(paths) > 10:
            return "Error: Too many files. Maximum 10 documents per batch."
        
        results = []
        successful = 0
        failed = 0
        
        for i, path in enumerate(paths, 1):
            results.append(f"\n# Document {i} of {len(paths)}\n")
            
            try:
                result = self._process_single_document(path)
                
                if result["success"]:
                    metadata = result["metadata"]
                    content = result["content"]
                    
                    results.append(f"## {metadata['title']}")
                    results.append(f"**Source:** {metadata['source']}")
                    if metadata.get('format'):
                        results.append(f"**Format:** {metadata['format']}")
                    if metadata.get('num_pages'):
                        results.append(f"**Pages:** {metadata['num_pages']}")
                    
                    results.append("\n---\n")
                    results.append(content)
                    results.append("\n" + "="*80 + "\n")
                    
                    successful += 1
                else:
                    results.append(f"**Error processing {path}:** {result['error']}")
                    results.append("\n" + "="*80 + "\n")
                    failed += 1
                    
            except Exception as e:
                results.append(f"**Unexpected error processing {path}:** {str(e)}")
                results.append("\n" + "="*80 + "\n")
                failed += 1
        
        # Add summary
        summary = [
            f"\n# Batch Processing Summary",
            f"**Total documents:** {len(paths)}",
            f"**Successfully processed:** {successful}",
            f"**Failed:** {failed}",
            "\n" + "="*80 + "\n"
        ]
        
        return "\n".join(summary + results)

    @tool
    def extract_metadata(self, path: str) -> str:
        """Extract metadata from a document without full content processing.
        
        Useful for quickly getting document information like title, page count,
        format, and other properties without processing the entire content.
        
        Args:
            path: Path to document file (local path or URL)
            
        Returns:
            Document metadata in a readable format.
        """
        if not path:
            return "Error: No file path provided"
        
        temp_file = None
        original_path = path
        
        try:
            # Validate file size
            self._validate_file_size(path, max_size_mb=5)  # Smaller limit for metadata
            
            # Download if URL
            if self._is_url(path):
                temp_file = self._download_url(path)
                path = temp_file
            
            # Use offline processor if Docling is not available
            if self._use_offline_fallback:
                metadata = self._offline_processor.extract_metadata(path)
                if 'error' in metadata:
                    return f"Error extracting metadata from '{original_path}': {metadata['error']}"
                    
                # Format metadata for display
                import json
                return f"# Document Metadata\n\n```json\n{json.dumps(metadata, indent=2)}\n```"
            
            # Process with Docling
            result = self._docling_converter.convert(path)
            
            # Extract comprehensive metadata
            doc = result.document
            metadata_parts = []
            
            metadata_parts.append(f"# Document Metadata")
            metadata_parts.append(f"**Source:** {original_path}")
            metadata_parts.append(f"**Filename:** {Path(original_path).name}")
            metadata_parts.append(f"**Format:** {Path(original_path).suffix.lower()}")
            
            if hasattr(doc, 'title') and doc.title:
                metadata_parts.append(f"**Title:** {doc.title}")
            
            if hasattr(doc, 'pages'):
                metadata_parts.append(f"**Number of Pages:** {len(doc.pages)}")
            
            # Try to get file size
            try:
                if not self._is_url(original_path):
                    size = Path(original_path).stat().st_size
                    size_mb = size / (1024 * 1024)
                    metadata_parts.append(f"**File Size:** {size_mb:.2f} MB")
            except Exception:
                pass
            
            # Try to extract any other available metadata
            if hasattr(doc, 'meta') and doc.meta:
                metadata_parts.append(f"\n## Additional Metadata")
                for key, value in doc.meta.items():
                    if value:
                        metadata_parts.append(f"**{key.title()}:** {value}")
            
            return "\n".join(metadata_parts)
            
        except Exception as e:
            return f"Error extracting metadata from '{original_path}': {str(e)}"
        finally:
            # Clean up temporary file
            if temp_file and Path(temp_file).exists():
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
