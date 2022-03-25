import shutil

import requests
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Creating a headless browser object
options = Options()
options.headless = True
browser = Firefox(options=options)


# Opening up the FontMeme drop shadow page
browser.get('https://fontmeme.com/shadow-effect/')


#

