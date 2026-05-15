from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

driver = webdriver.Chrome()

url = "https://www.shl.com/solutions/products/product-catalog/"

driver.get(url)

time.sleep(10)

links = driver.find_elements(By.TAG_NAME, "a")

products = []

for link in links:

    text = link.text.strip()
    href = link.get_attribute("href")

    if href and "product-catalog/view" in href:

        product = {
            "name": text,
            "url": href
        }

        products.append(product)

# Remove duplicates
unique_products = []

seen = set()

for product in products:

    if product["url"] not in seen:

        seen.add(product["url"])
        unique_products.append(product)

# Save JSON
with open("catalog.json", "w", encoding="utf-8") as file:

    json.dump(unique_products, file, indent=4)

print("Catalog saved successfully")
print("Total products:", len(unique_products))

driver.quit()