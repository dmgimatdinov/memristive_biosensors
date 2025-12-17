"""Google Patents parser - extract and save patent information to PDF.

Usage (CLI):
    python google_patents_parser.py --url "https://patents.google.com/patent/US1234567B2" --output patent.pdf

Extracts: abstract, description, claims from Google Patents page and saves to PDF.
"""
from __future__ import annotations

import sys
import argparse
import re
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
except ImportError:
    SimpleDocTemplate = None


def fetch_patent_page(url: str) -> Optional[str]:
    """Fetch Google Patents page HTML.
    
    Note: Google Patents uses JavaScript rendering. For better results with complex pages,
    consider using Selenium. This uses requests which may not capture all content.
    """
    if requests is None:
        raise RuntimeError("requests is not installed. Install with: pip install requests")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching patent page: {e}", file=sys.stderr)
        return None


def extract_text_between_tags(soup: BeautifulSoup, tag: str, class_name: Optional[str] = None) -> str:
    """Extract text from specific HTML tags."""
    if class_name:
        elem = soup.find(tag, class_=class_name)
    else:
        elem = soup.find(tag)
    
    return elem.get_text(strip=True) if elem else ""


def parse_patent_data(html: str) -> Dict[str, Any]:
    """Parse patent information from HTML."""
    if BeautifulSoup is None:
        raise RuntimeError("BeautifulSoup is not installed. Install with: pip install beautifulsoup4")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    data: Dict[str, Any] = {
        'title': '',
        'status': '',
        'year': '',
        'abstract': '',
        'description': '',
        'claims': '',
    }
    
    # Extract title
    title_elem = soup.find('h1', class_='title')
    if title_elem:
        data['title'] = title_elem.get_text(strip=True)
    else:
        # Try alternative selectors
        title_elem = soup.find('span', class_='title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
    
    # Extract status (pending/granted)
    status_elem = soup.find(string=re.compile(r'(Pending|Granted|Published)'))
    if status_elem:
        status_text = status_elem.get_text(strip=True).lower()
        if 'pending' in status_text:
            data['status'] = 'pending'
        elif 'granted' in status_text:
            data['status'] = 'granted'
    
    # Extract filing/grant date for year
    date_elem = soup.find(string=re.compile(r'\d{4}-\d{2}-\d{2}'))
    if date_elem:
        date_match = re.search(r'(\d{4})', str(date_elem))
        if date_match:
            data['year'] = date_match.group(1)
    
    # Extract abstract
    abstract_section = soup.find('section', class_=re.compile(r'abstract', re.I))
    if abstract_section:
        abstract_text = abstract_section.find('p')
        if abstract_text:
            data['abstract'] = abstract_text.get_text(strip=True)
    else:
        # Try finding by heading
        for heading in soup.find_all(['h2', 'h3']):
            if 'abstract' in heading.get_text().lower():
                next_p = heading.find_next('p')
                if next_p:
                    data['abstract'] = next_p.get_text(strip=True)
                break
    
    # Extract description
    description_section = soup.find('section', class_=re.compile(r'description', re.I))
    if description_section:
        paragraphs = description_section.find_all('p')
        data['description'] = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:5]])  # First 5 paragraphs
    else:
        # Try finding by heading
        for heading in soup.find_all(['h2', 'h3']):
            if 'description' in heading.get_text().lower():
                next_p = heading.find_next('p')
                if next_p:
                    data['description'] = next_p.get_text(strip=True)
                break
    
    # Extract claims
    claims_section = soup.find('section', class_=re.compile(r'claims', re.I))
    if claims_section:
        claim_texts = claims_section.find_all(re.compile(r'li|div'), class_=re.compile(r'claim', re.I))
        if claim_texts:
            data['claims'] = '\n\n'.join([c.get_text(strip=True)[:200] for c in claim_texts[:3]])  # First 3 claims
    else:
        # Try finding by heading
        for heading in soup.find_all(['h2', 'h3']):
            if 'claims' in heading.get_text().lower():
                next_section = heading.find_next(['div', 'section'])
                if next_section:
                    claim_items = next_section.find_all(re.compile(r'li|p'))
                    data['claims'] = '\n\n'.join([item.get_text(strip=True)[:200] for item in claim_items[:3]])
                break
    
    return data


def extract_title_words(title: str, num_words: int = 3) -> str:
    """Extract first N meaningful words from title."""
    # Remove patent designations and common words
    stop_words = {'and', 'or', 'the', 'a', 'an', 'of', 'for', 'in', 'on', 'with', 'by', 'to'}
    
    # Split and filter
    words = [w.replace(',', '').replace('.', '') for w in title.split()]
    meaningful_words = [w for w in words if w.lower() not in stop_words and len(w) > 2]
    
    return '_'.join(meaningful_words[:num_words]).lower()


def generate_filename(patent_data: Dict[str, Any]) -> str:
    """Generate filename based on patent data.
    
    Format: [pending_]YYYY_word1_word2_word3.pdf
    """
    parts = []
    
    # Add pending prefix if status is pending
    if patent_data.get('status') == 'pending':
        parts.append('pending')
    
    # Add year
    if patent_data.get('year'):
        parts.append(patent_data['year'])
    
    # Add three words from title
    title_words = extract_title_words(patent_data.get('title', 'patent'), num_words=3)
    if title_words:
        parts.append(title_words)
    else:
        parts.append('patent')
    
    # Join and add extension
    filename = '_'.join(parts) + '.pdf'
    
    # Clean up invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('__', '_')
    
    return filename


def create_pdf(patent_data: Dict[str, Any], output_path: str) -> bool:
    """Create PDF document with patent information."""
    if SimpleDocTemplate is None:
        print("reportlab is not installed. Install with: pip install reportlab", file=sys.stderr)
        return False
    
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2e5c8a'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=4,  # justify
        )
        
        # Title and metadata
        title = patent_data.get('title', 'Patent Document')
        story.append(Paragraph(title, title_style))
        
        # Metadata
        metadata = []
        if patent_data.get('status'):
            metadata.append(f"<b>Status:</b> {patent_data['status'].capitalize()}")
        if patent_data.get('year'):
            metadata.append(f"<b>Year:</b> {patent_data['year']}")
        
        if metadata:
            story.append(Paragraph(" | ".join(metadata), body_style))
            story.append(Spacer(1, 12))
        
        # Abstract section
        if patent_data.get('abstract'):
            story.append(Paragraph("Abstract", heading_style))
            abstract_text = patent_data['abstract']
            if len(abstract_text) > 1000:
                abstract_text = abstract_text[:1000] + "..."
            story.append(Paragraph(abstract_text, body_style))
            story.append(Spacer(1, 12))
        
        # Description section
        if patent_data.get('description'):
            story.append(Paragraph("Description", heading_style))
            description_text = patent_data['description']
            if len(description_text) > 2000:
                description_text = description_text[:2000] + "..."
            story.append(Paragraph(description_text, body_style))
            story.append(Spacer(1, 12))
        
        # Claims section
        if patent_data.get('claims'):
            story.append(PageBreak() if len(story) > 10 else Spacer(1, 12))
            story.append(Paragraph("Claims", heading_style))
            claims_text = patent_data['claims']
            if len(claims_text) > 1500:
                claims_text = claims_text[:1500] + "..."
            story.append(Paragraph(claims_text, body_style))
        
        # Build PDF
        doc.build(story)
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}", file=sys.stderr)
        return False


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Parse Google Patents and save information to PDF"
    )
    parser.add_argument(
        "--url", "-u",
        required=True,
        help="Google Patents URL (e.g., https://patents.google.com/patent/US1234567B2)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output PDF file path (auto-generated if not specified)"
    )
    
    args = parser.parse_args(argv)
    
    # Fetch and parse
    print(f"Fetching patent page: {args.url}", file=sys.stderr)
    html = fetch_patent_page(args.url)
    if not html:
        return 1
    
    print("Parsing patent data...", file=sys.stderr)
    patent_data = parse_patent_data(html)
    
    # Generate output path
    output_path = args.output or generate_filename(patent_data)
    
    print(f"Creating PDF: {output_path}", file=sys.stderr)
    if create_pdf(patent_data, output_path):
        print(f"Success! PDF saved to: {output_path}", file=sys.stderr)
        return 0
    else:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
