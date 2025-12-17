import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def search_patents(keyword, start_year, end_year):
    base_url = "https://patents.google.com/usearch"
    links = set()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    page = 1
    
    while True:
        params = {
            'q': keyword,
            'before_date': f'{end_year}-12-31',
            'after_date': f'{start_year}-01-01',
            'p': page
        }
        
        try:
            response = session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        all_links = soup.find_all('a', href=True)
        page_has_patents = False
        
        for link in all_links:
            href = link.get('href', '')
            if '/patent/' in href:
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin('https://patents.google.com/', href)
                
                if full_url.startswith('https://patents.google.com/patent/'):
                    links.add(full_url)
                    page_has_patents = True
        
        if not page_has_patents:
            break
        
        page += 1
        time.sleep(1)
    
    return links

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python gpp_links.py <keyword> <start_year> <end_year>", file=sys.stderr)
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    try:
        start_year = int(sys.argv[2])
        end_year = int(sys.argv[3])
    except ValueError:
        print("Error: Years must be integers", file=sys.stderr)
        sys.exit(1)
    
    if start_year > end_year:
        print("Error: Start year must be <= end year", file=sys.stderr)
        sys.exit(1)
    
    try:
        links = search_patents(keyword, start_year, end_year)
        
        if not links:
            print("No patents found", file=sys.stderr)
            sys.exit(1)
        
        with open('patents_links.txt', 'w', encoding='utf-8') as f:
            for link in sorted(links):
                f.write(link + '\n')
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
