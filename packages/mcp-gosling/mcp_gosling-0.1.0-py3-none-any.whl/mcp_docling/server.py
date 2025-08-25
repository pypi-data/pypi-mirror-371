"""
MCP Docling Server

A Model Context Protocol (MCP) server that provides document processing capabilities
using IBM's Docling library. This server exposes tools for processing various 
document formats (PDF, DOCX, PPTX, images, HTML) and converting them to structured
formats like Markdown and JSON.
"""

import logging
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio

import certifi
from docling.document_converter import DocumentConverter

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("docling")

# Global converter instance for efficiency
_converter: Optional[DocumentConverter] = None

def get_converter() -> DocumentConverter:
    """Get or create the global DocumentConverter instance."""
    global _converter
    if _converter is None:
        # Configure SSL before creating DocumentConverter
        import os
        import certifi
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['CURL_CA_BUNDLE'] = certifi.where()
        
        # Use default configuration for simplicity
        _converter = DocumentConverter()
        logger.info("DocumentConverter initialized")
    return _converter

@mcp.tool()
def process_document(
    file_path: str,
    output_format: str = "markdown",
    extract_images: bool = False,
    extract_tables: bool = True
) -> str:
    """
    Process a document using Docling and return the converted content.
    
    Supports multiple formats: PDF, DOCX, PPTX, images (PNG, JPG), HTML, etc.
    
    Args:
        file_path: Path to the document file to process
        output_format: Output format ("markdown", "json", "text")
        extract_images: Whether to extract and describe images
        extract_tables: Whether to extract table structure
        
    Returns:
        Processed document content in the specified format
        
    Example:
        process_document("report.pdf", "markdown", True, True)
    """
    try:
        # Validate input parameters
        if not file_path or not isinstance(file_path, str):
            raise ValueError("file_path must be a non-empty string")
            
        if output_format not in ["markdown", "json", "text"]:
            raise ValueError("output_format must be 'markdown', 'json', or 'text'")
            
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Check file size (50MB limit)
        if path.stat().st_size > 50 * 1024 * 1024:
            raise ValueError("File size exceeds 50MB limit")
            
        logger.info(f"Processing document: {file_path}")
        
        # Get converter and process document
        converter = get_converter()
        result = converter.convert(file_path)
        
        if not result or not hasattr(result, 'document'):
            raise RuntimeError("Document conversion failed - no result returned")
            
        document = result.document
        
        # Return content based on requested format
        if output_format == "markdown":
            content = document.export_to_markdown()
        elif output_format == "json":
            content = document.export_to_json()
        elif output_format == "text":
            content = document.export_to_text()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        logger.info(f"Successfully processed {file_path} to {output_format}")
        return content
        
    except FileNotFoundError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {str(e)}")
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Document processing failed: {str(e)}")) from e

@mcp.tool()
def batch_process_documents(
    file_paths: List[str],
    output_format: str = "markdown",
    output_directory: str = ""
) -> str:
    """
    Process multiple documents in batch and optionally save to directory.
    
    Args:
        file_paths: List of paths to document files
        output_format: Output format for all documents ("markdown", "json", "text")
        output_directory: Optional directory to save processed files (empty = return content)
        
    Returns:
        Summary of batch processing results or combined content
        
    Example:
        batch_process_documents(["doc1.pdf", "doc2.docx"], "markdown", "/output")
    """
    try:
        if not file_paths or not isinstance(file_paths, list):
            raise ValueError("file_paths must be a non-empty list")
            
        if len(file_paths) > 20:
            raise ValueError("Batch processing limited to 20 files maximum")
            
        logger.info(f"Starting batch processing of {len(file_paths)} documents")
        
        results = []
        errors = []
        
        for i, file_path in enumerate(file_paths):
            try:
                content = process_document(file_path, output_format)
                
                if output_directory:
                    # Save to file in output directory
                    output_dir = Path(output_directory)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    input_name = Path(file_path).stem
                    ext = "md" if output_format == "markdown" else "json" if output_format == "json" else "txt"
                    output_file = output_dir / f"{input_name}_processed.{ext}"
                    
                    output_file.write_text(content, encoding='utf-8')
                    results.append(f"✅ {file_path} → {output_file}")
                else:
                    # Return combined content
                    results.append(f"--- Document: {file_path} ---\n{content}\n")
                    
            except Exception as e:
                error_msg = f"❌ {file_path}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Prepare summary
        summary = f"Batch Processing Complete:\n"
        summary += f"• Processed: {len(results)} documents\n"
        summary += f"• Errors: {len(errors)} documents\n\n"
        
        if errors:
            summary += "ERRORS:\n" + "\n".join(errors) + "\n\n"
            
        if output_directory:
            summary += "RESULTS:\n" + "\n".join(results)
            return summary
        else:
            # Return combined content
            return summary + "CONTENT:\n" + "\n".join(results)
            
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Batch processing failed: {str(e)}")) from e

@mcp.tool()
def extract_document_metadata(file_path: str) -> str:
    """
    Extract detailed metadata and structure information from a document.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        JSON string containing detailed metadata and document structure
        
    Example:
        extract_document_metadata("report.pdf")
    """
    try:
        if not file_path or not isinstance(file_path, str):
            raise ValueError("file_path must be a non-empty string")
            
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Extracting metadata from: {file_path}")
        
        converter = get_converter()
        result = converter.convert(file_path)
        
        if not result or not hasattr(result, 'document'):
            raise RuntimeError("Document conversion failed")
            
        document = result.document
        
        # Extract comprehensive metadata
        metadata = {
            "file_info": {
                "path": str(path.absolute()),
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "format": path.suffix.lower()
            },
            "document_structure": {
                "page_count": len(document.pages) if hasattr(document, 'pages') else 0,
                "has_tables": bool(getattr(document, 'tables', [])),
                "has_figures": bool(getattr(document, 'figures', [])),
                "element_count": len(getattr(document, 'elements', []))
            }
        }
        
        # Add page-level information if available
        if hasattr(document, 'pages') and document.pages:
            metadata["pages"] = []
            for i, page in enumerate(document.pages):
                page_info = {
                    "page_number": i + 1,
                    "elements": len(getattr(page, 'elements', [])),
                }
                if hasattr(page, 'size'):
                    page_info["dimensions"] = {
                        "width": getattr(page.size, 'width', None),
                        "height": getattr(page.size, 'height', None)
                    }
                metadata["pages"].append(page_info)
        
        # Export as formatted JSON
        import json
        return json.dumps(metadata, indent=2, ensure_ascii=False)
        
    except FileNotFoundError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except Exception as e:
        logger.error(f"Metadata extraction failed for {file_path}: {str(e)}")
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Metadata extraction failed: {str(e)}")) from e

if __name__ == "__main__":
    # This allows the server to be run directly for testing
    mcp.run()
