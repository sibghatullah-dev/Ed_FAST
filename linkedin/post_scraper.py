"""
LinkedIn Post Scraper using Selenium
Integrated version for EdFast platform
"""

import os
import time
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from google.oauth2.service_account import Credentials
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.discovery import build
    import pyperclip
    SELENIUM_AVAILABLE = True
except ImportError:
    print("Warning: Selenium or Google API dependencies not installed. LinkedIn post scraping will not be available.")
    SELENIUM_AVAILABLE = False

class LinkedInPostScraper:
    """
    LinkedIn Post Scraper using Selenium WebDriver.
    Integrated with EdFast platform for social media monitoring.
    """
    
    def __init__(self, user_data_dir: Optional[str] = None, headless: bool = False):
        self.selenium_available = SELENIUM_AVAILABLE
        self.driver = None
        self.user_data_dir = user_data_dir or "chrome_user_data"
        self.headless = headless
        self.image_save_folder = "downloaded_images"
        self.drive_folder_id = None  # Set this if you want to upload to Google Drive
        
        if not self.selenium_available:
            print("⚠️ Selenium not available. Install with: pip install selenium")
    
    def setup_chrome(self) -> bool:
        """Setup Chrome WebDriver with appropriate options."""
        if not self.selenium_available:
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_argument("--start-maximized")
            
            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920,1080")
            
            if self.user_data_dir:
                user_data_path = os.path.join(os.getcwd(), self.user_data_dir)
                chrome_options.add_argument(f"user-data-dir={user_data_path}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            return False
    
    def login_to_linkedin(self) -> bool:
        """Login to LinkedIn (manual login required)."""
        if not self.driver:
            return False
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Check if already logged in
            if "feed" in self.driver.current_url or "in/" in self.driver.current_url:
                print("✅ Already logged in!")
                return True
            
            print("🔐 Please complete the login manually in the browser...")
            input("Press Enter after completing the login...")
            time.sleep(5)
            
            print("✅ Login successful!")
            return True
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def download_image(self, img_url: str, filename: str) -> Optional[str]:
        """Download an image from a URL and save it locally."""
        if not os.path.exists(self.image_save_folder):
            os.makedirs(self.image_save_folder)
        
        file_path = os.path.join(self.image_save_folder, filename)
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    for chunk in response.itercontent(1024):
                        file.write(chunk)
                return file_path
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
        return None
    
    def upload_to_drive(self, file_path: str) -> Optional[str]:
        """Upload file to Google Drive and return shareable link."""
        if not self.drive_folder_id or not os.path.exists("credentials.json"):
            return None
        
        try:
            creds = Credentials.from_service_account_file(
                "credentials.json", 
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            drive_service = build("drive", "v3", credentials=creds)
            
            file_metadata = {
                "name": os.path.basename(file_path),
                "parents": [self.drive_folder_id]
            }
            media = MediaFileUpload(file_path, mimetype="image/jpeg")
            file = drive_service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields="id"
            ).execute()
            
            file_id = file.get("id")
            drive_service.permissions().create(
                body={"role": "reader", "type": "anyone"}, 
                fileId=file_id
            ).execute()
            
            return f"https://drive.google.com/uc?id={file_id}"
        except Exception as e:
            print(f"❌ Error uploading to Drive: {e}")
            return None
    
    def scroll_to_element(self, element) -> None:
        """Scroll smoothly to a specific element."""
        if self.driver:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1.5)
    
    def scrape_posts_from_profile(self, profile_url: str, max_posts: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape posts from a LinkedIn profile or company page.
        
        Args:
            profile_url (str): LinkedIn profile or company page URL
            max_posts (int): Maximum number of posts to scrape
            
        Returns:
            List[Dict[str, Any]]: List of scraped post data
        """
        if not self.selenium_available or not self.driver:
            raise ImportError("Selenium not available. Please install with: pip install selenium")
        
        all_data = []
        last_processed_index = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Navigate to profile
        self.driver.get(profile_url)
        time.sleep(5)
        
        ul_xpath = "//ul[contains(@class, 'display-flex flex-wrap list-style-none justify-center')]"
        li_xpath = "./li"
        more_options_xpath = ".//button[contains(@class, 'feed-shared-control-menu__trigger')]"
        
        while len(all_data) < max_posts:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find post elements
            try:
                ul_element = self.driver.find_element(By.XPATH, ul_xpath)
                post_elements = ul_element.find_elements(By.XPATH, li_xpath)
            except:
                print("❌ Could not find post elements")
                break
            
            print(f"🔄 Total posts found: {len(post_elements)}")
            
            # Process new posts
            for post in post_elements[last_processed_index:]:
                if len(all_data) >= max_posts:
                    break
                
                try:
                    self.scroll_to_element(post)
                    
                    # Get post URL
                    post_url = "N/A"
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, more_options_xpath))
                        )
                        more_button = post.find_element(By.XPATH, more_options_xpath)
                        self.driver.execute_script("arguments[0].click();", more_button)
                        time.sleep(1.5)
                        
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//h5[normalize-space()='Copy link to post']"))
                        )
                        post.find_element(By.XPATH, "//h5[normalize-space()='Copy link to post']").click()
                        post_url = pyperclip.paste()
                    except:
                        pass
                    
                    # Determine post type
                    post_type = "Shared" if post.find_elements(
                        By.XPATH, ".//div[contains(@class, 'feed-shared-update-v2__update-content-wrapper')]"
                    ) else "Original"
                    
                    # Extract post content
                    post_content = "N/A"
                    try:
                        post_container = post.find_element(
                            By.XPATH, ".//div[contains(@class, 'feed-shared-update-v2__description')]"
                        )
                        text_spans = post_container.find_elements(By.XPATH, ".//span[@dir='ltr']")
                        post_content = " ".join(
                            span.text.strip() for span in text_spans if span.text.strip()
                        ) if text_spans else post_container.text.strip()
                    except:
                        pass
                    
                    # Extract engagement metrics
                    like_count = "0"
                    comment_count = "0"
                    repost_count = "0"
                    try:
                        counts = post.find_elements(
                            By.XPATH, ".//button[contains(@class, 'social-details-social-counts__count-value')]"
                        )
                        like_count = counts[0].get_attribute("aria-label").split(" ")[0] if len(counts) > 0 else "0"
                        comment_count = counts[1].get_attribute("aria-label").split(" ")[0] if len(counts) > 1 else "0"
                        repost_count = counts[2].get_attribute("aria-label").split(" ")[0] if len(counts) > 2 else "0"
                    except:
                        pass
                    
                    # Extract post date
                    post_date = "N/A"
                    try:
                        post_date_container = post.find_element(
                            By.XPATH, ".//span[contains(@class, 'update-components-actor__sub-description')]"
                        )
                        post_date_element = post_date_container.find_element(
                            By.XPATH, ".//span[contains(@class, 'visually-hidden')]"
                        )
                        post_date = post_date_element.text.strip()
                    except:
                        pass
                    
                    # Extract image
                    img_url = "N/A"
                    img_drive_link = "No Image"
                    try:
                        image_elements = post.find_elements(
                            By.XPATH, ".//img[contains(@class, 'ivm-view-attr__img')]"
                        )
                        if len(image_elements) > 1:
                            img_url = image_elements[1].get_attribute("src")
                        elif len(image_elements) > 0:
                            img_url = image_elements[0].get_attribute("src")
                        
                        if img_url != "N/A":
                            filename = f"post_image_{time.time()}.jpg"
                            local_image_path = self.download_image(img_url, filename)
                            if local_image_path and self.drive_folder_id:
                                img_drive_link = self.upload_to_drive(local_image_path) or "Upload Failed"
                    except:
                        pass
                    
                    post_data = {
                        "post_url": post_url,
                        "type": post_type,
                        "content": post_content,
                        "like_count": like_count,
                        "comment_count": comment_count,
                        "repost_count": repost_count,
                        "img_url": img_url,
                        "image_drive_link": img_drive_link,
                        "post_date": post_date,
                        "profile_url": profile_url.split("/recent-activity")[0],
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    all_data.append(post_data)
                    print(f"✅ Scraped post {len(all_data)}: {post_content[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Error processing post: {e}")
                    continue
            
            # Update last processed index
            last_processed_index = len(post_elements)
            
            # Check if reached bottom
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("✅ Reached end of posts")
                break
            last_height = new_height
        
        return all_data
    
    def save_posts_to_excel(self, posts_data: List[Dict[str, Any]], filename: str = "linkedin_posts.xlsx") -> str:
        """Save scraped posts data to Excel file."""
        df = pd.DataFrame(posts_data)
        df.to_excel(filename, index=False)
        print(f"✅ Data saved to {filename}")
        return filename
    
    def format_posts_for_api(self, posts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format posts data for API response."""
        return posts_data
    
    def close(self) -> None:
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
