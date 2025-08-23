#!/usr/bin/env python3
"""
🎯 ENHANCED DIAGRAM BUILDER - Production Ready
============================================
⚡ Advanced diagram rendering with caching, metadata, and Typst integration
🔷 Supports Mermaid, Graphviz, D2, PlantUML with intelligent fallbacks
📊 Part of WOT-PDF v1.2.0 - Diagram Enhancement Release

FEATURES:
- Smart caching based on content hash (idempotent)
- Metadata extraction (%% caption:, %% label:)
- Multi-platform CLI detection and execution
- Extended Markdown image support with {#fig:label}
- YAML configuration system
- Integration with existing wot-pdf templates
"""

import os
import re
import subprocess
import hashlib
import yaml
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from datetime import datetime

class EnhancedDiagramBuilder:
    """Enhanced diagram builder with caching, metadata, and configuration support"""
    
    # Supported diagram languages and their CLI commands
    SUPPORTED_ENGINES = {
        'mermaid': {
            'cmd': 'mmdc',
            'args': ['-i', '{input}', '-o', '{output}', '--backgroundColor', 'transparent'],
            'extensions': ['.mmd'],
            'description': 'Mermaid flowcharts and diagrams'
        },
        'dot': {
            'cmd': 'dot',
            'args': ['-Tsvg', '{input}', '-o', '{output}'],
            'extensions': ['.dot', '.gv'],
            'description': 'Graphviz DOT language'
        },
        'd2': {
            'cmd': 'd2',
            'args': ['{input}', '{output}'],
            'extensions': ['.d2'],
            'description': 'D2 declarative diagram language'
        },
        'plantuml': {
            'cmd': 'plantuml',
            'args': ['-tsvg', '{input}'],
            'extensions': ['.puml', '.plantuml'],
            'description': 'PlantUML unified modeling language'
        }
    }
    
    # Patterns for extracting metadata from diagram code
    METADATA_PATTERNS = {
        'caption': {
            'mermaid': r'^\s*%%\s*caption:\s*(.+)$',
            'plantuml': r'^\s*\'\s*caption:\s*(.+)$|^\s*%%\s*caption:\s*(.+)$',
            'd2': r'^\s*#\s*caption:\s*(.+)$',
            'dot': r'^\s*//\s*caption:\s*(.+)$|^\s*/\*\s*caption:\s*(.+)\s*\*/'
        },
        'label': {
            'mermaid': r'^\s*%%\s*label:\s*(fig:[\w\-]+)$',
            'plantuml': r'^\s*\'\s*label:\s*(fig:[\w\-]+)$|^\s*%%\s*label:\s*(fig:[\w\-]+)$',
            'd2': r'^\s*#\s*label:\s*(fig:[\w\-]+)$',
            'dot': r'^\s*//\s*label:\s*(fig:[\w\-]+)$|^\s*/\*\s*label:\s*(fig:[\w\-]+)\s*\*/'
        }
    }
    
    # Markdown image pattern with optional attributes
    MD_IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)(?:\{([^}]+)\})?'
    
    def __init__(self, config_path: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """Initialize enhanced diagram builder
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for output
        """
        self.logger = logger or self._setup_logger()
        self.config = self._load_config(config_path)
        self.cache_stats = {'hits': 0, 'misses': 0, 'errors': 0}
        
        # Verify CLI tools availability
        self._check_dependencies()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for diagram builder"""
        logger = logging.getLogger('wot_pdf.diagrams')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from YAML file with sensible defaults"""
        default_config = {
            'output_dir': 'diagrams',
            'cache_enabled': True,
            'typst_settings': {
                'margin': '2.5cm',
                'numbering': '"1."',
                'font_size': '11pt',
                'font_family': 'Liberation Sans'
            },
            'diagram_settings': {
                'default_width': '80%',
                'high_dpi': True,
                'background': 'transparent'
            },
            'document': {
                'include_toc': True,
                'include_lof': True,
                'include_lot': True,
                'page_numbering': True
            },
            'engines': {
                'mermaid': {'theme': 'neutral'},
                'dot': {'layout': 'dot', 'dpi': 300},
                'd2': {'theme': 'neutral'},
                'plantuml': {'style': 'plain'}
            }
        }
        
        # Try to load user configuration
        config_paths = [
            config_path,
            Path('.wot-pdf-diagrams.yaml'),
            Path('.build-config.yaml'),
            Path('wot-pdf.yaml')
        ]
        
        for path in config_paths:
            if path and path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = yaml.safe_load(f) or {}
                    
                    # Deep merge configurations
                    config = self._deep_merge_config(default_config, user_config)
                    self.logger.info(f"✓ Loaded config from {path}")
                    return config
                    
                except Exception as e:
                    self.logger.warning(f"Config error in {path}: {e}")
        
        self.logger.info("Using default configuration")
        return default_config
    
    def _deep_merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge user config into default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _check_dependencies(self):
        """Check which diagram engines are available"""
        self.available_engines = {}
        
        for engine, info in self.SUPPORTED_ENGINES.items():
            if self._has_cli(info['cmd']):
                self.available_engines[engine] = info
                self.logger.info(f"✓ {engine} engine available ({info['cmd']})")
            else:
                self.logger.warning(f"✗ {engine} engine not found ({info['cmd']})")
        
        if not self.available_engines:
            self.logger.error("No diagram engines available! Install at least one:")
            for engine, info in self.SUPPORTED_ENGINES.items():
                self.logger.error(f"  - {engine}: {info['description']}")
    
    def _has_cli(self, cmd: str) -> bool:
        """Check if CLI command is available"""
        try:
            result = subprocess.run(
                [cmd, '--help'], 
                capture_output=True, 
                timeout=10,
                check=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def find_diagram_blocks(self, md_text: str) -> List[Tuple[str, str, re.Match]]:
        """Extract code blocks with supported diagram languages"""
        blocks = []
        
        # Pattern for fenced code blocks
        pattern = r'```(\w+)\n(.*?)\n```'
        
        for match in re.finditer(pattern, md_text, re.DOTALL):
            lang = match.group(1).lower()
            code = match.group(2).strip()
            
            if lang in self.available_engines:
                blocks.append((lang, code, match))
                self.logger.debug(f"Found {lang} block: {len(code)} chars")
        
        return blocks
    
    def extract_metadata(self, lang: str, code: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract caption and label from diagram code"""
        caption = None
        label = None
        
        # Extract caption
        if lang in self.METADATA_PATTERNS['caption']:
            cap_pattern = re.compile(
                self.METADATA_PATTERNS['caption'][lang], 
                re.IGNORECASE | re.MULTILINE
            )
            cap_match = cap_pattern.search(code)
            if cap_match:
                # Get first non-None group
                caption = next((g for g in cap_match.groups() if g), None)
        
        # Extract label
        if lang in self.METADATA_PATTERNS['label']:
            lab_pattern = re.compile(
                self.METADATA_PATTERNS['label'][lang], 
                re.IGNORECASE | re.MULTILINE
            )
            lab_match = lab_pattern.search(code)
            if lab_match:
                label = lab_match.group(1)
        
        return caption, label
    
    def render_diagram(self, lang: str, code: str, output_dir: Path) -> Path:
        """Render diagram to SVG with caching support"""
        # Generate content hash for caching
        content_hash = hashlib.md5(code.encode('utf-8')).hexdigest()[:8]
        output_file = output_dir / f'{lang}_{content_hash}.svg'
        
        # Check cache if enabled
        if self.config['cache_enabled'] and output_file.exists():
            self.cache_stats['hits'] += 1
            self.logger.info(f"• CACHE HIT: {output_file.name}")
            return output_file
        
        self.cache_stats['misses'] += 1
        
        # Ensure engine is available
        if lang not in self.available_engines:
            raise RuntimeError(f"Engine not available: {lang}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary input file
        engine_info = self.available_engines[lang]
        temp_ext = engine_info['extensions'][0]
        temp_file = Path(f'.tmp_{lang}_{content_hash}{temp_ext}')
        
        try:
            # Write code to temp file
            temp_file.write_text(code, encoding='utf-8')
            
            # Build command arguments
            cmd_args = [engine_info['cmd']] + [
                arg.format(input=str(temp_file), output=str(output_file))
                for arg in engine_info['args']
            ]
            
            # Execute rendering
            self.logger.info(f"🔄 Rendering {lang} diagram...")
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.cache_stats['errors'] += 1
                raise RuntimeError(f"Rendering failed: {result.stderr.strip()}")
            
            if not output_file.exists():
                raise RuntimeError(f"Output file not created: {output_file}")
            
            self.logger.info(f"✓ Rendered: {output_file.name}")
            return output_file
            
        except subprocess.TimeoutExpired:
            self.cache_stats['errors'] += 1
            raise RuntimeError(f"Rendering timeout for {lang}")
        
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def process_markdown_images(self, text: str) -> str:
        """Convert Markdown images with labels to Typst figures"""
        
        def replace_image(match):
            alt_text = match.group(1) or "Image"
            image_path = match.group(2)
            attributes = match.group(3) or ""
            
            # Parse attributes: {#fig:label width=80%}
            label = None
            width = self.config['diagram_settings']['default_width']
            
            if attributes:
                # Parse label
                label_match = re.search(r'#(fig:[\w\-]+)', attributes)
                if label_match:
                    label = label_match.group(1)
                
                # Parse width
                width_match = re.search(r'width=([^,\s}]+)', attributes)
                if width_match:
                    width = width_match.group(1)
            
            # Generate automatic label if not provided
            if not label:
                path_hash = hashlib.md5(image_path.encode()).hexdigest()[:8]
                label = f"fig:{path_hash}"
            
            return f'''#figure(
  image("{image_path}", width: {width}),
  caption: [{alt_text}],
) <{label}>'''
        
        return re.sub(self.MD_IMAGE_PATTERN, replace_image, text)
    
    def md_to_typst(self, md_path: Path, output_path: Path) -> Dict[str, Any]:
        """Convert Markdown with diagrams to Typst document"""
        self.logger.info(f"Converting {md_path} to {output_path}")
        
        # Read markdown content
        md_content = md_path.read_text(encoding='utf-8')
        
        # Find and process diagram blocks
        diagram_blocks = self.find_diagram_blocks(md_content)
        output_dir = Path(self.config['output_dir'])
        
        stats = {
            'diagrams_processed': 0,
            'diagrams_cached': 0,
            'diagrams_rendered': 0,
            'images_processed': 0
        }
        
        def replace_diagram_block(match):
            lang = match.group(1).lower()
            code = match.group(2).strip()
            
            if lang not in self.available_engines:
                return match.group(0)  # Return original if engine not available
            
            try:
                # Extract metadata
                caption, label = self.extract_metadata(lang, code)
                
                # Render diagram
                svg_path = self.render_diagram(lang, code, output_dir)
                
                # Generate fallback caption and label
                content_hash = hashlib.md5(code.encode('utf-8')).hexdigest()[:8]
                if not caption:
                    caption = f"{lang.title()} Diagram {content_hash}"
                if not label:
                    label = f"fig:{content_hash}"
                
                stats['diagrams_processed'] += 1
                
                # Generate Typst figure
                width = self.config['diagram_settings']['default_width']
                return f'''#figure(
  image("{svg_path.as_posix()}", width: {width}),
  caption: [{caption}],
) <{label}>
'''
            
            except Exception as e:
                self.logger.error(f"Failed to process {lang} diagram: {e}")
                return f"// ERROR: Failed to render {lang} diagram: {e}\n"
        
        # Replace diagram blocks
        typst_content = re.sub(
            r'```(\w+)\n(.*?)\n```', 
            replace_diagram_block, 
            md_content, 
            flags=re.DOTALL
        )
        
        # Process markdown images
        original_images = len(re.findall(self.MD_IMAGE_PATTERN, typst_content))
        typst_content = self.process_markdown_images(typst_content)
        stats['images_processed'] = original_images
        
        # Generate Typst document header
        header = self._generate_typst_header()
        
        # Combine header and content
        full_document = header + typst_content
        
        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_document, encoding='utf-8')
        
        # Update stats
        stats['diagrams_cached'] = self.cache_stats['hits']
        stats['diagrams_rendered'] = self.cache_stats['misses']
        
        self.logger.info(f"✓ Generated {output_path}")
        self.logger.info(f"📊 Stats: {stats['diagrams_processed']} diagrams, "
                        f"{stats['images_processed']} images, "
                        f"{stats['diagrams_cached']} cached, "
                        f"{stats['diagrams_rendered']} rendered")
        
        return stats
    
    def _generate_typst_header(self) -> str:
        """Generate Typst document header with configuration"""
        ts = self.config['typst_settings']
        doc = self.config['document']
        
        header = f'''// Generated by WOT-PDF Enhanced Diagram Builder
// {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

#set heading(numbering: {ts['numbering']})
#set page(numbering: "1", margin: {ts['margin']})
#set text(size: {ts['font_size']}, font: "{ts['font_family']}")

// Helper functions for lists of figures and tables
#let list_of_figures() = {{
  heading(level: 1, "Seznam slik")
  for f in query(figure.where(kind: image)) {{
    let n = f.counter.display()
    let cap = f.caption.body
    [Slika #n: #cap]
    linebreak()
  }}
}}

#let list_of_tables() = {{
  heading(level: 1, "Seznam tabel")
  for t in query(figure.where(kind: table)) {{
    let n = t.counter.display()
    let cap = t.caption.body
    [Tabela #n: #cap]
    linebreak()
  }}
}}

'''
        
        # Add document structure elements
        if doc['include_toc']:
            header += "#outline(depth: 3)\n#pagebreak()\n\n"
        
        if doc['include_lof']:
            header += "#list_of_figures()\n#pagebreak()\n\n"
        
        if doc['include_lot']:
            header += "#list_of_tables()\n#pagebreak()\n\n"
        
        return header
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get current cache statistics"""
        return self.cache_stats.copy()
    
    def clear_cache(self) -> int:
        """Clear diagram cache and return number of files removed"""
        output_dir = Path(self.config['output_dir'])
        if not output_dir.exists():
            return 0
        
        removed = 0
        for svg_file in output_dir.glob("*.svg"):
            svg_file.unlink()
            removed += 1
        
        self.logger.info(f"🧹 Cleared {removed} cached diagrams")
        return removed


# CLI Interface
if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Diagram Builder for WOT-PDF')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('output', help='Output Typst file')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--clear-cache', action='store_true', help='Clear diagram cache')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    # Create builder
    config_path = Path(args.config) if args.config else None
    builder = EnhancedDiagramBuilder(config_path=config_path)
    
    # Clear cache if requested
    if args.clear_cache:
        builder.clear_cache()
        sys.exit(0)
    
    try:
        # Convert document
        stats = builder.md_to_typst(Path(args.input), Path(args.output))
        
        # Print summary
        print(f"\n✅ Conversion complete!")
        print(f"📊 Processed: {stats['diagrams_processed']} diagrams, {stats['images_processed']} images")
        print(f"⚡ Cache: {stats['diagrams_cached']} hits, {stats['diagrams_rendered']} renders")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
