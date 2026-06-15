"""
Run this from inside task6_visual_automation folder.
Switches target URLs from demo.opencart.com to books.toscrape.com
"""

with open("config.py", "r") as f:
    content = f.read()

old = '''PAGES = [
    {"id": "home",   "url": "https://demo.opencart.com/"},
    {"id": "search", "url": "https://demo.opencart.com/index.php?route=product/search&search=camera"},
    {"id": "login",  "url": "https://demo.opencart.com/index.php?route=account/login"},
]'''

new = '''PAGES = [
    {"id": "home",      "url": "https://books.toscrape.com/"},
    {"id": "catalogue", "url": "https://books.toscrape.com/catalogue/page-1.html"},
    {"id": "mystery",   "url": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"},
]'''

if old in content:
    content = content.replace(old, new)
    with open("config.py", "w") as f:
        f.write(content)
    print("Done — config.py updated to books.toscrape.com successfully.")
else:
    print("ERROR: Could not find PAGES section. Check config.py manually.")
    print("Manually replace the PAGES section with:")
    print(new)
