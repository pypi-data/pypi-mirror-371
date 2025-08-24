"""Chrome client using undetected-chromedriver for web scraping Reddit pages not available via API."""

import asyncio
import logging
import os
import time
import random
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class ChromeClient:
    """Client for interacting with undetected Chrome to scrape Reddit web pages."""

    def __init__(self):
        self.driver: Optional[uc.Chrome] = None

    def _get_chrome_driver(self) -> uc.Chrome:
        """Create and configure undetected Chrome driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        # Chrome options for stealth
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--disable-javascript")  # For basic scraping, we don't need JS
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        
        # Set headless mode
        options.add_argument("--headless=new")
        
        # Get custom Chrome executable path if set
        chrome_executable = os.getenv('CHROME_EXECUTABLE_PATH', '/opt/google/chrome/google-chrome')
        
        try:
            if os.path.exists(chrome_executable):
                options.binary_location = chrome_executable
                logger.info(f"Using Chrome executable: {chrome_executable}")
            
            # Create undetected Chrome driver
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True,
                headless=True
            )
            
            # Set implicit wait and page load timeout
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise

    def _human_like_delay(self, min_delay: float = 0.5, max_delay: float = 2.0) -> None:
        """Add human-like delays between actions."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    async def scrape_best_communities(self, page: int = 1) -> Dict[str, Any]:
        """Scrape Reddit's best communities page.

        Args:
            page: Page number to scrape (1-10)

        Returns:
            Dictionary containing communities data and pagination info
        """
        url = f"https://www.reddit.com/best/communities/{page}/"
        logger.info(f"Scraping best communities page {page}")

        driver = None
        try:
            # Run the synchronous webdriver operations in a thread pool
            def _scrape_sync():
                nonlocal driver
                driver = self._get_chrome_driver()
                
                # Navigate to the page
                logger.info(f"Navigating to {url}")
                driver.get(url)
                
                # Add human-like delay
                self._human_like_delay(1.0, 3.0)
                
                # Wait for content to load
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/r/"]'))
                    )
                except TimeoutException:
                    logger.warning("Timeout waiting for subreddit links, proceeding anyway")
                
                # Get page source and parse with BeautifulSoup
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract community data
                communities = []
                subreddit_map = {}
                
                # Find all subreddit links
                subreddit_links = soup.find_all('a', href=lambda x: x and x.startswith('/r/'))
                
                for link in subreddit_links:
                    href = link.get('href', '')
                    # Extract subreddit name from href like /r/subredditname
                    if href.startswith('/r/'):
                        subreddit_name = href.split('/')[2] if len(href.split('/')) > 2 else None
                        if subreddit_name and subreddit_name not in subreddit_map:
                            # Look for member count in surrounding elements
                            member_count = ''
                            parent = link.parent
                            
                            # Search parent elements for member count
                            for _ in range(5):
                                if parent:
                                    text = parent.get_text()
                                    # Look for member count patterns
                                    import re
                                    member_match = re.search(r'(\d+(?:\.\d+)?[KM]?)\s*members', text, re.IGNORECASE)
                                    if member_match:
                                        member_count = member_match.group(0)
                                        break
                                    parent = parent.parent
                                else:
                                    break
                            
                            subreddit_map[subreddit_name] = {
                                'name': subreddit_name,
                                'url': f"https://www.reddit.com{href}",
                                'members': member_count
                            }
                
                # Convert to list and add ranking
                communities_list = list(subreddit_map.values())
                for i, community in enumerate(communities_list):
                    community['rank'] = i + 1 + (page - 1) * 30
                
                # Limit to 30 communities per page
                communities_list = communities_list[:30]
                
                # Extract pagination info
                current_page = page
                has_next = len(communities_list) == 30  # Simple heuristic
                has_prev = page > 1
                
                return {
                    'communities': communities_list,
                    'pagination': {
                        'currentPage': current_page,
                        'totalPages': 10,  # Reddit typically shows 10 pages
                        'hasNext': has_next and page < 10,
                        'hasPrev': has_prev
                    }
                }
            
            # Run the synchronous operation in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _scrape_sync)
            return result
            
        except Exception as e:
            logger.error(f"Error scraping best communities: {e}")
            raise
        finally:
            # Clean up driver
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
                self.driver = None

    async def close(self):
        """Close the Chrome driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None