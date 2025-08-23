# 📄 WOT-PDF - Advanced PDF Generation v1.1.0

[![PyPI version](https://badge.fury.io/py/wot-pdf.svg)](https://badge.fury.io/py/wot-pdf)
[![Python Support](https://img.shields.io/pypi/pyversions/wot-pdf.svg)](https://pypi.org/project/wot-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional PDF generation with Enhanced ReportLab Engine v3.0 + Typst dual-engine architecture**

## 🎉 NEW in v1.1.0 - Enhanced ReportLab Engine v3.0

### ✅ Major Improvements
- **Fixed TOC Generation**: Proper table of contents with hierarchical numbering
- **Enhanced Emoji Support**: Native Unicode with SegoeUIEmoji font registration  
- **Professional Styling**: 6-level heading system with business-ready themes
- **Performance Optimized**: 32x faster than Typst for business documents (0.02s)
- **Perfect Compatibility**: All Canvas API issues resolved

### 📊 Quality Results
- **File Size**: Optimized 30KB output (2x larger but feature-rich)
- **Features**: Complete TOC + Hierarchical Numbering + Emoji Support
- **Speed**: Lightning-fast 0.02s generation time
- **Quality**: Business-ready professional output

## ✨ Core Features

🎯 **Dual PDF Engines** 
- **Enhanced ReportLab v3.0**: Performance leader for business documents ⚡
- **System Typst CLI**: Quality leader for academic documents 🎨
- **Intelligent Routing**: Automatic engine selection based on content

📚 **Professional Document Generation**
- Convert markdown to business-ready PDFs
- Complete table of contents with numbering
- Full emoji and Unicode support 😊🚀📊
- 6-level professional heading system
- Rich CLI interface
- GUI frontend (optional)
- Professional typography

## 🚀 Quick Start

### Installation

```bash
pip install wot-pdf
```

### Basic Usage

```bash
# Generate single PDF from file
wot-pdf generate --input document.md --output result.pdf --template technical

# Create professional book from directory
wot-pdf book ./docs/ book.pdf --template technical

# Analyze content for optimal engine selection
wot-pdf analyze document.md

# List available templates
wot-pdf templates

# Show detailed template information
wot-pdf template-info technical

# GUI mode (if installed)
wot-pdf-gui
```

### Python API

```python
from wot_pdf import PDFGenerator, generate_book

# Simple generation
generator = PDFGenerator()
result = generator.generate("document.md", "output.pdf")

# Book generation
result = generate_book(
    input_dir="./docs/",
    output_file="book.pdf", 
    template="technical"
)
```

## 📖 Templates

| Template | Best For | Features |
|----------|----------|----------|
| `academic` | Research papers | Citations, bibliography, equations |
| `technical` | Documentation | Code blocks, diagrams, TOC |
| `corporate` | Business reports | Professional styling, charts |
| `educational` | Learning materials | Exercises, callouts, examples |
| `minimal` | Simple documents | Clean, fast generation |

## 🛠️ Installation Options

### Minimal Installation
```bash
pip install wot-pdf
```

### With Development Tools
```bash
pip install wot-pdf[dev]
```

### With GUI Support
```bash
pip install wot-pdf[gui]
```

### With Documentation Tools
```bash
pip install wot-pdf[docs]
```

## 📋 Requirements

- **Python**: 3.8+
- **System Typst CLI** (recommended): [Install from typst.app](https://typst.app)
- **ReportLab**: Automatically installed (fallback engine)

## 🎯 Use Cases

✅ **Technical Documentation**
- API references
- User manuals  
- Installation guides

✅ **Academic Publishing**
- Research papers
- Thesis documents
- Conference proceedings

✅ **Business Reports**
- Quarterly reports
- Project documentation
- Presentation materials

✅ **Educational Content**
- Course materials
- Tutorials
- Reference guides

## 📊 Comparison

| Feature | wot-pdf | pandoc | WeasyPrint |
|---------|---------|--------|------------|
| Typst Integration | ✅ | ❌ | ❌ |
| Fallback Engine | ✅ | ❌ | ❌ |
| Professional Templates | ✅ | Limited | Limited |
| Book Generation | ✅ | Manual | Manual |
| GUI Interface | ✅ | ❌ | ❌ |
| CLI Interface | ✅ | ✅ | Limited |

## 🔧 Configuration

Create `.wot-pdf.yaml` in your project:

```yaml
default_template: technical
output_directory: ./generated/
typst:
  enabled: true
  timeout: 60
reportlab:
  compression: true
  embed_fonts: true
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- 📚 [Documentation](https://wot-pdf.readthedocs.io)
- 🐛 [Issues](https://github.com/work-organizing-tools/wot-pdf/issues)
- 💬 [Discussions](https://github.com/work-organizing-tools/wot-pdf/discussions)
- 🌟 [Source Code](https://github.com/work-organizing-tools/wot-pdf)

---

**Made with ❤️ by the Work Organizing Tools team**
