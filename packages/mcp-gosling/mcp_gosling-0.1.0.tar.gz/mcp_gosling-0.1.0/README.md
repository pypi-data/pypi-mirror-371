# 🦆 MCP Gosling - Document Processor for Goose

[![PyPI version](https://badge.fury.io/py/mcp-gosling.svg)](https://badge.fury.io/py/mcp-gosling)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Advanced document processing extension for Goose AI with enterprise-grade offline fallback**

A powerful [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides advanced document processing capabilities for [Goose](https://block.github.io/goose/). Process PDFs, DOCX, PPTX, images, and HTML documents with high fidelity using [IBM's Docling library](https://github.com/DS4SD/docling), with intelligent fallback to offline processing for network-restricted environments.

## ✨ **Key Features**

🔧 **Enterprise-Ready**: SSL certificate fixes for corporate networks  
📄 **Multi-Format**: PDF, DOCX, PPTX, images, HTML, and more  
🌐 **Offline Capable**: Graceful fallback to PyPDF2 when Hugging Face is blocked  
⚡ **High Performance**: Optimized for production workloads  
🛡️ **Robust**: Comprehensive error handling and validation  
🎯 **AI-Optimized**: Clean Markdown output perfect for AI analysis  

## 🚀 **Quick Start**

### Installation Options

#### Option 1: Standard Installation (Recommended)
```bash
pip install mcp-gosling
```

#### Option 2: Using uvx (Modern Tooling)
```bash
# Run directly without installation
uvx mcp-gosling

# Or using uv tool run (identical behavior)
uv tool run mcp-gosling
```

### Configuration for Goose

#### With Standard Installation:
```json
{
  "mcpServers": {
    "gosling": {
      "command": "mcp-gosling",
      "args": []
    }
  }
}
```

#### With uvx:
```json
{
  "mcpServers": {
    "gosling": {
      "command": "uvx",
      "args": ["mcp-gosling"]
    }
  }
}
```

### Usage

```bash
# Process your AWS certification PDF
goose "Process my AWS certification document at /path/to/cert.pdf"

# Batch process multiple documents
goose "Process all PDFs in my documents folder and summarize them"

# Extract metadata only
goose "What are the metadata details of this document?"
```

## 📋 **Available Tools**

### `process_document`
Process a single document and return clean Markdown content.

**Parameters:**
- `file_path` (string): Path to the document file
- `output_format` (string): "markdown", "json", or "text" (default: "markdown")
- `extract_images` (boolean): Whether to extract and describe images (default: false)
- `extract_tables` (boolean): Whether to extract table structure (default: true)

### `batch_process_documents`
Process multiple documents in batch with optional file output.

**Parameters:**
- `file_paths` (array): List of document file paths (max 20 files)
- `output_format` (string): Output format for all documents (default: "markdown")
- `output_directory` (string): Directory to save files (empty = return content)

### `extract_document_metadata`
Extract detailed metadata and structure information from a document.

**Parameters:**
- `file_path` (string): Path to the document file

## 🔧 **Advanced Features**

### Corporate Network Support
- ✅ SSL certificate fixes for enterprise environments
- ✅ Automatic fallback when Hugging Face Hub is blocked
- ✅ Works behind corporate firewalls and proxies

### Intelligent Processing
- **Primary**: IBM Docling for high-fidelity extraction with OCR and table recognition
- **Fallback**: PyPDF2 for reliable offline PDF processing
- **Formats**: PDF, DOCX, PPTX, PNG, JPG, HTML, TXT, MD, JSON

### Performance & Reliability
- File size limits (50MB for full processing, 5MB for metadata)
- Batch processing (up to 20 files)
- Comprehensive error handling
- Memory-efficient processing

## 🎯 **Use Cases**

- **📑 Document Analysis**: Extract and analyze content from reports, papers, contracts
- **🏢 Enterprise**: Process documents in network-restricted corporate environments  
- **🔍 Research**: Batch process academic papers and research documents
- **📊 Data Extraction**: Convert documents to structured data for AI analysis
- **📝 Content Migration**: Bulk convert document formats with preserved structure

## 🛠 **Technical Details**

**Built With:**
- [IBM Docling](https://github.com/DS4SD/docling) - Enterprise-grade document processing
- [PyPDF2](https://pypdf2.readthedocs.io/) - Reliable offline PDF processing
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol

**Requirements:**
- Python 3.9+
- Works on macOS, Linux, Windows
- Optional: GPU acceleration for enhanced performance

## 🚀 **Installation Options**

### For Goose Users (Recommended)

1. **Install via pip:**
   ```bash
   pip install mcp-gosling
   ```

2. **Configure in Goose:**
   Add the MCP server to your Goose configuration

3. **Start using:**
   ```bash
   goose "Process this document for me"
   ```

### For MCP Development

1. **Clone and install:**
   ```bash
   git clone https://github.com/masanderso/goose-docling.git
   cd goose-docling
   pip install -e .
   ```

2. **Test with MCP Inspector:**
   ```bash
   mcp dev src/mcp_docling/server.py
   ```

## 🔍 **Example Outputs**

### Document Processing
```markdown
# Document: AWS Certified Solutions Architect - Associate.pdf
**Source:** /path/to/document.pdf
**Format:** .pdf
**Pages:** 2

---

## Page 1

AWS Certified Solutions Architect - Associate
Notice of Exam Results
Candidate: Matthew Sanderson Exam Date: 12/3/2024
Candidate Score: 779 Pass/Fail: PASS
...
```

### Metadata Extraction
```json
{
  "file_info": {
    "name": "document.pdf",
    "size_mb": 0.03,
    "format": ".pdf"
  },
  "document_structure": {
    "page_count": 2,
    "has_tables": true,
    "has_figures": false
  }
}
```

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 **Links**

- [Goose AI Assistant](https://block.github.io/goose/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [IBM Docling Library](https://github.com/DS4SD/docling)
- [Issue Tracker](https://github.com/masanderso/goose-docling/issues)

## 🏷️ **Tags**

`goose-extension` `document-processing` `mcp-server` `docling` `pdf-processing` `enterprise-ready` `offline-capable` `ai-tools`

## 🚀 Features

- **Multi-format Support**: PDF, DOCX, PPTX, images (PNG, JPG), HTML, and more
- **Intelligent Processing**: OCR, table extraction, and structure preservation
- **Flexible Output**: Markdown, JSON, or plain text formats
- **Batch Processing**: Handle multiple documents efficiently
- **Metadata Extraction**: Detailed document structure and properties
- **Production Ready**: Robust error handling and file size limits

## 📋 Tools Available

This MCP server exposes three main tools:

### 1. `process_document`
Process a single document and return the converted content.

**Parameters:**
- `file_path` (string): Path to the document file
- `output_format` (string): "markdown", "json", or "text" (default: "markdown")
- `extract_images` (boolean): Whether to extract and describe images (default: false)
- `extract_tables` (boolean): Whether to extract table structure (default: true)

**Example:**
```
process_document("report.pdf", "markdown", true, true)
```

### 2. `batch_process_documents`
Process multiple documents in batch with optional file output.

**Parameters:**
- `file_paths` (array): List of document file paths (max 20 files)
- `output_format` (string): Output format for all documents (default: "markdown")
- `output_directory` (string): Directory to save files (empty = return content)

**Example:**
```
batch_process_documents(["doc1.pdf", "doc2.docx"], "markdown", "/output")
```

### 3. `extract_document_metadata`
Extract detailed metadata and structure information from a document.

**Parameters:**
- `file_path` (string): Path to the document file

**Example:**
```
extract_document_metadata("report.pdf")
```

## 🛠 Installation

### For Goose Users

#### Option 1: Standard Installation
1. Install the MCP server:
```bash
pip install mcp-gosling
```

2. Add to your Goose configuration:
```json
{
  "mcpServers": {
    "gosling": {
      "command": "mcp-gosling",
      "args": []
    }
  }
}
```

#### Option 2: Using uvx (Modern)
1. Ensure uv is installed:
```bash
pip install uv
```

2. Add to your Goose configuration:
```json
{
  "mcpServers": {
    "gosling": {
      "command": "uvx",
      "args": ["mcp-gosling"]
    }
  }
}
```

### For MCP Development

1. Clone and install:
```bash
git clone https://github.com/masanderso/mcp-gosling.git
cd mcp-gosling
pip install -e .
```

2. Test with MCP Inspector:
```bash
mcp dev src/mcp_docling/server.py
```

## 🔧 Configuration

The server automatically configures Docling with optimal settings:
- OCR enabled for scanned documents
- Table structure extraction with cell matching
- Support for all major document formats
- 50MB file size limit for safety

## 🎯 Use Cases

- **Research**: Extract content from academic papers and reports
- **Business**: Process contracts, invoices, and presentations  
- **Data Extraction**: Convert documents to structured data
- **Content Migration**: Bulk convert document formats
- **Analysis**: Extract metadata and document structure

## 🏗 Architecture

This server follows the MCP (Model Context Protocol) specification:
- **Tools**: Document processing functions exposed to AI assistants
- **STDIO Transport**: Communication via standard input/output
- **Error Handling**: Proper MCP error responses
- **Type Safety**: Full type annotations and validation

## 🤝 Integration Examples

### With Goose
```
"Process the quarterly report in /documents/q4-report.pdf and summarize the key findings"
```

### With other MCP clients
```python
# Call the process_document tool
result = await client.call_tool("process_document", {
    "file_path": "/path/to/document.pdf",
    "output_format": "markdown"
})
```

## 📊 Performance

- **Speed**: Optimized for production workloads
- **Memory**: Efficient processing of large documents
- **Reliability**: Robust error handling and validation
- **Scalability**: Suitable for batch processing workflows

## 🐛 Troubleshooting

Common issues and solutions:

- **File not found**: Ensure file paths are absolute and accessible
- **Large files**: Files over 50MB are rejected for safety
- **Format errors**: Check that file format is supported
- **Memory issues**: Process large batches in smaller chunks

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 🔗 Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [IBM Docling Library](https://github.com/DS4SD/docling)
- [Goose AI Assistant](https://block.github.io/goose/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
