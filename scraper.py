import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
from tqdm import tqdm

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.data_dir = "data"
        self.scraped_data_file = os.path.join(self.data_dir, "scraped_data.json")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def is_valid_url(self, url):
        """Check if URL belongs to the same domain."""
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def clean_text(self, text):
        """Clean extracted text by removing extra whitespace."""
        return " ".join(text.split())

    def extract_content(self, soup):
        """Extract meaningful content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text(separator=" ")
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_desc = meta_tag.get("content", "")

        return {
            "title": self.clean_text(title),
            "meta_description": self.clean_text(meta_desc),
            "content": self.clean_text(text)
        }

    def scrape_website(self):
        """Scrape the website and save data if not already scraped."""
        if os.path.exists(self.scraped_data_file):
            print("Website data already exists. Skipping scraping.")
            with open(self.scraped_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        pages_data = []
        urls_to_visit = [self.base_url]
        
        with tqdm(desc="Scraping pages") as pbar:
            while urls_to_visit:
                current_url = urls_to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                    
                try:
                    response = requests.get(current_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract content
                        content = self.extract_content(soup)
                        content['url'] = current_url
                        pages_data.append(content)
                        
                        # Find new links
                        for link in soup.find_all('a', href=True):
                            url = urljoin(current_url, link['href'])
                            if self.is_valid_url(url) and url not in self.visited_urls:
                                urls_to_visit.append(url)
                        
                        self.visited_urls.add(current_url)
                        pbar.update(1)
                    
                except Exception as e:
                    print(f"Error scraping {current_url}: {str(e)}")
                    continue

        # Save scraped data
        with open(self.scraped_data_file, 'w', encoding='utf-8') as f:
            json.dump(pages_data, f, ensure_ascii=False, indent=2)

        return pages_data

if __name__ == "__main__":
    scraper = WebScraper("https://www.inwebinfo.com")
    scraper.scrape_website() 