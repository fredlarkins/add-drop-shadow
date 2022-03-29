

from email.mime import image
import shutil
from PIL import Image
import exif
from pathlib import Path
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys


def resize(image_fp:Path):
    with Image.open(image_fp) as img:
        img.load()
    
    # creating a file path for the modified file
    modified_fp = Path('modified', image_fp.name)
    
    # if the image is greater than 1000 pixels wide (otherwise we're not bothered)
    if img.width > 1000:
        
        # specifying a max width of 1000 pixels
        new_width = 1000
        new_height = round(img.height * (1000 / img.width))
        
        # resizing the image
        print('\tResizing...')
        img = img.resize((new_width, new_height))
        
        # saving to the modified file path
        img.save(fp = modified_fp)
        
        # adding metadata to the image to signal that it has been resized
        with open(modified_fp, 'rb') as i:
            
            # instantating the exif.Image() object
            ex = exif.Image(i)
            
            # setting the 'image description' exif attribute to 'resized'
            ex.image_description = 'Resized by Python'
        
        with open(modified_fp, 'wb') as i:
            
            # writing it back to the file object we created above, i
            i.write(ex.get_file())
    
    else:
        # we haven't done anything to the image, we're just going to save it into the modified folder
        print('\tNo resize necessary.')
        img.save(modified_fp)
    
    return modified_fp



def convert_to_webp(source:Path):
    '''
    Credit: https://www.webucator.com/tutorial/using-python-to-convert-images-to-webp/
    '''
    # specifying destination path
    destination = Path('webp-images', source.with_suffix('.webp').name)
    print('\tConverting to webp...')
    image = Image.open(source)  # Open image
    image.save(destination, format="webp")  # Convert image to webp
    print('\tSuccess!')




def add_drop_shadow(modified_image_fp:Path):
    
    # specifying our options for browser to be headless
    options = Options()
    options.headless = True
    
    # instantiating our browser
    browser = Firefox(options=options)
    
    # navigating to font meme's drop shadow generator
    print('\tRequesting FontMeme\'s drop shadow page...')
    browser.get('https://fontmeme.com/shadow-effect/')
    
    # locating the input button for the file and uploading it
    try:
        image_input = WebDriverWait(
            driver=browser,
            timeout=10
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@type="file"]')
            )
        )
        
    # in case locating the element fails
    except:
        '''
        To do: some sort of notification system for failed uploads.
        '''
        sys.exit('Could not locate image input!')
    
    try:
        # uploading the image
        # using the 'raw' filepath of the photo (with Path.resolve()) to circumvent...
        # ... issues with double backslash in windoes file paths
        # see resources:
            # - double slashes: https://stackoverflow.com/questions/54377047/pathlib-return-non-windows-path-with-double-slash
            # - Path.resolve(): https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve
        image_input.send_keys(rf'{modified_image_fp.resolve()}')
        
        # when an image uploads correctly, a 'clear' button appears in case the user want to use a different image
        # it's a good test for whether the image uploaded, and is an implicit wait for the function to cease doing stuff until the image is uploaded
        clear_me_button = WebDriverWait(
            driver=browser,
            timeout=30
        ).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="clearme"]')
            )
        )
        print('\tImage uploaded successfully.')
        
    except:
        sys.exit('Image did not upload properly!')
    
    # finding the colour selector for our drop shadow
    colour_selector = browser.find_element(By.XPATH, '//*[@id="colorSelector"]')
    colour_selector.click()
    
    # clicking on the dark grey option for colour
    grey = browser.find_element(By.CSS_SELECTOR, 'div.jscolor-palette-sample:nth-child(29) > div:nth-child(1)')
    grey.click()

    # clicking on the preset shadow size dropdown
    preset_dropdown = browser.find_element(By.XPATH, '//*[@id="effect_a_title"]')
    preset_dropdown.click()
    
    # choosing preset 'B', aka 10 x 20 px
    preset_B = browser.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[1]/div/div[4]/div/div/div[3]/div[2]/ul/li[2]/span')
    preset_B.click()
    
    # when you select a preset, FontMeme actually goes ahead and applies the shadow
    # the 'Generate' button appears when the image is fully generated - I assume that's for the case where the user wants to change the shadow...
    # .. and RE-generate the image
    # as such, it's a useful signifier of whether the image with drop shadow has generated properly
    try:
        generate_button = WebDriverWait(
            browser,
            60
        ).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, '.gradientred')
        ))
    except:
        sys.exit('\tTimed out waiting for the image to generate!')

    # waiting for the generated image to be visible
    try:
        image = WebDriverWait(
            browser,
            45
        ).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="text_image"]')
            )
        )
        print('\tImage generated with drop shadow.')
    except:
        sys.exit('\tImage did not render properly!')
    
    # finally, we've got the url from which we'll download the image w/ drop shadow
    temp_image_url = image.get_attribute('src')
    
    # streaming the image with requests
    print('\tDownloading image with drop shadow...')
    r = requests.get(temp_image_url, stream=True)
    
    # reformatting the filename to be a png file (if it was, for instance, a jpg)
    # source: https://stackoverflow.com/questions/54152653/renaming-file-extension-using-pathlib-python-3
    png_path = modified_image_fp.with_suffix('.png')
    
    # deleting the original image (i.e. so we don't get jpg and png versions)
    # source: https://docs.python.org/3/library/pathlib.html#pathlib.Path.unlink
    modified_image_fp.unlink()
    
    # # writing that bytes response to a file using shutil
    # print('Re-writing original image...')
    # with open(modified_image_fp, 'wb') as f:
    #     shutil.copyfileobj(r.raw, f)
    #     print('✔️')

    png_path.write_bytes(r.content)

    browser.close()
    return png_path


def main(image:Path):
    print(f'#--- Begin process for {image.name} ---#')
    # resizing
    mod_image = resize(image)
    
    # adding drop shadow
    png_path = add_drop_shadow(mod_image)
    
    # replacing old name with 'completed' so for loop knows when to stop
    image.replace(image.with_stem(f'{image.stem}__COMPLETED'))
    
    # converting to webp
    convert_to_webp(png_path)
    print(f'#--- End process for {image.name} ---#\n')

    
for image in Path('images-to-modify').iterdir():
    if '__COMPLETED' in image.stem:
        continue
    else:
        main(image)