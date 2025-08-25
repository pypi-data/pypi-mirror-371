# 📄 WOT-PDF - Advanced PDF Generation v1.2.2

[![PyPI version](https://badge.fury.io/py/wot-pdf.svg)](https://badge.fury.io/py/wot-pdf)
[![Python Support](https://img.shields.io/pypi/pyversions/wot-pdf.svg)](https://pypi.org/project/wot-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional PDF generation with Production Builder v1.2.2 + Complete CLI System**

## 🎉 NEW in v1.2.2 - Complete CLI & Intelligence System

### ✅ Major New Features
- **🧠 Intelligent Content Analysis**: Advanced content analyzer with engine recommendation
- **� Complete CLI System**: 8 professional commands with intelligent routing  
- **� Template Previews**: Generate previews for all templates with one command
- **🔍 Content Insight**: Analyze complexity, code blocks, and optimal engine selection
- **⚙️ Enhanced Engine Router**: Automatic Typst/ReportLab selection based on content analysis

### 🎛️ Complete CLI Commands
```bash
# Content Analysis & Recommendations  
wot-pdf analyze document.md --verbose      # Intelligent content analysis
wot-pdf templates                          # List all available templates
wot-pdf template-info technical           # Detailed template information

# PDF Generation
wot-pdf generate --input doc.md --output doc.pdf --template minimal
wot-pdf multi-template input.md --output-dir outputs --templates "minimal,technical"
wot-pdf create-previews --output-dir previews  # Generate all template previews

# Book Generation
wot-pdf book --input-dir ./docs --output book.pdf --template academic
wot-pdf version                           # System information
```

## 🆕 Previous v1.2.1 Features  
- **📝 Professional Code Highlighting**: Native Typst `#raw()` integration
- **🌐 Internet Image Support**: Download & cache images from URLs  
- **🔧 CLI Auto-Installation**: Intelligent detection & installation of diagram tools
- **⚡ Sub-60ms Performance**: Enterprise-grade build pipeline
- **🎯 All Limitations Resolved**: Complete feature parity achieved

## ✨ Core Features

🎯 **Production Builder v1.2.1**
- **Professional Code Highlighting**: 8+ languages with Typst native syntax
- **Internet Image Processing**: Auto-download & cache with hash-based system  
- **CLI Auto-Installation**: Smart detection for mermaid, dot, d2, plantuml
- **Advanced Table Processing**: Captions + cross-references + positioning
- **Enterprise Performance**: Sub-60ms builds with intelligent caching

🚀 **Dual PDF Engines** 
- **Enhanced ReportLab v3.0**: Performance leader for business documents ⚡
- **Production Typst Builder**: Quality leader for academic documents 🎨
- **Intelligent Routing**: Automatic engine selection based on content

📚 **Professional Document Generation**
- Convert markdown to production-ready PDFs
- Complete table of contents with numbering
- Full emoji and Unicode support 😊🚀📊
- Professional code blocks with syntax highlighting
- Internet image support with intelligent caching
- Rich CLI interface with auto-setup
- GUI frontend (optional)

## 🚀 Quick Start

### Installation

```bash
pip install wot-pdf
```

### Complete CLI System (v1.2.2)

```bash
# 🧠 Content Analysis & Intelligence
wot-pdf analyze document.md                    # Basic content analysis  
wot-pdf analyze document.md --verbose          # Detailed analysis with recommendations
wot-pdf templates                              # List all 10 available templates
wot-pdf template-info minimal                  # Detailed template information
wot-pdf version                                # System info: version, engines, templates

# 🎯 PDF Generation (with intelligent engine selection)
wot-pdf generate --input doc.md --output result.pdf --template minimal
wot-pdf generate --input doc.md --output tech.pdf --template technical --engine typst
wot-pdf generate --input doc.md --output corp.pdf --template corporate --verbose

# 📚 Multi-Template & Preview Generation
wot-pdf multi-template input.md --output-dir outputs --templates "minimal,technical,academic"
wot-pdf create-previews --output-dir previews  # Generate previews for ALL templates

# 📖 Book Generation from Directory
wot-pdf book --input-dir ./docs --output book.pdf --template academic --title "My Book"
```

### Enhanced Python API (v1.2.2)

```python
from wot_pdf import generate_pdf, generate_book, analyze_content_for_engine

# 🧠 Intelligent Generation with Content Analysis
analysis = analyze_content_for_engine("# My Document\n\n```python\nprint('hello')\n```")
print(f"Recommended engine: {analysis['engine']}")  # 'typst' for code-heavy content

# 🎯 Advanced PDF Generation
result = generate_pdf(
    input_content="document.md",
    output_file="output.pdf",
    template="technical",         # 10 templates available
    force_engine="typst",        # or "reportlab" 
    generate_toc=True,
    page_numbering="standard"
)

# 📖 Professional Book Generation  
result = generate_book(
    input_dir="./docs/",
    output_file="book.pdf",
    template="academic",
    title="Professional Guide", 
    author="Your Name",
    recursive=True
)
```

## 📖 Professional Templates (10 Available)

| Template | Best For | Key Features |
|----------|----------|--------------|
| `academic` | Research papers, theses | Citations, bibliography, equations, formal structure |
| `technical` | API docs, software manuals | Code syntax highlighting, diagrams, detailed TOC |
| `corporate` | Business reports, proposals | Professional styling, charts, executive summary |
| `educational` | Course materials, tutorials | Learning exercises, callouts, step-by-step guides |
| `minimal` | Simple documents, notes | Clean typography, fast generation, basic formatting |
| `creative` | Marketing, presentations | Modern design, visual elements, flexible layout |
| `magazine` | Articles, newsletters | Multi-column, image-rich, engaging typography |
| `scientific` | Research publications | Advanced equations, figures, academic formatting |
| `presentation` | Slides, handouts | Large fonts, visual hierarchy, presentation-ready |
| `handbook` | User guides, manuals | Structured sections, cross-references, appendices |

💡 **Template Preview Generation**: `wot-pdf create-previews --output-dir previews`

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
