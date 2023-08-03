import re
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import date


class EmailExtractor:
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.visited_urls = set()
        self.email_addresses = set()
        self.filter_criteria = {}

    def extract_emails(self, filter_criteria=None):
        self.filter_criteria = filter_criteria
        self.crawl_website(self.starting_url)
        self.filter_emails()
        self.validate_emails()
        self.save_emails_to_database()
        self.generate_report()

    def crawl_website(self, url):
        if url not in self.visited_urls:
            self.visited_urls.add(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    email_addresses = self.extract_email_addresses_from_page(soup)
                    self.email_addresses.update(email_addresses)
                    for link in soup.find_all('a', href=True):
                        link_url = self.get_absolute_url(url, link['href'])
                        if link_url:
                            self.crawl_website(link_url)
            except requests.exceptions.RequestException:
                pass

    def extract_email_addresses_from_page(self, soup):
        email_addresses = set()
        email_pattern = re.compile(r'[-.\w]{1,64}@[-.\w]{1,255}\.[a-zA-Z]{2,6}')
        email_matches = re.findall(email_pattern, str(soup))
        email_addresses.update(email_matches)

        for tag in soup.find_all('a', attrs={'href': re.compile('^mailto:')}):
            # Removing 'mailto:' part from the email address
            email_addresses.add(tag['href'][7:])

        return email_addresses

    def filter_emails(self):
        if self.filter_criteria:
            filtered_email_addresses = set()
            for email_address in self.email_addresses:
                if any(keyword in email_address for keyword in self.filter_criteria.get('keywords', [])) or any(
                        domain_name in email_address.split('@')[1] for domain_name in self.filter_criteria.get('domain_names', [])):
                    filtered_email_addresses.add(email_address)
            self.email_addresses = filtered_email_addresses

    def validate_emails(self):
        validated_email_addresses = set()
        for email_address in self.email_addresses:
            if self.validate_email_address(email_address):
                validated_email_addresses.add(email_address)
        self.email_addresses = validated_email_addresses

    def validate_email_address(self, email_address):
        return re.match(r'^[-.\w]{1,64}@[-.\w]{1,255}\.[a-zA-Z]{2,6}$', email_address) is not None

    def save_emails_to_database(self):
        # TODO: Implement code to save emails to the database here
        pass

    def generate_report(self):
        report = f"Source URL: {self.starting_url}\n"
        report += f"Date of extraction: {date.today()}\n"
        report += f"Applied filters: {json.dumps(self.filter_criteria)}\n"
        report += "Email addresses:\n"
        for email_address in self.email_addresses:
            report += f"- {email_address}\n"
        print(report)

    def get_absolute_url(self, base_url, href):
        if href.startswith('/'):
            parsed_url = urlparse(base_url)
            return f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
        elif urlparse(href).netloc == urlparse(base_url).netloc:
            return href
        else:
            return None


if __name__ == '__main__':
    starting_url = input("Enter the starting URL: ")
    filter_criteria = {
        'domain_names': ['example.com'],
        'keywords': ['sales'],
    }
    extractor = EmailExtractor(starting_url)
    extractor.extract_emails(filter_criteria)