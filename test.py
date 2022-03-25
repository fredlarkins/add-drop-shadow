from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

browser = Firefox()

browser.get('https://fontmeme.com/shadow-effect/')

file = 'C:\\Users\\Freddie.Larkins\\Documents\\add-drop-shadow\\profile.png'

elem = browser.find_element(by=By.XPATH,
                            value='//input[@type="file"]')

elem.send_keys(file)
