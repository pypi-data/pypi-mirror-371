#!/usr/bin/env python3
"""
🎯 ENHANCED REPORTLAB ENGINE - PROFESSIONAL THEMES
==================================================
⚡ Advanced ReportLab engine with Typst-quality themes
🔷 Professional styling matching Typst output quality
📊 Hybrid approach for maximum compatibility and beauty

FEATURES:
- Professional color schemes from Typst themes
- Advanced typography with custom fonts
- Template-specific styling and layouts
- Code highlighting and professional formatting
"""

import unicodedata
import re

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import re

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Table, TableStyle, Image, KeepTogether, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.colors import HexColor, black, blue, red, green, gray, white
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.platypus.tableofcontents import TableOfContents
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class EnhancedReportLabEngine:
    """
    Enhanced ReportLab PDF engine with professional Typst-quality themes
    """
    
    # CUSTOM FONT SUPPORT
    CUSTOM_FONTS = {
        'source_code_pro': {
            'family': 'SourceCodePro',
            'files': {
                'regular': 'fonts/SourceCodePro-Regular.ttf',
                'bold': 'fonts/SourceCodePro-Bold.ttf',
                'italic': 'fonts/SourceCodePro-Italic.ttf'
            },
            'code_font': True
        },
        'inter': {
            'family': 'Inter',
            'files': {
                'regular': 'fonts/Inter-Regular.ttf',
                'bold': 'fonts/Inter-Bold.ttf',
                'italic': 'fonts/Inter-Italic.ttf'
            },
            'body_font': True
        },
        'roboto_slab': {
            'family': 'RobotoSlab',
            'files': {
                'regular': 'fonts/RobotoSlab-Regular.ttf',
                'bold': 'fonts/RobotoSlab-Bold.ttf'
            },
            'heading_font': True
        }
    }
    
    # PROFESSIONAL THEME DEFINITIONS (matching Typst themes)
    PROFESSIONAL_THEMES = {
        'modern_blue': {
            'name': '🔵 Modern Blue Professional',
            'primary_color': '#2563eb',
            'secondary_color': '#1e40af', 
            'accent_color': '#3b82f6',
            'text_color': '#1f2937',
            'background_color': '#f8fafc',
            'code_bg': '#f1f5f9'
        },
        'elegant_forest': {
            'name': '🌲 Elegant Forest',
            'primary_color': '#059669',
            'secondary_color': '#047857',
            'accent_color': '#10b981', 
            'text_color': '#1f2937',
            'background_color': '#f0fdf4',
            'code_bg': '#ecfdf5'
        },
        'warm_autumn': {
            'name': '🍂 Warm Autumn',
            'primary_color': '#dc2626',
            'secondary_color': '#b91c1c',
            'accent_color': '#ef4444',
            'text_color': '#1f2937', 
            'background_color': '#fef2f2',
            'code_bg': '#fee2e2'
        },
        'royal_purple': {
            'name': '👑 Royal Purple',
            'primary_color': '#7c3aed',
            'secondary_color': '#6d28d9',
            'accent_color': '#8b5cf6',
            'text_color': '#1f2937',
            'background_color': '#faf5ff',
            'code_bg': '#f3e8ff'
        },
        'corporate_gray': {
            'name': '🏢 Corporate Gray',
            'primary_color': '#374151',
            'secondary_color': '#1f2937',
            'accent_color': '#6b7280',
            'text_color': '#111827',
            'background_color': '#f9fafb',
            'code_bg': '#f3f4f6'
        },
        'creative_vibrant': {
            'name': '🎨 Creative Vibrant',
            'primary_color': '#dc2626',
            'secondary_color': '#2563eb',
            'accent_color': '#f97316',
            'text_color': '#1f2937',
            'background_color': '#fefefe',
            'code_bg': '#f8fafc'
        },
        'magazine_red': {
            'name': '📰 Magazine Red',
            'primary_color': '#dc2626',
            'secondary_color': '#991b1b',
            'accent_color': '#f87171',
            'text_color': '#1f2937',
            'background_color': '#fffbfb',
            'code_bg': '#fef2f2'
        },
        'scientific_blue': {
            'name': '🔬 Scientific Blue',
            'primary_color': '#1e40af',
            'secondary_color': '#0f766e',
            'accent_color': '#3b82f6',
            'text_color': '#1f2937',
            'background_color': '#f0f9ff',
            'code_bg': '#e0f2fe'
        },
        'presentation_blue': {
            'name': '📊 Presentation Blue',
            'primary_color': '#1565c0',
            'secondary_color': '#43a047',
            'accent_color': '#ff9800',
            'text_color': '#37474f',
            'background_color': '#f5f5f5',
            'code_bg': '#f8f9fa'
        },
        'handbook_green': {
            'name': '📖 Handbook Green',
            'primary_color': '#2e7d32',
            'secondary_color': '#795548',
            'accent_color': '#ff8f00',
            'text_color': '#424242',
            'background_color': '#f8f9fa',
            'code_bg': '#f1f8e9'
        }
    }
    
    # TEMPLATE CONFIGURATIONS
    TEMPLATE_CONFIGS = {
        'technical': {
            'theme': 'modern_blue',
            'features': ['code_highlighting', 'api_docs', 'diagrams'],
            'font_size': 11,
            'line_spacing': 1.2
        },
        'academic': {
            'theme': 'elegant_forest', 
            'features': ['citations', 'bibliography', 'equations'],
            'font_size': 12,
            'line_spacing': 1.4
        },
        'corporate': {
            'theme': 'corporate_gray',
            'features': ['executive_summary', 'charts', 'branding'], 
            'font_size': 11,
            'line_spacing': 1.3
        },
        'educational': {
            'theme': 'warm_autumn',
            'features': ['exercises', 'examples', 'highlights'],
            'font_size': 12,
            'line_spacing': 1.3
        },
        'minimal': {
            'theme': 'corporate_gray',
            'features': ['clean_typography', 'basic_formatting'],
            'font_size': 11,
            'line_spacing': 1.2
        },
        'creative': {
            'theme': 'creative_vibrant',
            'features': ['artistic_layout', 'vibrant_colors', 'creative_elements'],
            'font_size': 11,
            'line_spacing': 1.3
        },
        'magazine': {
            'theme': 'magazine_red',
            'features': ['publication_style', 'editorial_layout', 'article_format'],
            'font_size': 10,
            'line_spacing': 1.2
        },
        'scientific': {
            'theme': 'scientific_blue',
            'features': ['research_format', 'equations', 'citations', 'bibliography'],
            'font_size': 11,
            'line_spacing': 1.4
        },
        'presentation': {
            'theme': 'presentation_blue',
            'features': ['slide_style', 'bullet_points', 'visual_emphasis'],
            'font_size': 12,
            'line_spacing': 1.2
        },
        'handbook': {
            'theme': 'handbook_green',
            'features': ['manual_format', 'step_instructions', 'reference_style'],
            'font_size': 11,
            'line_spacing': 1.3
        }
    }
    
    def __init__(self):
        """Initialize enhanced ReportLab engine"""
        self.logger = logging.getLogger(__name__)
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required but not installed")
        
        self.styles = getSampleStyleSheet()
        self.theme = None
        self.template_config = None
        
        # Initialize custom fonts
        self._setup_custom_fonts()
        
    def _setup_custom_fonts(self):
        """Setup custom fonts for enhanced typography"""
        self.available_fonts = {
            'body': 'Helvetica',
            'heading': 'Helvetica-Bold', 
            'code': 'Courier'
        }
        
        # Try to load custom fonts if available
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from pathlib import Path
            
            for font_key, font_config in self.CUSTOM_FONTS.items():
                font_family = font_config['family']
                font_files = font_config['files']
                
                # Try to register fonts from common locations
                font_paths = [
                    Path('fonts'),
                    Path('assets/fonts'),
                    Path('../fonts'),
                    Path.home() / 'fonts'
                ]
                
                for font_path in font_paths:
                    if font_path.exists():
                        regular_path = font_path / font_files['regular']
                        if regular_path.exists():
                            try:
                                # Register regular font
                                pdfmetrics.registerFont(TTFont(font_family, str(regular_path)))
                                
                                # Register bold if available
                                if 'bold' in font_files:
                                    bold_path = font_path / font_files['bold']
                                    if bold_path.exists():
                                        pdfmetrics.registerFont(TTFont(f"{font_family}-Bold", str(bold_path)))
                                
                                # Register italic if available  
                                if 'italic' in font_files:
                                    italic_path = font_path / font_files['italic']
                                    if italic_path.exists():
                                        pdfmetrics.registerFont(TTFont(f"{font_family}-Italic", str(italic_path)))
                                
                                # Update available fonts based on font type
                                if font_config.get('body_font'):
                                    self.available_fonts['body'] = font_family
                                if font_config.get('heading_font'):
                                    self.available_fonts['heading'] = f"{font_family}-Bold" if 'bold' in font_files else font_family
                                if font_config.get('code_font'):
                                    self.available_fonts['code'] = font_family
                                
                                self.logger.info(f"✅ Loaded custom font: {font_family}")
                                break
                                
                            except Exception as e:
                                self.logger.debug(f"Could not load font {font_family}: {e}")
                                continue
                
        except Exception as e:
            self.logger.debug(f"Custom font setup failed, using defaults: {e}")
            
        self.logger.info(f"🔤 Font Configuration: Body={self.available_fonts['body']}, Heading={self.available_fonts['heading']}, Code={self.available_fonts['code']}")
        
    def _setup_professional_styles(self, template: str = "technical"):
        """Setup professional paragraph styles with Typst-quality themes"""
        
        # Get template configuration
        self.template_config = self.TEMPLATE_CONFIGS.get(template, self.TEMPLATE_CONFIGS['technical'])
        theme_name = self.template_config['theme']
        self.theme = self.PROFESSIONAL_THEMES[theme_name]
        
        # Clear existing custom styles
        custom_styles = ['ProfTitle', 'ProfSubtitle', 'ProfCode', 'ProfQuote', 'ProfCaption']
        for i in range(1, 7):
            custom_styles.append(f'ProfHeading{i}')
        
        for style_name in custom_styles:
            if style_name in self.styles:
                del self.styles[style_name]
        
        # Professional title style
        self.styles.add(ParagraphStyle(
            name='ProfTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor(self.theme['primary_color']),
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName=self.available_fonts['heading']
        ))
        
        # Professional subtitle
        self.styles.add(ParagraphStyle(
            name='ProfSubtitle', 
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor(self.theme['secondary_color']),
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName=self.available_fonts['body']
        ))
        
        # Professional headings with theme colors
        heading_sizes = [18, 16, 14, 13, 12, 11]
        for i, size in enumerate(heading_sizes, 1):
            self.styles.add(ParagraphStyle(
                name=f'ProfHeading{i}',
                parent=self.styles['Normal'],
                fontSize=size,
                textColor=HexColor(self.theme['primary_color']),
                fontName=self.available_fonts['heading'],
                spaceAfter=12,
                spaceBefore=20 if i <= 2 else 16,
                leftIndent=0
            ))
        
        # Professional code style - improved readability
        self.styles.add(ParagraphStyle(
            name='ProfCode',
            parent=self.styles['Code'],
            fontSize=10,  # Increased from 9 to 10 for better readability
            textColor=HexColor('#2d2d2d'),  # Darker text for better contrast
            backColor=HexColor('#f8f8f8'),  # Light gray background
            fontName=self.available_fonts['code'],
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=15,
            rightIndent=15,
            borderWidth=1,
            borderColor=HexColor('#e0e0e0'),  # Softer border
            borderPadding=8  # More padding inside
        ))
        
        # Professional quote style
        self.styles.add(ParagraphStyle(
            name='ProfQuote',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor(self.theme['secondary_color']),
            fontName='Helvetica-Oblique',
            leftIndent=30,
            rightIndent=30,
            spaceAfter=12,
            spaceBefore=12,
            borderColor=HexColor(self.theme['accent_color']),
            borderWidth=0,
            borderPadding=0,
            leftBorderWidth=3,  # Left border for quote
            leftBorderColor=HexColor(self.theme['accent_color']),
            leftBorderPadding=15
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='ProfCaption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor(self.theme['secondary_color']),
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=6
        ))
    
    def _create_professional_header_footer(self, canvas, doc, title: str, author: str, page_numbering: str = "standard"):
        """Create professional header and footer with various page numbering styles"""
        canvas.saveState()
        
        # Header
        if hasattr(doc, 'page') and doc.page > 1:  # Skip header on first page
            header_text = title[:50] + "..." if len(title) > 50 else title
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(HexColor(self.theme['secondary_color']))
            canvas.drawString(50, A4[1] - 30, header_text)
            
            # Header line
            canvas.setStrokeColor(HexColor(self.theme['accent_color']))
            canvas.setLineWidth(0.5)
            canvas.line(50, A4[1] - 35, A4[0] - 50, A4[1] - 35)
        
        # Footer
        canvas.setFont('Helvetica', 9) 
        canvas.setFillColor(HexColor(self.theme['secondary_color']))
        
        # Enhanced page numbering with different styles
        page_num = doc.page if hasattr(doc, 'page') else 1
        
        if page_numbering == "standard":
            page_text = f"Page {page_num}"
        elif page_numbering == "simple":
            page_text = str(page_num)
        elif page_numbering == "dash":
            page_text = f"— {page_num} —"
        elif page_numbering == "brackets":
            page_text = f"[{page_num}]"
        elif page_numbering == "roman":
            # Convert to Roman numerals for TOC pages, Arabic for content
            if page_num <= 10:  # Assume first 10 pages could be TOC/front matter
                roman_nums = ['', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
                page_text = roman_nums[page_num] if page_num < len(roman_nums) else str(page_num)
            else:
                page_text = str(page_num - 10)  # Reset numbering after TOC
        else:
            page_text = f"Page {page_num}"  # Default fallback
        
        # Draw page number
        canvas.drawRightString(A4[0] - 50, 30, page_text)
        
        # Author/date
        footer_left = f"{author} • {datetime.now().strftime('%Y-%m-%d')}"
        canvas.drawString(50, 30, footer_left)
        
        # Footer line
        canvas.setStrokeColor(HexColor(self.theme['accent_color']))
        canvas.setLineWidth(0.5)
        canvas.line(50, 45, A4[0] - 50, 45)
        
        canvas.restoreState()
    
    def generate(self,
                 content: str,
                 output_file: Path,
                 template: str = "technical",
                 title: Optional[str] = None,
                 author: Optional[str] = None,
                 generate_toc: bool = False,
                 page_numbering: str = "standard",
                 number_headings: bool = True,
                 **kwargs) -> Dict[str, Any]:
        """
        Generate professional PDF with enhanced styling
        """
        try:
            # Setup professional styles
            self._setup_professional_styles(template)
            
            # Create document with professional styling
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=60,
                title=title or "Document",
                author=author or "WOT-PDF"
            )
            
            # Create story (content elements)
            story = []
            
            # Add title page if title provided
            if title:
                story.append(Paragraph(title, self.styles['ProfTitle']))
                if author:
                    story.append(Paragraph(f"by {author}", self.styles['ProfSubtitle']))
                story.append(Spacer(1, 40))
                story.append(PageBreak())
            
            # Generate TOC if requested - FIXED ORDER
            if generate_toc:
                print(f"🔧 TOC generation requested with number_headings={number_headings}")
                headings = self._collect_headings(content)
                print(f"📋 Collected {len(headings)} headings for TOC")
                
                if number_headings and headings:
                    # Apply numbering to headings in content BEFORE TOC generation
                    print(f"🔢 Applying numbering to {len(headings)} headings")
                    content = self._apply_heading_numbers(content, headings)
                    # Re-collect headings after numbering (they now have numbered_text)
                    headings = self._collect_headings(content)
                    print(f"📋 Re-collected {len(headings)} numbered headings")
                
                if headings:
                    print(f"📑 Generating TOC with {len(headings)} entries")
                    toc_elements = self._generate_toc(headings)
                    story.extend(toc_elements)
                    print(f"✅ TOC generated successfully with {len(toc_elements)} elements")
                else:
                    print("⚠️ No headings found for TOC generation")
            
            # Process markdown content with optimization for large documents
            if self._optimize_for_large_content(content):
                # Use chunked processing for large documents
                content_elements = self._process_content_in_chunks(content)
            else:
                # Standard processing for normal documents
                content_elements = self._process_markdown_content(content)
            
            story.extend(content_elements)
            
            # Build PDF with professional header/footer
            def add_header_footer(canvas, doc):
                self._create_professional_header_footer(canvas, doc, title or "Document", author or "WOT-PDF", page_numbering)
            
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            # Get file size
            file_size = output_file.stat().st_size if output_file.exists() else 0
            
            self.logger.info(f"✅ Enhanced ReportLab PDF generated: {output_file} ({file_size/1024:.1f} KB)")
            
            return {
                "success": True,
                "output_file": str(output_file),
                "file_size_bytes": file_size,
                "template": template,
                "theme": self.theme['name'],
                "engine": "enhanced_reportlab"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced ReportLab generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "enhanced_reportlab"
            }
    
    def _process_markdown_content(self, content: str) -> List[Any]:
        """Process markdown content into ReportLab story elements with proper Unicode support"""
        story = []
        
        # Ensure proper UTF-8 encoding
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        
        # Clean and normalize Unicode content
        content = self._clean_unicode_content(content)
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ').strip()
                if header_text and level <= 6:
                    # Clean Unicode in headers
                    header_text = self._clean_unicode_content(header_text)
                    # Remove any remaining problematic characters
                    header_text = ''.join(char for char in header_text if ord(char) < 65536)
                    story.append(Paragraph(header_text, self.styles[f'ProfHeading{level}']))
                    story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Code blocks
            if line.startswith('```'):
                language = line[3:].strip()  # Extract language identifier
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    
                    # Clean Unicode in code blocks
                    code_text = self._clean_unicode_content(code_text)
                    
                    # Special handling for Python strings with < and > characters
                    code_text = self._fix_python_string_operators(code_text)
                    
                    # MINIMAL escaping - only what breaks ReportLab XML parsing
                    # Remove aggressive HTML entity escaping for better code readability
                    # Most characters like <>"' are fine in ReportLab Paragraph context
                    
                    # Handle very long code blocks
                    if len(code_text) > 2000:
                        code_text = code_text[:1997] + "..."
                    
                    # SIMPLE & EFFECTIVE - Clean XML but preserve all content
                    try:
                        # Clean the code for XML safety - MINIMAL escaping
                        cleaned_code = self._clean_code_for_xml(code_text)
                        
                        # Add language label if specified
                        if language:
                            story.append(Paragraph(f'<i>{language}</i>', self.styles['Normal']))
                            story.append(Spacer(1, 3))
                        
                        # FIXED: Use Preformatted to preserve line breaks and indentation
                        story.append(Preformatted(cleaned_code, self.styles['ProfCode']))
                            
                    except Exception as e:
                        # If formatting fails, fall back to safe approach
                        self.logger.warning(f"Code block formatting failed, using fallback: {e}")
                        
                        # Try with basic Preformatted fallback
                        try:
                            safe_code = self._make_safe_text(code_text)
                            if language:
                                story.append(Paragraph(f'Code ({language}):', self.styles['Normal']))
                            story.append(Preformatted(safe_code, self.styles['ProfCode']))
                        except:
                            # Last resort - plain paragraph
                            safe_code = self._make_safe_text(code_text)
                            story.append(Paragraph(f'Code: {safe_code}', self.styles['Normal']))
                    
                    story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Block quotes
            if line.startswith('>'):
                quote_text = line.lstrip('> ').strip()
                story.append(Paragraph(quote_text, self.styles['ProfQuote']))
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Lists
            if line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', line):
                list_items = []
                while i < len(lines) and lines[i].strip() and (
                    lines[i].strip().startswith(('- ', '* ', '+ ')) or 
                    re.match(r'^\d+\.\s', lines[i].strip())
                ):
                    item_text = re.sub(r'^[-*+]\s|\d+\.\s', '', lines[i].strip())
                    list_items.append(f'• {item_text}')
                    i += 1
                
                for item in list_items:
                    story.append(Paragraph(item, self.styles['Normal']))
                    story.append(Spacer(1, 3))
                story.append(Spacer(1, 6))
                continue
            
            # Table detection (enhanced markdown table processing)
            if '|' in line and line.count('|') >= 2:
                table_data, rows_processed = self._process_markdown_table(lines, i)
                if table_data:
                    # Create professional table
                    table = self._create_professional_table(table_data)
                    story.append(table)
                    story.append(Spacer(1, 12))
                    i += rows_processed
                    continue
                
                # Fallback for simple table rows
                table_text = (line.replace('&', '&amp;')
                                 .replace('<', '&lt;')
                                 .replace('>', '&gt;'))
                try:
                    story.append(Paragraph(table_text, self.styles['Normal']))
                except Exception as e:
                    clean_text = line.replace('<', '').replace('>', '').replace('&', '').replace('|', ' | ')
                    story.append(Paragraph(clean_text, self.styles['Normal']))
                story.append(Spacer(1, 6))
                i += 1
                continue
            
            # Regular paragraph
            para_text = self._process_inline_formatting(line)
            
            # Final safety check for paragraph creation with XML validation
            try:
                # Validate XML tags are properly balanced
                if self._validate_xml_tags(para_text):
                    story.append(Paragraph(para_text, self.styles['Normal']))
                else:
                    # XML tags not balanced - escape and use as plain text
                    safe_text = para_text.replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(safe_text, self.styles['Normal']))
            except Exception as e:
                # Fallback: completely clean text without any formatting
                self.logger.warning(f"Paragraph formatting failed, using plain text: {e}")
                clean_text = (line.replace('<', '')
                                 .replace('>', '')
                                 .replace('&', '')
                                 .replace('|', ' | '))
                story.append(Paragraph(clean_text, self.styles['Normal']))
            
            story.append(Spacer(1, 6))
            i += 1
        
        return story
    
    def _validate_xml_tags(self, text: str) -> bool:
        """Validate that XML tags are properly balanced"""
        import re
        from collections import deque
        
        # Find all tags
        tag_pattern = r'<(/?)([^>]+?)>'
        tags = re.findall(tag_pattern, text)
        
        stack = deque()
        
        for is_closing, tag_name in tags:
            # Clean tag name (remove attributes)
            clean_tag = tag_name.split()[0].lower()
            
            if is_closing:  # Closing tag
                if not stack or stack[-1] != clean_tag:
                    return False  # Unmatched closing tag
                stack.pop()
            else:  # Opening tag
                # Skip self-closing tags and specific ReportLab tags
                if not tag_name.endswith('/') and clean_tag not in ['br', 'img']:
                    stack.append(clean_tag)
        
        return len(stack) == 0  # All tags should be closed
    
    def _clean_code_for_xml(self, code: str) -> str:
        """Clean code content for XML parsing - MINIMAL escaping for better readability"""
        if not code:
            return ""
        
        # Step 1: Unicode normalization
        code = unicodedata.normalize('NFKC', code)
        
        # Step 2: ONLY escape characters that BREAK XML parsing
        # Most code characters are fine in ReportLab Paragraph context
        xml_critical_replacements = {
            '&': '&amp;',   # Only if not already escaped
        }
        
        # Only escape standalone & that would break XML
        # Avoid double escaping already escaped entities
        if '&amp;' not in code and '&lt;' not in code and '&gt;' not in code:
            code = code.replace('&', '&amp;')
        
        # Step 3: Clean up whitespace but preserve structure
        code = code.replace('\r\n', '\n')  # Normalize line endings
        code = code.replace('\r', '\n')    # Mac line endings
        code = code.replace('\t', '    ')  # Tabs to spaces for consistent display
        
        return code

    def _make_safe_text(self, text: str) -> str:
        """Create completely ReportLab-safe text - BULLETPROOF XML-SAFE VERSION"""
        if not text:
            return ""
            
        # Step 1: Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Step 2: AGGRESSIVE XML entity encoding - prevent ALL XML parsing
        xml_entities = {
            '&': '&amp;',   # Must be first!
            '<': '&lt;',    
            '>': '&gt;',    
            '"': '&quot;',  
            "'": '&#39;',   
        }
        
        for char, entity in xml_entities.items():
            text = text.replace(char, entity)
        
        # Step 3: Clean remaining problematic characters
        text = (text
                .replace('\t', '    ')      # Tabs to spaces
                .replace('\r', '')          # Remove carriage returns
                .replace('`', "'")          # Backticks to quotes
                .replace('\\', '/')         # Backslashes to forward slashes
                )
        
        # Step 4: Remove any XML-like patterns that might remain
        import re
        # Remove anything that looks like XML tags after entity encoding
        text = re.sub(r'&lt;[^&]*&gt;', '[XML-like content removed]', text)
        
        # Step 5: Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Step 6: Truncate if too long (ReportLab paragraph limit)
        if len(text) > 3000:
            text = text[:3000] + "... [content truncated for safety]"
        
        return text.strip()

    def _gentle_safe_text(self, text: str) -> str:
        """Gentle text cleaning - preserves readability"""
        if not text:
            return ""
        
        # Step 1: Only normalize Unicode if needed
        import unicodedata
        text = unicodedata.normalize('NFKC', text)
        
        # Step 2: Only escape truly dangerous characters
        dangerous_replacements = {
            '<': '&lt;',  # XML tags
            '>': '&gt;',  # XML tags
        }
        
        for char, replacement in dangerous_replacements.items():
            # Only replace if not already part of our own formatting
            if char in text and not f'&{replacement[1:-1]};' in text:
                text = text.replace(char, replacement)
        
        return text.strip()

    def _process_inline_formatting(self, text: str) -> str:
        """Process inline markdown formatting - IMPROVED VERSION"""
        
        # Step 1: Process inline code FIRST (before _make_safe_text destroys it)
        import re
        
        # Find inline code patterns: `code here`
        inline_code_pattern = r'`([^`]+)`'
        
        def replace_inline_code(match):
            code_content = match.group(1)
            # Minimal escaping for inline code
            code_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
            return f'<font name="Courier" color="#d63384" backColor="#f8f9fa" size="9">{code_content}</font>'
        
        # Replace inline code
        text = re.sub(inline_code_pattern, replace_inline_code, text)
        
        # Step 2: Process links (before _make_safe_text)
        text = self._process_links(text)
        
        # Step 3: Only GENTLE safe text processing (not the aggressive _make_safe_text)
        text = self._gentle_safe_text(text)
        
        # Step 4: Bold formatting - simple and safe
        while '**' in text:
            start = text.find('**')
            if start == -1:
                break
            end = text.find('**', start + 2)
            if end == -1:
                break
            
            before = text[:start]
            content = text[start + 2:end]
            after = text[end + 2:]
            
            text = before + '<b>' + content + '</b>' + after
        
        # Step 5: Italic formatting - FIXED to avoid conflict with bold
        import re
        # Use regex to handle italic that's NOT part of bold
        # Match *text* but not **text** 
        italic_pattern = r'(?<!\*)\*([^\*]+)\*(?!\*)'
        text = re.sub(italic_pattern, r'<i>\1</i>', text)
        
        # Step 6: Strikethrough - ~~text~~
        strikethrough_pattern = r'~~([^~]+)~~'
        text = re.sub(strikethrough_pattern, r'<strike>\1</strike>', text)
        
        # Step 7: Underline - __text__ (but not if it's part of bold)
        underline_pattern = r'(?<!\*)__([^_]+)__(?!\*)'
        text = re.sub(underline_pattern, r'<u>\1</u>', text)
        
        return text
    
    def _clean_unicode_content(self, content: str) -> str:
        """Clean and normalize Unicode content for ReportLab compatibility"""
        import unicodedata
        
        # Normalize Unicode characters
        content = unicodedata.normalize('NFKC', content)
        
        # Replace problematic Unicode characters with ReportLab-safe alternatives
        replacements = {
            # Common problematic characters
            '\u2013': '-',      # en dash
            '\u2014': '--',     # em dash  
            '\u2018': "'",      # left single quote
            '\u2019': "'",      # right single quote
            '\u201c': '"',      # left double quote
            '\u201d': '"',      # right double quote
            '\u2026': '...',    # ellipsis
            '\u00a0': ' ',      # non-breaking space
            
            # Arrows and symbols that might cause issues
            '\u2192': '->',     # right arrow
            '\u2190': '<-',     # left arrow
            '\u2194': '<->',    # left-right arrow
            '\u2022': '•',      # bullet point (keep as is, works in ReportLab)
            
            # Mathematical symbols
            '\u2264': '<=',     # less than or equal
            '\u2265': '>=',     # greater than or equal
            '\u00b1': '+/-',    # plus-minus
            '\u00d7': 'x',      # multiplication sign
            '\u00f7': '/',      # division sign
            
            # Degree symbol (keep as is, usually works)
            # '\u00b0': '°',    
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Handle emoji and other high Unicode - convert to descriptions
        content = self._handle_emoji_content(content)
        
        return content
    
    def _handle_emoji_content(self, content: str) -> str:
        """Convert emoji to text descriptions for ReportLab compatibility"""
        
        # Common emoji in technical documentation
        emoji_replacements = {
            '🎯': '[TARGET]',
            '🔧': '[TOOL]',
            '📊': '[CHART]', 
            '📋': '[CLIPBOARD]',
            '⚡': '[LIGHTNING]',
            '🔷': '[DIAMOND]',
            '✅': '[CHECK]',
            '❌': '[X]',
            '⚠️': '[WARNING]',
            '🚨': '[ALERT]',
            '💡': '[BULB]',
            '🔍': '[SEARCH]',
            '📁': '[FOLDER]',
            '📄': '[FILE]',
            '🎨': '[PALETTE]',
            '🏢': '[BUILDING]',
            '👑': '[CROWN]',
            '🌲': '[TREE]',
            '🍂': '[LEAVES]',
            '🔵': '[BLUE_CIRCLE]',
            '🔴': '[RED_CIRCLE]',
            '🟢': '[GREEN_CIRCLE]',
            '🟡': '[YELLOW_CIRCLE]',
            '⚙️': '[GEAR]',
            '🛠️': '[TOOLS]',
            
            # MISSING EMOJI - Add the ones causing 'n' problems
            '☕': '[COFFEE]',
            '🌶️': '[PEPPER]',
            '🔥': '[FIRE]',
            '🚀': '[ROCKET]',
            '👋': '[WAVE]',
            '🔄': '[REFRESH]',
            '❓': '[QUESTION]',
            '🛡️': '[SHIELD]',  # This was causing 'nn'!
        }
        
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        return content
    
    def _fix_python_string_operators(self, code_text: str) -> str:
        """Fix Python strings containing < and > operators that break XML parsing"""
        import re
        
        # Find Python string patterns with < or > inside
        # Match patterns like: 'text < value' or "text > value"
        patterns = [
            (r"'([^']*<[^']*)'", lambda m: f"'{m.group(1).replace('<', 'less than ')}'"),
            (r"'([^']*>[^']*)'", lambda m: f"'{m.group(1).replace('>', 'greater than ')}'"),
            (r'"([^"]*<[^"]*)"', lambda m: f'"{m.group(1).replace("<", "less than ")}"'),
            (r'"([^"]*>[^"]*)"', lambda m: f'"{m.group(1).replace(">", "greater than ")}"'),
        ]
        
        for pattern, replacement in patterns:
            code_text = re.sub(pattern, replacement, code_text)
        
        return code_text
    
    def _process_markdown_table(self, lines: List[str], start_index: int) -> Tuple[Optional[List[List[str]]], int]:
        """Process markdown table into table data"""
        table_data = []
        current_index = start_index
        
        # Process first line (header)
        header_line = lines[current_index].strip()
        if not header_line or '|' not in header_line:
            return None, 0
        
        # Parse header row
        header_cells = [cell.strip() for cell in header_line.split('|') if cell.strip()]
        if not header_cells:
            return None, 0
            
        table_data.append(header_cells)
        current_index += 1
        
        # Check for separator line (optional in our implementation)
        if current_index < len(lines):
            sep_line = lines[current_index].strip()
            if sep_line and '|' in sep_line and ('-' in sep_line or ':' in sep_line):
                # This is a separator line, skip it
                current_index += 1
        
        # Process data rows
        while current_index < len(lines):
            line = lines[current_index].strip()
            if not line or '|' not in line:
                break
            
            # Parse data row
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                # Pad or trim cells to match header count
                while len(cells) < len(header_cells):
                    cells.append("")
                cells = cells[:len(header_cells)]
                table_data.append(cells)
            
            current_index += 1
        
        rows_processed = current_index - start_index
        return table_data if len(table_data) > 1 else None, rows_processed
    
    def _create_professional_table(self, table_data: List[List[str]]) -> Optional[Any]:
        """Create a professionally styled ReportLab table"""
        if not table_data:
            return None
            
        # Clean table data for XML safety - ADVANCED approach with Paragraph objects
        clean_data = []
        for row_idx, row in enumerate(table_data):
            clean_row = []
            for cell_idx, cell in enumerate(row):
                # STEP 1: Process inline formatting (creates HTML tags)
                formatted_cell = self._process_inline_formatting(cell.strip())
                
                # STEP 2: Create Paragraph object to handle HTML properly
                try:
                    if row_idx == 0:  # Header row
                        cell_paragraph = Paragraph(formatted_cell, self.styles['Normal'])
                    else:  # Data rows
                        cell_paragraph = Paragraph(formatted_cell, self.styles['Normal'])
                    clean_row.append(cell_paragraph)
                except:
                    # Fallback to simple text if Paragraph creation fails
                    safe_text = cell.strip().replace('<', '&lt;').replace('>', '&gt;')
                    clean_row.append(safe_text)
            clean_data.append(clean_row)
        
        # Create table
        table = Table(clean_data)
        
        # Get theme colors
        primary_color = HexColor(self.theme['primary_color'])
        secondary_color = HexColor(self.theme['secondary_color'])
        accent_color = HexColor(self.theme['accent_color'])
        text_color = HexColor(self.theme['text_color'])
        bg_color = HexColor(self.theme['background_color'])
        
        # Professional table styling
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), bg_color),
            ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [bg_color, colors.white]),
            
            # Borders and grid
            ('GRID', (0, 0), (-1, -1), 0.5, secondary_color),
            ('LINEBELOW', (0, 0), (-1, 0), 1, primary_color),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(table_style)
        
        # Auto-size columns
        table._argW[0] = None  # Let ReportLab auto-size columns
        
        return table
    
    def _collect_headings(self, content: str) -> List[Dict[str, Any]]:
        """Collect all headings for TOC generation with automatic numbering"""
        headings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6 and line.lstrip('# ').strip():
                    heading_text = line.lstrip('# ').strip()
                    # Clean heading text
                    heading_text = self._clean_unicode_content(heading_text)
                    heading_text = ''.join(char for char in heading_text if ord(char) < 65536)
                    
                    headings.append({
                        'level': level,
                        'text': heading_text,
                        'line_num': line_num + 1,
                        'original_line': line  # Store original for replacement
                    })
        
        # Add automatic numbering
        headings_with_numbers = self._add_heading_numbers(headings)
        return headings_with_numbers
    
    def _add_heading_numbers(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add automatic hierarchical numbering to headings"""
        # Counter for each level (index 0 = level 1, index 1 = level 2, etc.)
        counters = [0] * 6
        
        for heading in headings:
            level = heading['level']
            
            # Increment counter for current level
            counters[level - 1] += 1
            
            # Reset all deeper level counters
            for i in range(level, 6):
                counters[i] = 0
            
            # Generate number string
            number_parts = []
            for i in range(level):
                if counters[i] > 0:
                    number_parts.append(str(counters[i]))
            
            heading_number = '.'.join(number_parts)
            heading['number'] = heading_number
            heading['numbered_text'] = f"{heading_number}. {heading['text']}"
        
        return headings
    
    def _apply_heading_numbers(self, content: str, headings: List[Dict[str, Any]]) -> str:
        """Apply automatic numbering to headings in content"""
        lines = content.split('\n')
        
        for heading in headings:
            line_num = heading['line_num'] - 1  # Convert to 0-based index
            if line_num < len(lines):
                original_line = lines[line_num]
                # Use numbered text if available, otherwise original
                numbered_text = heading.get('numbered_text', heading['text'])
                
                # Extract the heading prefix (# ## ### etc.)
                level = heading['level']
                prefix = '#' * level + ' '
                
                # Replace the original heading with numbered version
                if 'numbered_text' in heading:
                    lines[line_num] = prefix + numbered_text
        
        return '\n'.join(lines)
    
    def _generate_toc(self, headings: List[Dict[str, Any]]) -> List[Any]:
        """Generate professional table of contents with numbering"""
        if not headings:
            return []
        
        toc_elements = []
        
        # TOC Title
        toc_elements.append(Paragraph("Table of Contents", self.styles['ProfTitle']))
        toc_elements.append(Spacer(1, 20))
        
        # TOC Entries
        for heading in headings:
            level = heading['level']
            # Use numbered text if available, otherwise original text
            text = heading.get('numbered_text', heading['text'])
            
            # Indent based on heading level
            indent = (level - 1) * 20
            
            # TOC entry style
            if level == 1:
                toc_style = ParagraphStyle(
                    name=f'TOC{level}',
                    parent=self.styles['Normal'],
                    fontSize=12,
                    textColor=HexColor(self.theme['primary_color']),
                    fontName='Helvetica-Bold',
                    leftIndent=indent,
                    spaceAfter=8,
                    spaceBefore=4
                )
            else:
                toc_style = ParagraphStyle(
                    name=f'TOC{level}',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=HexColor(self.theme['text_color']),
                    fontName='Helvetica',
                    leftIndent=indent,
                    spaceAfter=4,
                    spaceBefore=2
                )
            
            # Clean text for TOC entry
            clean_text = self._make_safe_text(text)
            toc_elements.append(Paragraph(clean_text, toc_style))
        
        toc_elements.append(Spacer(1, 30))
        toc_elements.append(PageBreak())
        
        return toc_elements
    
    def _process_images(self, content: str) -> str:
        """Process markdown images and add proper captions"""
        import re
        
        # Pattern for markdown images: ![alt text](path/to/image "optional title")
        image_pattern = r'!\[([^\]]*)\]\(([^)]+?)(?:\s+"([^"]*)")?\)'
        
        def replace_image(match):
            alt_text = match.group(1) or "Image"
            image_path = match.group(2)
            title = match.group(3) or alt_text
            
            # For now, replace with a placeholder indicating image location
            # In full implementation, this would embed actual images
            placeholder = f"\n**[IMAGE: {alt_text}]**\n*File: {image_path}*\n*Caption: {title}*\n"
            return placeholder
        
        # Replace all image references
        processed_content = re.sub(image_pattern, replace_image, content)
        return processed_content
    
    def _add_image_to_story(self, image_path: str, alt_text: str = "", caption: str = "", story: Optional[List[Any]] = None):
        """Add image with caption to story elements"""
        if story is None:
            return
            
        try:
            # Try to load and add the image
            from pathlib import Path
            img_path = Path(image_path)
            
            if img_path.exists():
                # Create image with proper sizing
                img = Image(str(img_path))
                
                # Auto-resize to fit page width (max 6 inches wide)
                max_width = 6 * inch
                max_height = 4 * inch
                
                # Calculate scaling to maintain aspect ratio
                img_width = img.drawWidth
                img_height = img.drawHeight
                
                if img_width > max_width:
                    scale = max_width / img_width
                    img.drawWidth = max_width
                    img.drawHeight = img_height * scale
                
                if img.drawHeight > max_height:
                    scale = max_height / img.drawHeight
                    img.drawHeight = max_height
                    img.drawWidth = img.drawWidth * scale
                
                # Add image to story
                story.append(Spacer(1, 12))
                story.append(img)
                
                # Add caption if provided
                if caption:
                    story.append(Spacer(1, 6))
                    story.append(Paragraph(f"<i>{caption}</i>", self.styles['ProfCaption']))
                
                story.append(Spacer(1, 12))
                
            else:
                # Image not found - add placeholder
                placeholder_text = f"[Image not found: {image_path}]"
                if alt_text:
                    placeholder_text = f"[{alt_text} - Image not found: {image_path}]"
                story.append(Paragraph(placeholder_text, self.styles['Normal']))
                story.append(Spacer(1, 6))
                
        except Exception as e:
            # Image processing failed - add error placeholder
            error_text = f"[Image processing failed: {image_path} - {str(e)}]"
            story.append(Paragraph(error_text, self.styles['Normal']))
            story.append(Spacer(1, 6))
    
    def _process_links(self, text: str) -> str:
        """Convert markdown links to ReportLab clickable links"""
        import re
        
        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Create ReportLab link with professional styling
            # Use theme colors for links
            link_color = self.theme['accent_color'] if self.theme else '#3b82f6'
            
            return f'<link href="{link_url}" color="{link_color}"><u>{link_text}</u></link>'
        
        # Replace all markdown links
        processed_text = re.sub(link_pattern, replace_link, text)
        return processed_text
    
    def _add_bookmarks(self, doc, headings: List[Dict[str, Any]]):
        """Add PDF bookmarks for navigation"""
        # This would require more advanced ReportLab features
        # For now, we'll implement basic structure
        
        if not headings:
            return
        
        # Create bookmark outline (simplified implementation)
        bookmark_data = []
        for heading in headings:
            bookmark_data.append({
                'title': heading['text'],
                'level': heading['level'],
                'page': 1  # Simplified - in full implementation would track actual page numbers
            })
        
        # Store bookmark data for potential future use
        doc._bookmark_data = bookmark_data
    
    def _optimize_for_large_content(self, content: str) -> bool:
        """Check if content requires optimization for large documents"""
        # Criteria for large document optimization
        line_count = len(content.split('\n'))
        char_count = len(content)
        table_count = content.count('|')
        code_block_count = content.count('```')
        
        # Consider large if:
        is_large = (
            line_count > 500 or          # More than 500 lines
            char_count > 50000 or        # More than 50KB
            table_count > 100 or         # Many table cells
            code_block_count > 20        # Many code blocks
        )
        
        if is_large:
            self.logger.info(f"📊 Large document detected: {line_count} lines, {char_count} chars, optimizing...")
        
        return is_large
    
    def _process_content_in_chunks(self, content: str, chunk_size: int = 1000) -> List[Any]:
        """Process large content in chunks to optimize memory usage"""
        lines = content.split('\n')
        story = []
        
        # Process in chunks
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            # Process chunk with standard processing
            chunk_elements = self._process_markdown_content(chunk_content)
            story.extend(chunk_elements)
            
            # Add memory optimization break for very large documents
            if len(story) > 5000:  # Every 5000 elements, add a memory break
                story.append(Spacer(1, 0))  # Invisible spacer to help with memory
        
        return story


# Create alias for backward compatibility
ReportLabEngine = EnhancedReportLabEngine

if __name__ == "__main__":
    # Quick test
    engine = EnhancedReportLabEngine()
    test_content = """
# Test Professional Document

This is a **professional** document with *enhanced* styling.

## Code Example

```python
def hello_world():
    print("Hello, professional world!")
```

> This is a professional quote with beautiful styling.

## Features

- Professional color themes
- Enhanced typography  
- Beautiful code highlighting
- Modern layout design

The enhanced ReportLab engine provides Typst-quality output!
"""
    
    result = engine.generate(
        content=test_content,
        output_file=Path("test_enhanced.pdf"),
        template="technical", 
        title="Enhanced ReportLab Test",
        author="WOT-PDF Team"
    )
    
    print(f"Test result: {result}")
