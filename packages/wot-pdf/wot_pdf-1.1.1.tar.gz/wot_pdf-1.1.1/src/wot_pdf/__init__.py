"""
🎯 WOT-PDF - Advanced PDF Generation v1.1.1
============================================

Professional PDF generation with Enhanced ReportLab Engine v3.0:
- Enhanced ReportLab v3.0: Performance leader for business documents ⚡  
- Typst CLI: Quality leader for academic documents 🎨
- Intelligent routing: Automatic engine selection

NEW in v1.1.1:
- ✅ Fixed TOC generation with hierarchical numbering
- ✅ Enhanced emoji support (😊🚀📊✅) with font registration  
- ✅ Professional 6-level styling system
- ✅ Performance optimized (0.02s generation, 32x faster)
- ✅ Business-ready professional output quality
- ✅ Version synchronization and PyPI compatibility

Features:
- 📚 Professional document generation from markdown
- 🎨 5 professional templates
- ⚡ Advanced Typst integration
- 🔧 Rich CLI interface
- 📊 Professional output

Quick Start:
    >>> from wot_pdf import PDFGenerator, generate_book
    >>> generator = PDFGenerator()
    >>> result = generator.generate("doc.md", "output.pdf")
    >>> 
    >>> # Book generation
    >>> result = generate_book("./docs/", "book.pdf", template="technical")
"""

__version__ = "1.1.1"
__author__ = "Work Organizing Tools Team"
__email__ = "info@wot-tools.com"
__license__ = "MIT"

# Core API exports
from .core.generator import PDFGenerator
from .api.main_api import generate_pdf, generate_book, list_templates

def get_info():
    """Get package information"""
    return {
        "name": "WOT-PDF",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "engines": ["Typst", "ReportLab"],
        "templates": ["Academic", "Technical", "Corporate", "Educational", "Minimal"]
    }

# CLI entry point
from .cli import main as cli_main
from .core.generator import PDFGenerator
from .core.book_generator import BookGenerator
from .core.template_manager import TemplateManager

# High-level convenience functions
from .api.main_api import generate_pdf, generate_book, list_templates

# Template system
from .templates.template_registry import AVAILABLE_TEMPLATES

# CLI (imported only when needed)
# from .cli import main as cli_main

# All available templates
TEMPLATES = [
    "academic",     # Research papers with citations
    "technical",    # Documentation with code blocks
    "corporate",    # Business reports  
    "educational",  # Learning materials
    "minimal"       # Clean, simple design
]

def get_version():
    """Get wot-pdf version."""
    return __version__

def get_info():
    """Get package information."""
    return {
        "name": "wot-pdf", 
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "templates": TEMPLATES,
        "engines": ["typst", "reportlab"]
    }

# Convenience imports for common usage
__all__ = [
    # Core classes
    "PDFGenerator",
    "BookGenerator", 
    "TemplateManager",
    
    # High-level functions
    "generate_pdf",
    "generate_book",
    "list_templates",
    
    # Constants
    "TEMPLATES",
    "AVAILABLE_TEMPLATES",
    
    # Utilities
    "get_version",
    "get_info",
]
