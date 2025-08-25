"""
Yahoo Finance web scraper for real-time quote data.
"""
import re
import time
from typing import Optional


import requests
from bs4 import BeautifulSoup
from fast_tradier.interfaces.IRealTimeQuoteProvider import IRealTimeQuoteProvider


class YahooFinanceQuoteScraper(IRealTimeQuoteProvider):
    """
    Yahoo Finance web scraper that implements IRealTimeQuoteProvider interface.
    
    Scrapes real-time price data from Yahoo Finance web pages.
    """
    
    BASE_URL = "https://finance.yahoo.com/quote/"
    
    def __init__(self, timeout: int = 10, retry_count: int = 3, retry_delay: float = 1.0):
        """
        Initialize the Yahoo Finance scraper.
        
        Args:
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        
        # Headers to mimic a real browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get the current price for a given symbol from Yahoo Finance.
        
        Args:
            symbol: The ticker symbol (e.g., 'AAPL', '^GSPC')
            
        Returns:
            The current price as a float, or None if not available
        """
        if not symbol:
            return None
            
        symbol = symbol.strip().upper()
        url = f"{self.BASE_URL}{symbol}"
        
        for attempt in range(self.retry_count):
            try:                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                price = self._extract_price_from_html(response.text, symbol)
                if price is not None:
                    return price
                else:
                    raise ValueError("Price extraction failed")
            except Exception as e:
                print("exception: ", e)

            # Wait before retrying (except on last attempt)
            if attempt < self.retry_count - 1:
                time.sleep(self.retry_delay)

        return None

    def _extract_price_from_html(self, html: str, symbol: str) -> Optional[float]:
        """
        Extract the current price from Yahoo Finance HTML content.
        
        Args:
            html: The HTML content from Yahoo Finance
            symbol: The ticker symbol for logging
            
        Returns:
            The extracted price as float, or None if not found
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Strategy 1: Look for the main price element with data-symbol attribute
            price_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
            if price_element:
                price_text = price_element.get('value') or price_element.text.strip()
                return self._parse_price(price_text)
            
            # Strategy 2: Look for span with specific classes (backup method)
            price_selectors = [
                f'fin-streamer[data-symbol="{symbol}"]',
                'span[data-reactid*="price"]',
                '.Trsdu\(0\.3s\).Fw\(b\).Fz\(36px\).Mb\(-4px\).D\(ib\)',
                '.Fw\\(b\\).Fz\\(36px\\).Mb\\(-4px\\).D\\(ib\\)'
            ]
            
            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get('value') or element.text.strip()
                    if price_text and self._is_valid_price(price_text):
                        return self._parse_price(price_text)
            
            # Strategy 3: Regex search for price patterns in the HTML
            price_patterns = [
                rf'"regularMarketPrice":\{{"raw":([\d\.]+)',
                rf'"regularMarketPrice":\{{"fmt":"([\d,\.]+)"',
                rf'data-symbol="{symbol}"[^>]*value="([\d,\.]+)"'
            ]
            
            for pattern in price_patterns:
                matches = re.search(pattern, html)
                if matches:
                    price_text = matches.group(1)
                    return self._parse_price(price_text)
            return None
            
        except Exception as e:
            print("exception: ", e)
            return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse a price string into a float.
        
        Args:
            price_text: The price text to parse
            
        Returns:
            The parsed price as float, or None if parsing fails
        """
        try:
            if not price_text:
                return None
                
            # Remove common formatting characters
            cleaned = price_text.replace(',', '').replace('$', '').strip()
            
            if cleaned and self._is_valid_price(cleaned):
                return float(cleaned)
                
        except (ValueError, TypeError) as e:
            print("exception: ", e)

        return None

    def _is_valid_price(self, price_text: str) -> bool:
        """
        Check if a price string looks valid.
        
        Args:
            price_text: The price text to validate
            
        Returns:
            True if the price looks valid, False otherwise
        """
        if not price_text:
            return False
            
        # Remove common formatting and check if it's a valid number
        cleaned = price_text.replace(',', '').replace('$', '').strip()
        
        try:
            price = float(cleaned)
            return price > 0 and price < 1000000  # Reasonable price range
        except (ValueError, TypeError):
            return False

    def close(self):
        """Close the session to free resources."""
        if hasattr(self, 'session'):
            self.session.close()