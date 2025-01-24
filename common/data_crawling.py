from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def download_file(download_path="C:/Users/sue01/Downloads"):
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_path,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "directory_upgrade": True,
                "safebrowsing.enabled": True  # 안전 브라우징 비활성화
            }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    try:
        # Open the webpage
        url = "https://stat.molit.go.kr/portal/cate/statView.do?hRsId=58&hFormId=5498&hSelectId=5498&hPoint=00&hAppr=1&hDivEng=&oFileName=&rFileName=&midpath=&sFormId=5498&sStart=201101&sEnd=202412&sStyleNum=2&settingRadio=xlsx"
        driver.get(url)
        time.sleep(20)  # Wait for the page to load

        # Locate the download button
        download_button = driver.find_element(By.ID, "fileDownBtn")
        ActionChains(driver).move_to_element(download_button).click().perform()
        time.sleep(10)

        # Click the download button
        download_button1 = driver.find_element(By.XPATH, '//*[@id="file-download-modal"]/div[2]/div[3]/button')
        ActionChains(driver).move_to_element(download_button1).click().perform()
        time.sleep(30)  # Wait for the file to download

        print(f"File has been downloaded to {download_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
        
download_file()
