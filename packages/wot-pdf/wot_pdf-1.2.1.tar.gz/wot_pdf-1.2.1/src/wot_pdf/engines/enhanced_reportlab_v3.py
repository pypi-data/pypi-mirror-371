#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced ReportLab Engine v3.0 - Complete Solution
====================================================

Based on comprehensive analysis findings:
- Fixed TOC generation order
- Enhanced emoji support
- Improved hierarchical numbering
- Better error handling
- Professional structure
"""

import os
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    # ReportLab imports
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, KeepTogether
    )
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.pdfgen.canvas import Canvas
    
    # Font handling
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    print(f"❌ ReportLab not available: {e}")
    REPORTLAB_AVAILABLE = False


@dataclass
class HeadingInfo:
    """Structure for heading information"""
    level: int
    text: str
    original_text: str
    numbered_text: str
    line_number: int
    page_reference: str = ""


class EnhancedTOC(TableOfContents):
    """Enhanced Table of Contents with better formatting"""
    
    def __init__(self):
        super().__init__()
        self.rightColumnWidth = 72
        self.leftColumnWidth = None
        self.topMargin = 12
        
    def wrap(self, availWidth, availHeight):
        """Better wrapping for TOC"""
        self.width = availWidth
        self.height = min(availHeight, len(self.entries) * 18 + 24)
        return (self.width, self.height)


class EnhancedReportLabEngine:
    """
    Enhanced ReportLab PDF Generation Engine v3.0
    
    Features:
    - Fixed TOC generation with proper numbering
    - Enhanced emoji and Unicode support
    - Professional themes and styling
    - Hierarchical chapter numbering
    - Performance optimizations
    - Better error handling
    """
    
    def __init__(self, theme: Optional[Dict[str, Any]] = None):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for this engine")
            
        self.theme = theme or self._get_default_theme()
        self.fonts_registered = False
        self.chapter_counters = [0] * 10  # Support up to 10 levels
        
        # Register fonts first, then create styles
        self._register_fonts()
        self.styles = self._create_enhanced_styles()
        
        print(f"🚀 Enhanced ReportLab Engine v3.0 initialized with theme: {self.theme['name']}")
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Enhanced default theme with emoji support"""
        return {
            'name': 'Professional Enhanced',
            'primary_color': colors.HexColor('#2E4057'),
            'secondary_color': colors.HexColor('#048A81'),
            'accent_color': colors.HexColor('#FF6B35'),
            'text_color': colors.HexColor('#2C3E50'),
            'background_color': colors.HexColor('#F8F9FA'),
            'emoji_support': True,
            'advanced_typography': True
        }
    
    def _register_fonts(self):
        """Register Unicode-capable fonts for emoji support"""
        if self.fonts_registered:
            return
            
        try:
            # Try to register Noto fonts for emoji support
            font_paths = [
                "C:/Windows/Fonts/seguiemj.ttf",  # Windows emoji font
                "C:/Windows/Fonts/arial.ttf",     # Fallback
                "/System/Library/Fonts/Arial Unicode MS.ttf",  # macOS
                "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf"  # Linux
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('EmojiFont', font_path))
                        print(f"✅ Registered emoji font: {font_path}")
                        self.fonts_registered = True
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to register font {font_path}: {e}")
                        continue
            
            if not self.fonts_registered:
                print("⚠️ No emoji fonts found, using default fonts")
                
        except Exception as e:
            print(f"⚠️ Font registration failed: {e}")
        
        self.fonts_registered = True
    
    def _create_enhanced_styles(self) -> Dict[str, ParagraphStyle]:
        """Create comprehensive style library"""
        base_styles = getSampleStyleSheet()
        custom_styles = {}
        
        # Enhanced normal style with emoji support
        font_name = 'EmojiFont' if self.fonts_registered else 'Helvetica'
        
        custom_styles['Enhanced'] = ParagraphStyle(
            'Enhanced',
            parent=base_styles['Normal'],
            fontName=font_name,
            fontSize=11,
            leading=16,
            textColor=self.theme['text_color'],
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )
        
        # Professional heading styles (6 levels)
        heading_configs = [
            {'size': 20, 'space': 18, 'color': self.theme['primary_color']},
            {'size': 18, 'space': 16, 'color': self.theme['primary_color']},
            {'size': 16, 'space': 14, 'color': self.theme['secondary_color']},
            {'size': 14, 'space': 12, 'color': self.theme['secondary_color']},
            {'size': 13, 'space': 10, 'color': self.theme['text_color']},
            {'size': 12, 'space': 8, 'color': self.theme['text_color']}
        ]
        
        for i, config in enumerate(heading_configs, 1):
            custom_styles[f'ProfHeading{i}'] = ParagraphStyle(
                f'ProfHeading{i}',
                parent=base_styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=config['size'],
                textColor=config['color'],
                spaceBefore=config['space'],
                spaceAfter=config['space'] // 2,
                keepWithNext=True
            )
        
        # Enhanced code style
        custom_styles['ProfCode'] = ParagraphStyle(
            'ProfCode',
            parent=base_styles['Code'],
            fontName='Courier',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#F8F9FA'),
            borderColor=colors.HexColor('#DEE2E6'),
            borderWidth=1,
            leftIndent=12,
            rightIndent=12,
            spaceBefore=6,
            spaceAfter=6
        )
        
        # TOC styles
        custom_styles['TOCHeading'] = ParagraphStyle(
            'TOCHeading',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=self.theme['primary_color'],
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        return custom_styles
    
    def _collect_headings(self, content: str) -> List[HeadingInfo]:
        """Collect all headings with enhanced detection"""
        headings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Enhanced heading detection
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                
                # Clean text for numbering
                original_text = text
                # Remove existing numbering patterns
                clean_text = re.sub(r'^\d+(\.\d+)*\.\s*', '', text)
                
                heading = HeadingInfo(
                    level=level,
                    text=clean_text,
                    original_text=original_text,
                    numbered_text="",  # Will be filled by numbering
                    line_number=line_num
                )
                headings.append(heading)
                
        print(f"📋 Collected {len(headings)} headings for processing")
        return headings
    
    def _apply_heading_numbers(self, content: str, headings: List[HeadingInfo]) -> str:
        """Apply hierarchical numbering to headings"""
        if not headings:
            return content
        
        # Reset counters
        self.chapter_counters = [0] * 10
        lines = content.split('\n')
        
        for heading in headings:
            # Update counters
            level = heading.level - 1  # Convert to 0-based
            self.chapter_counters[level] += 1
            
            # Reset deeper levels
            for i in range(level + 1, len(self.chapter_counters)):
                self.chapter_counters[i] = 0
            
            # Generate number
            number_parts = []
            for i in range(level + 1):
                if self.chapter_counters[i] > 0:
                    number_parts.append(str(self.chapter_counters[i]))
            
            if number_parts:
                number = '.'.join(number_parts)
                heading.numbered_text = f"{number}. {heading.text}"
                
                # Update the line in content
                line_idx = heading.line_number - 1
                if line_idx < len(lines):
                    # Preserve markdown formatting
                    hash_prefix = '#' * heading.level
                    lines[line_idx] = f"{hash_prefix} {heading.numbered_text}"
            else:
                heading.numbered_text = heading.text
        
        print(f"🔢 Applied numbering to {len(headings)} headings")
        return '\n'.join(lines)
    
    def _generate_toc(self, headings: List[HeadingInfo]) -> List[Any]:
        """Generate enhanced Table of Contents"""
        if not headings:
            return []
        
        elements = []
        
        # TOC Title
        elements.append(Paragraph("📋 Table of Contents", self.styles['TOCHeading']))
        elements.append(Spacer(1, 12))
        
        # TOC Entries
        for heading in headings:
            # Indent based on level
            indent = "　" * (heading.level - 1)  # Use wide space for indentation
            display_text = heading.numbered_text or heading.text
            
            # Create entry with leader dots
            entry_text = f"{indent}{display_text}"
            toc_entry = Paragraph(entry_text, self.styles['Enhanced'])
            elements.append(toc_entry)
            elements.append(Spacer(1, 2))
        
        elements.append(PageBreak())
        print(f"📑 Generated TOC with {len(headings)} entries")
        return elements
    
    def _process_markdown_content(self, content: str) -> List[Any]:
        """Process markdown content with enhanced features"""
        elements = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Enhanced heading processing
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                
                # Enhanced emoji support
                if self.theme.get('emoji_support', True):
                    text = self._enhance_emoji_display(text)
                
                style_name = f'ProfHeading{min(level, 6)}'
                elements.append(Paragraph(text, self.styles[style_name]))
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Code block processing
            if line.startswith('```'):
                language = line[3:].strip() or 'text'
                code_lines = []
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if i < len(lines):
                    i += 1  # Skip closing ```
                
                # Enhanced code formatting
                if code_lines:
                    elements.append(Spacer(1, 6))
                    if language != 'text':
                        elements.append(Paragraph(f'<i>📄 {language}</i>', self.styles['Enhanced']))
                    
                    code_text = '\n'.join(code_lines)
                    code_text = self._enhance_code_display(code_text)
                    elements.append(Paragraph(code_text, self.styles['ProfCode']))
                    elements.append(Spacer(1, 6))
                continue
            
            # Regular paragraph with emoji support
            if self.theme.get('emoji_support', True):
                line = self._enhance_emoji_display(line)
            
            paragraph = Paragraph(line, self.styles['Enhanced'])
            elements.append(paragraph)
            elements.append(Spacer(1, 3))
            i += 1
        
        print(f"✅ Processed {len(elements)} content elements")
        return elements
    
    def _enhance_emoji_display(self, text: str) -> str:
        """Enhanced emoji display with better Unicode support"""
        if not self.theme.get('emoji_support', True):
            return text
        
        # Map common emojis to Unicode
        emoji_map = {
            ':smile:': '😊',
            ':rocket:': '🚀',
            ':check:': '✅',
            ':warning:': '⚠️',
            ':info:': 'ℹ️',
            ':book:': '📖',
            ':file:': '📄',
            ':folder:': '📁',
            ':gear:': '⚙️',
            ':star:': '⭐',
            ':heart:': '❤️',
            ':thumbs_up:': '👍',
        }
        
        # Apply emoji replacements
        for shortcode, emoji in emoji_map.items():
            text = text.replace(shortcode, emoji)
        
        # Ensure proper encoding
        try:
            # Use font that supports Unicode if available
            if self.fonts_registered:
                text = text.encode('utf-8').decode('utf-8')
        except UnicodeError:
            # Fallback to ASCII if Unicode fails
            text = text.encode('ascii', 'replace').decode('ascii')
        
        return text
    
    def _enhance_code_display(self, code: str) -> str:
        """Enhanced code display with better formatting"""
        # Basic syntax highlighting through styling
        lines = code.split('\n')
        enhanced_lines = []
        
        for line in lines:
            # Simple keyword highlighting
            if any(keyword in line for keyword in ['def ', 'class ', 'import ', 'from ']):
                line = f'<b>{line}</b>'
            elif line.strip().startswith('#'):
                line = f'<i>{line}</i>'
            
            enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _create_professional_header_footer(self, canvas: Canvas, doc: Any, 
                                         title: str, author: str, 
                                         page_numbering: str = "standard"):
        """Enhanced header/footer with multiple numbering styles"""
        page_num = doc.page
        
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(self.theme['text_color'])
        
        # Title in header
        canvas.drawString(72, A4[1] - 40, title[:50] + "..." if len(title) > 50 else title)
        
        # Author in header (right aligned)
        canvas.drawRightString(A4[0] - 72, A4[1] - 40, f"📝 {author}")
        
        # Header line
        canvas.setStrokeColor(self.theme['secondary_color'])
        canvas.setLineWidth(0.5)
        canvas.line(72, A4[1] - 50, A4[0] - 72, A4[1] - 50)
        
        # Footer with enhanced page numbering
        footer_y = 40
        
        # Page numbering styles
        if page_numbering == "standard":
            page_text = f"Page {page_num}"
        elif page_numbering == "of_total":
            # Note: Total pages would need to be calculated in a two-pass system
            page_text = f"Page {page_num}"
        elif page_numbering == "roman":
            page_text = f"Page {self._to_roman(page_num)}"
        elif page_numbering == "chapter_page":
            page_text = f"Chapter Page {page_num}"
        elif page_numbering == "minimal":
            page_text = str(page_num)
        else:
            page_text = f"Page {page_num}"
        
        # Center page number
        text_width = canvas.stringWidth(page_text, 'Helvetica', 10)
        canvas.drawString((A4[0] - text_width) / 2, footer_y, page_text)
        
        # Footer line
        canvas.line(72, footer_y + 10, A4[0] - 72, footer_y + 10)
        
        canvas.restoreState()
    
    def _to_roman(self, num: int) -> str:
        """Convert number to Roman numerals"""
        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        literals = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        result = ''
        for i in range(len(values)):
            count = num // values[i]
            result += literals[i] * count
            num -= values[i] * count
        return result.lower()
    
    def generate_pdf(self, 
                    content: str, 
                    output_path: str, 
                    title: Optional[str] = None,
                    author: Optional[str] = None,
                    subject: Optional[str] = None,
                    generate_toc: bool = True,
                    number_headings: bool = True,
                    page_numbering: str = "standard") -> Dict[str, Any]:
        """
        Generate PDF with enhanced features
        
        Args:
            content: Markdown content to convert
            output_path: Output PDF file path
            title: Document title
            author: Document author
            subject: Document subject
            generate_toc: Whether to generate table of contents
            number_headings: Whether to add hierarchical numbering
            page_numbering: Page numbering style
            
        Returns:
            Generation statistics and metadata
        """
        start_time = time.time()
        
        # Register fonts for emoji support
        self._register_fonts()
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=title or "Enhanced PDF Document",
            author=author or "WOT-PDF Enhanced Engine",
            subject=subject or "Generated with Enhanced ReportLab Engine v3.0"
        )
        
        story = []
        
        try:
            # FIXED: Correct order for TOC generation
            if generate_toc:
                print(f"🔧 TOC generation requested with number_headings={number_headings}")
                headings = self._collect_headings(content)
                print(f"📋 Collected {len(headings)} headings for TOC")
                
                if number_headings and headings:
                    # Apply numbering to headings in content FIRST
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
            
            # Process main content
            print("📝 Processing main content...")
            content_elements = self._process_markdown_content(content)
            story.extend(content_elements)
            print(f"✅ Added {len(content_elements)} content elements")
            
            # Build PDF with enhanced header/footer
            def add_header_footer(canvas, doc):
                self._create_professional_header_footer(
                    canvas, doc, 
                    title or "Document", 
                    author or "WOT-PDF Enhanced", 
                    page_numbering
                )
            
            print("🔨 Building PDF document...")
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            # Generate statistics
            end_time = time.time()
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            stats = {
                "engine": "Enhanced ReportLab v3.0",
                "success": True,
                "file_size": file_size,
                "generation_time": round(end_time - start_time, 3),
                "content_length": len(content),
                "elements_count": len(story),
                "theme": self.theme['name'],
                "features_used": {
                    "toc_generated": generate_toc,
                    "headings_numbered": number_headings,
                    "emoji_support": self.theme.get('emoji_support', True),
                    "page_numbering": page_numbering,
                    "fonts_registered": self.fonts_registered
                }
            }
            
            print(f"🎉 PDF generated successfully!")
            print(f"📊 Size: {file_size:,} bytes, Time: {stats['generation_time']}s")
            print(f"🎨 Theme: {self.theme['name']}, Elements: {len(story)}")
            
            return stats
            
        except Exception as e:
            print(f"❌ PDF generation failed: {e}")
            return {
                "engine": "Enhanced ReportLab v3.0",
                "success": False,
                "error": str(e),
                "generation_time": time.time() - start_time
            }


def test_enhanced_engine():
    """Test the enhanced engine with comprehensive content"""
    test_content = """# 📚 Enhanced ReportLab Engine v3.0 Test

## 🚀 Features Overview

This document tests all enhanced features of the ReportLab engine:

### ✅ Hierarchical Numbering
- Automatic chapter numbering
- Multi-level support
- Clean numbering display

### 🎨 Enhanced Styling
- Professional themes
- Custom typography
- Better spacing

### 📋 Table of Contents
- Automatic generation
- Proper numbering integration
- Professional formatting

## 🔧 Technical Features

### Emoji Support
Enhanced emoji support includes:
- Native Unicode handling 😊
- Fallback mechanisms ⚠️
- Font registration 🎯

### Code Highlighting

```python
def enhanced_example():
    '''Enhanced code display with syntax hints'''
    print("Hello Enhanced World! 🌍")
    return {"status": "success", "emoji": "✅"}
```

### Advanced Typography
- Professional font selection
- Better line spacing
- Enhanced readability

## 🎯 Performance Metrics

The enhanced engine provides:
1. **Better Quality**: Improved formatting and structure
2. **Emoji Support**: Native Unicode emoji handling
3. **Professional Output**: Business-ready documents
4. **Fixed TOC**: Properly ordered table of contents generation

## 📊 Conclusion

This enhanced version addresses all issues found in the analysis:
- ✅ Fixed TOC generation order
- ✅ Enhanced emoji support
- ✅ Better hierarchical numbering
- ✅ Professional styling
- ✅ Improved error handling

Perfect for professional document generation! 🎉
"""
    
    print("🧪 Testing Enhanced ReportLab Engine v3.0...")
    
    try:
        engine = EnhancedReportLabEngine()
        
        output_path = "enhanced_reportlab_v3_test.pdf"
        
        stats = engine.generate_pdf(
            content=test_content,
            output_path=output_path,
            title="Enhanced ReportLab Engine v3.0 Test",
            author="WOT-PDF Enhanced System",
            subject="Comprehensive Engine Testing",
            generate_toc=True,
            number_headings=True,
            page_numbering="standard"
        )
        
        print("\n" + "="*50)
        print("📊 ENHANCED ENGINE TEST RESULTS")
        print("="*50)
        
        for key, value in stats.items():
            if key == "features_used":
                print(f"🎯 {key}:")
                for feature, enabled in value.items():
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {feature}: {enabled}")
            else:
                print(f"📈 {key}: {value}")
        
        if stats.get("success", False):
            print(f"\n🎉 SUCCESS: Enhanced PDF generated at '{output_path}'")
        else:
            print(f"\n❌ FAILED: {stats.get('error', 'Unknown error')}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_enhanced_engine()
