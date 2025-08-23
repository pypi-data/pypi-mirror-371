#!/usr/bin/env python3
"""
🎯 WOT-PDF PRODUCTION BUILDER - Production-Ready Markdown→Typst→PDF
================================================================
🚀 Optimized end-to-end pipeline with caching, metadata extraction, and cross-platform support
📊 Smart diagram rendering with hash-based caching and idempotent builds
🎨 Auto-caption and label extraction from diagram comments

FEATURES:
- Hash-based SVG caching for performance
- Caption/label extraction from diagram comments
- Cross-platform CLI detection (Windows/Linux/macOS)
- Markdown image processing with {#fig:label} support
- List of Figures/Tables generation
- Idempotent builds with intelligent change detection
"""

import os
import re
import sys
import subprocess
import hashlib
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

# WOT-PDF integration
from wot_pdf.core.base_engine import BaseEngine
from wot_pdf.utils.logger import setup_logger


@dataclass
class DiagramMetadata:
    """Metadata extracted from diagram"""
    caption: Optional[str] = None
    label: Optional[str] = None
    hash: Optional[str] = None
    language: Optional[str] = None


@dataclass
class BuildStats:
    """Statistics for build process"""
    diagrams_processed: int = 0
    diagrams_cached: int = 0
    diagrams_rendered: int = 0
    images_processed: int = 0
    build_time_ms: float = 0.0
    cache_hit_rate: float = 0.0


# Supported diagram engines with CLI commands
SUPPORTED_ENGINES = {
    'mermaid': ('mmdc', ['-i', '{input}', '-o', '{output}', '--theme', 'default', '--backgroundColor', 'transparent']),
    'dot': ('dot', ['-Tsvg', '{input}', '-o', '{output}']),
    'graphviz': ('dot', ['-Tsvg', '{input}', '-o', '{output}']),
    'd2': ('d2', ['{input}', '{output}', '--theme', '0']),
    'plantuml': ('plantuml', ['-tsvg', '{input}']),
}

# Caption extraction patterns for different languages
CAPTION_PATTERNS = {
    'mermaid': r'^\s*%%\s*caption:\s*(.+)$',
    'plantuml': r'^\s*\'\s*caption:\s*(.+)$|^\s*%%\s*caption:\s*(.+)$',
    'd2': r'^\s*#\s*caption:\s*(.+)$',
    'dot': r'^\s*//\s*caption:\s*(.+)$|^\s*/\*\s*caption:\s*(.+)\s*\*/',
    'graphviz': r'^\s*//\s*caption:\s*(.+)$|^\s*/\*\s*caption:\s*(.+)\s*\*/',
}

# Label extraction patterns for different languages
LABEL_PATTERNS = {
    'mermaid': r'^\s*%%\s*label:\s*(fig:[\w\-_]+)$',
    'plantuml': r'^\s*\'\s*label:\s*(fig:[\w\-_]+)$|^\s*%%\s*label:\s*(fig:[\w\-_]+)$',
    'd2': r'^\s*#\s*label:\s*(fig:[\w\-_]+)$',
    'dot': r'^\s*//\s*label:\s*(fig:[\w\-_]+)$|^\s*/\*\s*label:\s*(fig:[\w\-_]+)\s*\*/',
    'graphviz': r'^\s*//\s*label:\s*(fig:[\w\-_]+)$|^\s*/\*\s*label:\s*(fig:[\w\-_]+)\s*\*/',
}


class ProductionDiagramBuilder:
    """Production-ready diagram builder with caching and metadata extraction"""
    
    def __init__(self, 
                 output_dir: Path = Path('diagrams'),
                 cache_enabled: bool = True,
                 logger: Optional[logging.Logger] = None):
        
        self.output_dir = output_dir
        self.cache_enabled = cache_enabled
        self.logger = logger or setup_logger(__name__)
        
        # CLI availability cache
        self._cli_cache: Dict[str, bool] = {}
        
        # Build statistics
        self.stats = BuildStats()
        
        # Auto-install CLI tools if missing
        self._ensure_cli_tools()
        
        self.logger.info(f"🚀 Production Diagram Builder initialized (cache: {cache_enabled})")
    
    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH with caching"""
        if command in self._cli_cache:
            return self._cli_cache[command]
            
        try:
            # Try to run command with --version or --help
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            try:
                # Try with --help
                result = subprocess.run([command, '--help'], 
                                      capture_output=True, 
                                      timeout=5)
                available = result.returncode == 0
            except:
                available = False
        
        self._cli_cache[command] = available
        return available
    
    def _ensure_cli_tools(self):
        """Auto-install missing CLI tools"""
        missing_tools = []
        
        for lang, (command, _) in SUPPORTED_ENGINES.items():
            if not self._is_command_available(command):
                missing_tools.append((lang, command))
        
        if missing_tools:
            self.logger.warning(f"🔧 Missing CLI tools: {[f'{lang}({cmd})' for lang, cmd in missing_tools]}")
            self._install_missing_tools(missing_tools)
    
    def _install_missing_tools(self, missing_tools: List[Tuple[str, str]]):
        """Install missing CLI tools automatically"""
        install_commands = {
            'mermaid': 'npm install -g @mermaid-js/mermaid-cli',
            'dot': 'choco install graphviz',  # Windows
            'd2': 'curl -fsSL https://d2lang.com/install.sh | sh',
            'plantuml': 'choco install plantuml'
        }
        
        for lang, cmd in missing_tools:
            if cmd in install_commands:
                self.logger.info(f"🔨 Auto-installing {cmd} for {lang} diagrams...")
                try:
                    install_cmd = install_commands[cmd]
                    if sys.platform.startswith('win'):
                        # Windows installation
                        if 'npm install' in install_cmd:
                            subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True, capture_output=True)
                        elif 'choco install' in install_cmd:
                            subprocess.run(['choco', 'install', cmd, '-y'], check=True, capture_output=True)
                    else:
                        # Linux/macOS installation  
                        subprocess.run(install_cmd, shell=True, check=True, capture_output=True)
                    
                    self.logger.info(f"✅ Successfully installed {cmd}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"❌ Failed to install {cmd}: {e}")
                    self.logger.info(f"💡 Manual install: {install_commands[cmd]}")
                except FileNotFoundError:
                    self.logger.warning(f"❌ Installer not found for {cmd}")
                    self.logger.info(f"💡 Manual install: {install_commands[cmd]}")
    
    def download_image(self, url: str) -> str:
        """Download image from URL and cache locally"""
        try:
            # Create cache directory for images
            cache_dir = Path("image_cache")
            cache_dir.mkdir(exist_ok=True)
            
            # Generate cache filename from URL hash
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
            url_parsed = urllib.parse.urlparse(url)
            extension = Path(url_parsed.path).suffix or '.jpg'
            cache_file = cache_dir / f"img_{url_hash}{extension}"
            
            # Return cached file if exists
            if cache_file.exists():
                self.logger.info(f"📁 Using cached image: {cache_file}")
                return str(cache_file)
            
            # Download image
            self.logger.info(f"⬇️ Downloading image: {url}")
            headers = {'User-Agent': 'WOT-PDF/1.2.0 (PDF Generator)'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    with open(cache_file, 'wb') as f:
                        f.write(response.read())
                    self.logger.info(f"✅ Downloaded: {cache_file}")
                    return str(cache_file)
                else:
                    raise Exception(f"HTTP {response.status}")
                    
        except Exception as e:
            self.logger.warning(f"❌ Failed to download image {url}: {e}")
            return url  # Return original URL as fallback
    
    def find_diagram_blocks(self, md_text: str) -> List[Tuple[str, str, re.Match]]:
        """Find all diagram code blocks in Markdown"""
        blocks = []
        
        # Find fenced code blocks
        pattern = r'```(\w+)\n(.*?)\n```'
        for match in re.finditer(pattern, md_text, re.DOTALL):
            lang = match.group(1).lower()
            code = match.group(2)
            
            if lang in SUPPORTED_ENGINES:
                blocks.append((lang, code, match))
        
        return blocks
    
    def extract_metadata(self, lang: str, code: str) -> DiagramMetadata:
        """Extract caption and label from diagram code"""
        metadata = DiagramMetadata(language=lang)
        
        # Extract caption
        if lang in CAPTION_PATTERNS:
            cap_pattern = re.compile(CAPTION_PATTERNS[lang], re.IGNORECASE | re.MULTILINE)
            cap_match = cap_pattern.search(code)
            if cap_match:
                # Get first non-None group
                metadata.caption = next((g for g in cap_match.groups() if g), None)
        
        # Extract label
        if lang in LABEL_PATTERNS:
            lab_pattern = re.compile(LABEL_PATTERNS[lang], re.IGNORECASE | re.MULTILINE)
            lab_match = lab_pattern.search(code)
            if lab_match:
                metadata.label = lab_match.group(1)
        
        # Generate hash
        metadata.hash = hashlib.md5(code.encode('utf-8')).hexdigest()[:8]
        
        # Auto-generate label if not provided
        if not metadata.label:
            metadata.label = f'fig:{metadata.hash}'
        
        # Auto-generate caption if not provided
        if not metadata.caption:
            metadata.caption = f'Diagram {metadata.hash}'
        
        return metadata
    
    def check_cli_availability(self, command: str) -> bool:
        """Check if CLI command is available (with caching)"""
        if command in self._cli_cache:
            return self._cli_cache[command]
        
        try:
            # Try different ways to check command availability
            if command == 'mmdc':
                result = subprocess.run([command, '--version'], 
                                      capture_output=True, timeout=5, check=False)
            elif command == 'dot':
                result = subprocess.run([command, '-V'], 
                                      capture_output=True, timeout=5, check=False)
            elif command == 'd2':
                result = subprocess.run([command, '--version'], 
                                      capture_output=True, timeout=5, check=False)
            elif command == 'plantuml':
                # PlantUML might be available as jar or command
                result = subprocess.run([command, '-version'], 
                                      capture_output=True, timeout=5, check=False)
                if result.returncode != 0:
                    # Try java -jar plantuml.jar
                    result = subprocess.run(['java', '-jar', 'plantuml.jar', '-version'], 
                                          capture_output=True, timeout=5, check=False)
            else:
                result = subprocess.run([command, '--help'], 
                                      capture_output=True, timeout=5, check=False)
            
            available = result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            available = False
        
        self._cli_cache[command] = available
        return available
    
    def render_diagram(self, lang: str, code: str, metadata: DiagramMetadata) -> Path:
        """Render diagram to SVG with caching"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output path
        svg_path = self.output_dir / f'{lang}_{metadata.hash}.svg'
        
        # Check cache
        if self.cache_enabled and svg_path.exists():
            self.logger.info(f"• SKIP (cache) {svg_path}")
            self.stats.diagrams_cached += 1
            return svg_path
        
        # Get engine configuration
        if lang not in SUPPORTED_ENGINES:
            raise ValueError(f"Unsupported diagram language: {lang}")
        
        command, args_template = SUPPORTED_ENGINES[lang]
        
        # Check CLI availability
        if not self.check_cli_availability(command):
            raise RuntimeError(f'CLI tool not installed or not in PATH: {command}')
        
        # Create temporary input file
        temp_input = Path(f'.tmp_{lang}_{metadata.hash}.{lang}')
        temp_input.write_text(code, encoding='utf-8')
        
        try:
            # Prepare command arguments
            real_args = []
            for arg in args_template:
                formatted_arg = arg.format(
                    input=str(temp_input),
                    output=str(svg_path)
                )
                real_args.append(formatted_arg)
            
            # Execute rendering command
            self.logger.info(f"🔨 Rendering {lang} diagram: {command} {' '.join(real_args)}")
            
            result = subprocess.run(
                [command] + real_args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise RuntimeError(f'Diagram rendering failed for {lang}: {error_msg}')
            
            # Verify output was created
            if not svg_path.exists():
                raise RuntimeError(f'SVG output not created: {svg_path}')
            
            self.logger.info(f"✅ Rendered {svg_path}")
            self.stats.diagrams_rendered += 1
            
            return svg_path
        
        finally:
            # Cleanup temporary files
            temp_input.unlink(missing_ok=True)
    
    def process_markdown_images(self, text: str) -> str:
        """Process Markdown images with enhanced caption and label support"""
        processed_text = text
        
        # Pattern 1: ![alt](path){#fig:label} - explicit label
        explicit_label_pattern = r'!\[([^\]]*)\]\(([^)]+)\)\s*\{#(fig:[\w\-_]+)\}'
        
        # Pattern 2: ![alt](path) - auto-generate label
        simple_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)(?!\s*\{)'
        
        def replace_explicit_image(match: re.Match) -> str:
            alt_text = match.group(1)
            image_path = match.group(2)
            label = match.group(3)
            
            # Download image if it's a URL
            if image_path.startswith(('http://', 'https://')):
                local_path = self.download_image(image_path)
            else:
                local_path = image_path
            
            # Use alt text as caption, fallback to generic
            caption = alt_text.strip() if alt_text.strip() else f"Slika {label.split(':')[-1]}"
            
            typst_figure = (
                f'#figure(\n'
                f'  image("{local_path}", width: 80%),\n'
                f'  caption: [{caption}],\n'
                f') <{label}>\n'
            )
            
            self.stats.images_processed += 1
            return typst_figure
        
        def replace_simple_image(match: re.Match) -> str:
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # Download image if it's a URL
            if image_path.startswith(('http://', 'https://')):
                local_path = self.download_image(image_path)
            else:
                local_path = image_path
            
            # Generate hash-based label for auto-labeling
            image_hash = hashlib.md5(local_path.encode('utf-8')).hexdigest()[:8]
            label = f"fig:img_{image_hash}"
            
            # Use alt text as caption, fallback to filename
            if alt_text.strip():
                caption = alt_text.strip()
            else:
                # Extract filename without extension as caption
                filename = Path(local_path).stem
                caption = filename.replace('_', ' ').replace('-', ' ').title()
            
            typst_figure = (
                f'#figure(\n'
                f'  image("{local_path}", width: 80%),\n'
                f'  caption: [{caption}],\n'
                f') <{label}>\n'
            )
            
            self.stats.images_processed += 1
            return typst_figure
        
        # First replace explicit labels
        processed_text = re.sub(explicit_label_pattern, replace_explicit_image, processed_text)
        
        # Then replace simple images (that don't already have labels)
        processed_text = re.sub(simple_image_pattern, replace_simple_image, processed_text)
        
        return processed_text
    
    def process_markdown_tables(self, text: str) -> str:
        """Process Markdown tables with caption and label support"""
        # Pattern to find table caption comments before tables
        # <!-- caption: Table caption text -->
        # <!-- label: tbl:tablename -->
        # <!-- position: top | bottom -->
        # | Header 1 | Header 2 |
        # |----------|----------|
        # | Data 1   | Data 2   |
        
        # Find all table patterns with optional captions
        table_pattern = r'(?:<!--\s*caption:\s*([^>]+)\s*-->\s*\n)?(?:<!--\s*label:\s*(tbl:[\w\-_]+)\s*-->\s*\n)?(?:<!--\s*position:\s*(top|bottom)\s*-->\s*\n)?\s*(\|[^\n]+\|\s*\n(?:\|[\s\-:]+\|\s*\n)?(?:\|[^\n]+\|\s*\n)*)'
        
        def convert_markdown_table_to_typst(table_content: str) -> str:
            """Convert Markdown table syntax to Typst table() syntax"""
            lines = table_content.strip().split('\n')
            table_rows = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or not line.startswith('|'):
                    continue
                    
                # Skip separator lines (contain only |, -, :, spaces)
                if re.match(r'^\|[\s\-:]+\|$', line):
                    continue
                
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
                if cells:
                    # Filter out cells that look like separator rows
                    if not all(re.match(r'^[\s\-:]*$', cell) for cell in cells):
                        table_rows.append(cells)
            
            if not table_rows:
                return "table()"
            
            # Determine column count
            max_cols = max(len(row) for row in table_rows) if table_rows else 0
            
            # Build Typst table syntax
            typst_cells = []
            for row in table_rows:
                # Pad row to max columns
                while len(row) < max_cols:
                    row.append("")
                
                # Add cells to typst format
                for cell in row:
                    # Escape special characters for Typst content blocks
                    # In Typst content blocks [...]:
                    # - $ starts math mode, so needs escaping as \$
                    # - [ ] are reserved for content blocks
                    # - \ is escape character  
                    escaped_cell = (cell.replace('\\', '\\\\')
                                       .replace('$', '\\$')
                                       .replace('[', '\\[')
                                       .replace(']', '\\]'))
                    typst_cells.append(f'[{escaped_cell}]')
            
            # Create Typst table
            cells_str = ',\n    '.join(typst_cells)
            typst_table = f'  table(\n    columns: {max_cols},\n    {cells_str},\n  )'
            
            return typst_table
        
        def replace_table(match: re.Match) -> str:
            caption_comment = match.group(1)
            label_comment = match.group(2)
            position_comment = match.group(3)
            table_content = match.group(4)
            
            # Generate auto-label if not provided
            if not label_comment:
                table_hash = hashlib.md5(table_content.encode('utf-8')).hexdigest()[:8]
                label = f"tbl:table_{table_hash}"
            else:
                label = label_comment
            
            # Use caption or generate from first header
            if caption_comment:
                caption = caption_comment.strip()
            else:
                # Extract first row as caption base
                first_row = table_content.split('\n')[0]
                headers = [h.strip() for h in first_row.split('|')[1:-1]]  # Remove empty first/last
                if headers:
                    caption = f"Tabela podatkov: {', '.join(headers[:3])}" + ("..." if len(headers) > 3 else "")
                else:
                    caption = f"Tabela {label.split(':')[-1]}"
            
            # Convert Markdown table to Typst table syntax
            typst_table_content = convert_markdown_table_to_typst(table_content)
            
            # Generate shorter, cleaner caption for better outline display
            clean_caption = caption
            if len(caption) > 60:
                # For long captions, create shorter version
                if ":" in caption:
                    parts = caption.split(":")
                    main_part = parts[0].strip()
                    # Keep max 50 chars for main part
                    clean_caption = main_part[:47] + "..." if len(main_part) > 50 else main_part
                else:
                    clean_caption = caption[:57] + "..."
            
            # Determine caption position (top by default, bottom if specified)
            position = "top"
            if position_comment and position_comment.strip().lower() == "bottom":
                position = "bottom"
            
            # Convert to Typst table figure with position
            if position == "bottom":
                typst_table = f'#figure(\n{typst_table_content},\n  caption: [{clean_caption}],\n  placement: bottom,\n) <{label}>\n'
            else:
                typst_table = f'#figure(\n{typst_table_content},\n  caption: [{clean_caption}],\n) <{label}>\n'
            
            return typst_table
        
        # Apply table processing
        processed_text = re.sub(table_pattern, replace_table, text, flags=re.MULTILINE)
        
        return processed_text
    
    def convert_markdown_to_typst(self, text: str) -> str:
        """Convert basic Markdown syntax to Typst syntax"""
        # Convert headings: ## Header → = Header 
        text = re.sub(r'^####\s+(.+)$', r'==== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^###\s+(.+)$', r'=== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'== \1', text, flags=re.MULTILINE)
        text = re.sub(r'^#\s+(.+)$', r'= \1', text, flags=re.MULTILINE)
        
        # Convert bold: **text** → *text*
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        
        # Convert italic: *text* → _text_ (but avoid conflicts with bold)
        # Only convert single asterisks that aren't part of ** patterns
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'_\1_', text)
        
        # Convert inline code: `code` → `code` (already correct)
        # No change needed for inline code
        
        # Convert cross-references: [text](#tbl:label) → @tbl:label or [text](#label) → @label
        text = re.sub(r'\[([^\]]+)\]\(#(tbl:[^)]+)\)', r'@\2', text)
        text = re.sub(r'\[([^\]]+)\]\(#(fig:[^)]+)\)', r'@\2', text)
        
        return text
    
    def md_to_typst(self, md_path: Path, typ_path: Path) -> BuildStats:
        """Convert Markdown to Typst with diagram processing"""
        start_time = datetime.now()
        
        # Reset stats
        self.stats = BuildStats()
        
        self.logger.info(f"📄 Converting {md_path} → {typ_path}")
        
        # Read Markdown content
        try:
            markdown_text = md_path.read_text(encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to read Markdown file: {e}")
        
        # Find diagram blocks
        diagram_blocks = self.find_diagram_blocks(markdown_text)
        self.stats.diagrams_processed = len(diagram_blocks)
        
        self.logger.info(f"🔍 Found {len(diagram_blocks)} diagram blocks")
        
        # Process diagram blocks
        def replace_diagram_block(match: re.Match) -> str:
            lang = match.group(1).lower()
            code = match.group(2)
            
            # Extract metadata
            metadata = self.extract_metadata(lang, code)
            
            # Render diagram
            try:
                svg_path = self.render_diagram(lang, code, metadata)
            except Exception as e:
                self.logger.error(f"Failed to render {lang} diagram: {e}")
                # Return original block on error
                return match.group(0)
            
            # Generate Typst figure
            typst_figure = (
                f'#figure(\n'
                f'  image("{svg_path.as_posix()}", width: 80%),\n'
                f'  caption: [{metadata.caption}],\n'
                f') <{metadata.label}>\n'
            )
            
            return typst_figure
        
        # Replace diagram blocks
        processed_text = re.sub(
            r'```(\w+)\n(.*?)\n```',
            replace_diagram_block,
            markdown_text,
            flags=re.DOTALL
        )
        
        # Process regular Markdown images
        processed_text = self.process_markdown_images(processed_text)
        
        # Process Markdown tables
        processed_text = self.process_markdown_tables(processed_text)
        
        # Convert remaining Markdown syntax to Typst
        processed_text = self.convert_markdown_to_typst(processed_text)
        
        # Add Typst header
        typst_header = self._generate_typst_header()
        
        # Write Typst file
        try:
            typ_path.write_text(typst_header + processed_text, encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to write Typst file: {e}")
        
        # Calculate statistics
        end_time = datetime.now()
        self.stats.build_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if self.stats.diagrams_processed > 0:
            self.stats.cache_hit_rate = (self.stats.diagrams_cached / self.stats.diagrams_processed) * 100
        
        self.logger.info(f"✅ Typst conversion completed: {typ_path}")
        self.logger.info(f"📊 Stats: {self.stats.diagrams_processed} diagrams, {self.stats.diagrams_cached} cached, {self.stats.cache_hit_rate:.1f}% cache hit rate")
        
        return self.stats
    
    def _generate_typst_header(self) -> str:
        """Generate enhanced Typst document header with list functions"""
        return '''#set heading(numbering: "1.")
#set page(numbering: "1", margin: 2cm)
#set text(font: "Arial", size: 11pt)
#set par(leading: 0.65em)

// Enhanced helper functions for lists with clickable links
#let list_of_figures() = {
  heading(level: 1, "Seznam slik", numbering: none)
  let fig_counter = 1
  for f in query(figure.where(kind: image)) {
    let n = f.counter.display()
    let loc = f.location()
    [Slika #n: #link(loc)[#f.caption.body]]
    linebreak()
  }
}

#let list_of_tables() = {
  heading(level: 1, "Seznam tabel", numbering: none) 
  for t in query(figure.where(kind: table)) {
    let n = t.counter.display()
    let loc = t.location()
    [Tabela #n: #link(loc)[#t.caption.body]]
    linebreak()
  }
}

// Quick reference function for all figures and tables
#let list_of_all_figures() = {
  heading(level: 1, "Seznam slik in tabel", numbering: none)
  
  // Figures
  let figures = query(figure.where(kind: image))
  if figures.len() > 0 {
    heading(level: 2, "Slike", numbering: none)
    for f in figures {
      let n = f.counter.display()
      let loc = f.location()
      [Slika #n: #link(loc)[#f.caption.body]]
      linebreak()
    }
  }
  
  // Tables
  let tables = query(figure.where(kind: table))
  if tables.len() > 0 {
    heading(level: 2, "Tabele", numbering: none)
    for t in tables {
      let n = t.counter.display() 
      let loc = t.location()
      [Tabela #n: #link(loc)[#t.caption.body]]
      linebreak()
    }
  }
}

// Document outline
#outline(depth: 3)
#pagebreak()

// Lists (uncomment as needed)
// #list_of_figures()
// #pagebreak()
// #list_of_tables()
// #pagebreak()
// #list_of_all_figures()
// #pagebreak()

'''


class WOTPDFProductionEngine(BaseEngine):
    """WOT-PDF engine integration for production builder"""
    
    def __init__(self):
        super().__init__()
        self.builder = ProductionDiagramBuilder()
        self.logger = setup_logger(self.__class__.__name__)
    
    def generate_pdf(self, input_file: str, output_file: str, **kwargs) -> Dict:
        """Generate PDF using production builder + Typst"""
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Determine intermediate files
        if input_path.suffix.lower() == '.md':
            # Markdown → Typst → PDF
            typst_path = input_path.with_suffix('.typ')
            
            # Convert MD to Typst
            stats = self.builder.md_to_typst(input_path, typst_path)
            
            # Compile Typst to PDF
            result = self._compile_typst(typst_path, output_path)
            
            return {
                'success': result['success'],
                'output_file': str(output_path),
                'intermediate_file': str(typst_path),
                'stats': {
                    'diagrams_processed': stats.diagrams_processed,
                    'diagrams_cached': stats.diagrams_cached,
                    'cache_hit_rate': stats.cache_hit_rate,
                    'build_time_ms': stats.build_time_ms
                },
                'message': result.get('message', 'PDF generated successfully')
            }
        
        elif input_path.suffix.lower() == '.typ':
            # Typst → PDF
            return self._compile_typst(input_path, output_path)
        
        else:
            return {
                'success': False,
                'message': f'Unsupported input format: {input_path.suffix}'
            }
    
    def _compile_typst(self, typst_path: Path, pdf_path: Path) -> Dict:
        """Compile Typst to PDF"""
        try:
            # Check if Typst is installed
            result = subprocess.run(
                ['typst', 'compile', str(typst_path), str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ PDF compiled: {pdf_path}")
                return {
                    'success': True,
                    'output_file': str(pdf_path),
                    'message': 'PDF compiled successfully'
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown Typst error"
                self.logger.error(f"❌ Typst compilation failed: {error_msg}")
                return {
                    'success': False,
                    'message': f'Typst compilation failed: {error_msg}'
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Typst compilation timed out'
            }
        
        except FileNotFoundError:
            return {
                'success': False,
                'message': 'Typst not installed or not in PATH'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Typst compilation error: {str(e)}'
            }
    
    def get_engine_info(self) -> Dict:
        """Get engine information"""
        # Check CLI availability
        cli_status = {}
        for engine, (command, _) in SUPPORTED_ENGINES.items():
            cli_status[engine] = self.builder.check_cli_availability(command)
        
        return {
            'name': 'WOT-PDF Production Engine',
            'version': '1.2.0',
            'supported_inputs': ['.md', '.typ'],
            'supported_outputs': ['.pdf'],
            'features': [
                'Diagram rendering with caching',
                'Caption/label extraction',
                'Markdown image processing',
                'List of figures/tables generation'
            ],
            'diagram_engines': cli_status,
            'cache_enabled': self.builder.cache_enabled
        }


# CLI Interface
def main():
    """Main CLI entry point for production builder"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WOT-PDF Production Builder')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('output', nargs='?', help='Output Typst file (optional)')
    parser.add_argument('--pdf', action='store_true', help='Also compile to PDF')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--diagrams-dir', default='diagrams', help='Diagrams output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('production_builder', level=logging.DEBUG if args.verbose else logging.INFO)
    
    # Determine output file
    input_path = Path(args.input)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.typ')
    
    # Create builder
    builder = ProductionDiagramBuilder(
        output_dir=Path(args.diagrams_dir),
        cache_enabled=not args.no_cache,
        logger=logger
    )
    
    try:
        # Convert MD to Typst
        stats = builder.md_to_typst(input_path, output_path)
        
        logger.info(f"📊 Build Statistics:")
        logger.info(f"  • Diagrams processed: {stats.diagrams_processed}")
        logger.info(f"  • Diagrams cached: {stats.diagrams_cached}")
        logger.info(f"  • Images processed: {stats.images_processed}")
        logger.info(f"  • Cache hit rate: {stats.cache_hit_rate:.1f}%")
        logger.info(f"  • Build time: {stats.build_time_ms:.1f}ms")
        
        # Optionally compile to PDF
        if args.pdf:
            engine = WOTPDFProductionEngine()
            pdf_path = output_path.with_suffix('.pdf')
            
            result = engine._compile_typst(output_path, pdf_path)
            
            if result['success']:
                logger.info(f"🎉 Complete pipeline success: {input_path} → {output_path} → {pdf_path}")
            else:
                logger.error(f"❌ PDF compilation failed: {result['message']}")
                sys.exit(1)
        
        logger.info("✅ Production build completed successfully!")
    
    except Exception as e:
        logger.error(f"❌ Build failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
