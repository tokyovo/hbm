import requests
from bs4 import BeautifulSoup
import time
import logging
from decimal import Decimal
from celery import shared_task
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .models import Product, OptionCategory, OptionValue, Variant, Image, Collection

base_url = "https://hairbeautymart.com.au"

# Path to ChromeDriver
driver_path = "/usr/local/bin/chromedriver"

# Configure logging
logger = logging.getLogger(__name__)

@shared_task
def get_or_update_product_info(product_url):
    """
    Fetch or update the product information for the given product URL.
    """
    logger.info(f"Fetching or updating product info for: {product_url}")

    # Set up Selenium WebDriver options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-gpu')  # Applicable to windows OS only
    options.add_argument('--remote-debugging-port=9222')  # Required for Chrome to work in headless mode
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')  # Disable extensions that could interfere
    options.add_argument('--disable-application-cache')  # Avoid caching issues
    options.add_argument('--start-maximized')  # Start with a maximized window

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open the product page
        driver.get(product_url)
        time.sleep(3)  # Adjust based on page load time

        # Parse the HTML using BeautifulSoup
        response = requests.get(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the product title
        title_tag = soup.find('div', class_='product_form')
        title = title_tag.get('data-product', '').split('"title":"')[1].split('"')[0] if title_tag else 'Title not found'
        logger.info(f"Product Title: {title}")

        # Extract the product description
        description_tag = soup.find('div', class_='description content bottom has-padding-top')
        description = description_tag.get_text(separator='\n', strip=True) if description_tag else 'Description not found'
        logger.info(f"Product Description: {description}")

        # Extract image URL
        image_tag = soup.find('div', class_='image__container').find('img')
        image_url = 'https:' + image_tag['data-zoom-src'] if image_tag and 'data-zoom-src' in image_tag.attrs else None
        logger.info(f"Image URL: {image_url}")

        # Extract the price from the modal price section
        logger.info(f"Extracting price for {product_url}...")

        try:
            # Extract the price within the correct modal_price class
            price_element = soup.find('p', class_='modal_price subtitle').find('span', class_='current_price').find('span', class_='money')
            price_str = price_element.text.strip()
            logger.info(f"Raw price string: {price_str}")

            # Clean up the price string (remove currency symbols, commas, etc.)
            clean_price_str = price_str.replace('$', '').replace(' AUD', '').strip()
            price = Decimal(clean_price_str)  # Convert to Decimal
            logger.info(f"Clean price: {price}")

        except Exception as e:
            logger.error(f"Could not find price for {product_url}. Error: {str(e)}")
            price = Decimal('0.0')

        # Now, update the product in the database
        product_obj, _ = Product.objects.update_or_create(
            source_url=product_url,
            defaults={
                'title': title,
                'description': description,
                'price': price  # Always store the extracted price
            }
        )

        # Create or update the Image for the product, if an image URL was found
        if image_url:
            image_obj, _ = Image.objects.update_or_create(
                product=product_obj,
                defaults={
                    'url': image_url,
                    'alt_text': title  # You can adjust alt_text if necessary
                }
            )
            logger.info(f"Image linked to product: {product_obj.title} (URL: {image_url})")
        else:
            logger.info(f"No valid image URL found for product: {product_obj.title}")

        # Process product options (like Size or Color) and prices
        logger.info(f"Processing options for {product_url}...")

        # Initialize lists to store options and prices
        all_options = {}
        all_prices = {}

        select_containers = driver.find_elements(By.CLASS_NAME, 'select-container')

        if select_containers:
            for container in select_containers:
                try:
                    # Find the option category label (e.g., Size, Color) and dropdown
                    label = container.find_element(By.TAG_NAME, 'label').text.strip()
                    select_element = container.find_element(By.CSS_SELECTOR, 'select.single-option-selector')
                    logger.info(f"Found option category: {label}")

                    # Create lists to store the options and prices for this label
                    options_list = []
                    prices_list = []

                    # Create a Select object to interact with the dropdown
                    select = Select(select_element)

                    # Loop through each option in the dropdown
                    for option in select.options:
                        logger.info(f"Selecting option: {option.text}")
                        options_list.append(option.text)

                        # Select the option by visible text
                        select.select_by_visible_text(option.text)

                        # Wait for the price to update
                        time.sleep(2)  # Adjust if necessary

                        # Find and clean up the price element
                        try:
                            price_element = driver.find_element(By.CSS_SELECTOR, 'p.modal_price.subtitle .current_price .money')
                            price_str = price_element.text.strip()
                            logger.info(f"Raw price string: {price_str}")

                            # Clean up the price string (remove currency symbols, commas, etc.)
                            clean_price_str = price_str.replace('$', '').replace(' AUD', '').strip()
                            price = Decimal(clean_price_str)  # Convert to Decimal
                            logger.info(f"Clean price: {price}")
                            prices_list.append(price)

                        except Exception as e:
                            logger.error(f"Price element not found for option {option.text}. Error: {e}")
                            prices_list.append(Decimal('0.0'))

                    # Store the options and prices in the all_options and all_prices dictionaries
                    all_options[label] = options_list
                    all_prices[label] = prices_list

                except Exception as e:
                    logger.error(f"Error processing options for {product_url}: {str(e)}")
        
        # Create variants based on the available options
        for category, options_list in all_options.items():
            for i, option_value in enumerate(options_list):
                # Get or create OptionCategory and OptionValue
                option_category, _ = OptionCategory.objects.get_or_create(name=category)
                option_value_obj, _ = OptionValue.objects.get_or_create(category=option_category, value=option_value)

                # Create or update the Variant
                price = all_prices[category][i]
                variant_obj, _ = Variant.objects.update_or_create(
                    product=product_obj,
                    price=price
                )
                variant_obj.options.add(option_value_obj)
        
        product_obj.allow_update = False
        product_obj.save()

        logger.info(f"Finished processing product: {product_url}")

    except Exception as e:
        logger.error(f"Error processing product {product_url}: {str(e)}")

    finally:
        # Close the WebDriver
        driver.quit()

@shared_task
def get_collection_links_task(collection_limit=None, product_limit=None):
    """
    Celery task to fetch and store collection links and their products.
    This version adds detailed logging and progress tracking using tqdm.

    :param collection_limit: Optional limit for the number of collections to process.
    :param product_limit: Optional limit for the number of products to process per collection.
    """
    logger.info("Starting collection and product parsing task...")

    # Fetch collection links from the main page and the collections page
    collection_links = get_collection_links(base_url)
    collection_links.update(get_collection_links(f"{base_url}/collections"))

    # Apply the collection limit if provided
    if collection_limit:
        collection_links = list(collection_links)[:collection_limit]

    logger.info(f"Found {len(collection_links)} collections to process.")

    # Process each collection link
    for collection_link in tqdm(collection_links, desc="Processing collections"):
        logger.info(f"Processing collection: {collection_link}")
        
        # Get product links for each collection using Selenium
        product_links = get_product_links(collection_link)

        # Apply the product limit if provided
        if product_limit:
            product_links = list(product_links)[:product_limit]
        
        # Save collection to the database
        collection_obj, _ = Collection.objects.update_or_create(
            source_url=collection_link,
            defaults={'title': collection_link.split('/')[-1].replace('-', ' ').title()}
        )
        
        logger.info(f"Found {len(product_links)} products in collection: {collection_link}")
        
        # Store products in the collection
        for product_link in tqdm(product_links, desc=f"Processing products in {collection_link}"):
            logger.info(f"Processing product: {product_link}")
            
            product_obj, created = Product.objects.update_or_create(
                source_url=product_link,
                defaults={
                    'title': product_link.split('/')[-1].replace('-', ' ').title(),
                    'description': 'Auto-generated description'
                }
            )
            collection_obj.products.add(product_obj)
            if created:
                logger.info(f"Created new product: {product_obj.title}")
            else:
                logger.info(f"Updated existing product: {product_obj.title}")

    logger.info("Completed collection and product parsing task.")


def get_collection_links(url):
    logger.info(f"Fetching URL: {url}")
    response = requests.get(url)
    time.sleep(2)  # Wait for content to load

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all links that match the pattern "/collections/***"
        links = {a['href'] for a in soup.find_all('a', href=True) if '/collections/' in a['href']}
        
        # Ensure all links have the full base URL
        full_links = {link if link.startswith("http") else base_url + link for link in links}
        
        logger.info(f"Found {len(full_links)} collection links on {url}")
        return full_links
    else:
        logger.error(f"Failed to fetch {url} with status code: {response.status_code}")
        return set()


def get_product_links(collection_url):
    """
    Fetch product links by scrolling the collection page using Selenium.
    """
    logger.info(f"Fetching products from {collection_url} using Selenium with scrolling.")
    
    # Set up the WebDriver options (headless mode for running in the background)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (without opening a window)
    options.add_argument('--disable-dev-shm-usage')  # Avoid shared memory issues in limited environments
    options.add_argument('--no-sandbox')
    
    # Set up ChromeDriver service
    service = Service(driver_path)
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=options)
    
    product_links = set()
    
    try:
        # Load the collection page
        driver.get(collection_url)
        
        # Scroll and gather product links
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new products to load
            time.sleep(10)
            
            # Find all product links
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            for element in elements:
                link = element.get_attribute('href')
                product_links.add(link)
            
            # Calculate new scroll height and compare with the last height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Exit loop if no more content is loaded
            
            last_height = new_height
        
        logger.info(f"Found {len(product_links)} product links on {collection_url}")
        
    except Exception as e:
        logger.error(f"Error fetching product links from {collection_url}: {str(e)}")
    
    finally:
        # Close the WebDriver
        driver.quit()
    
    return product_links
