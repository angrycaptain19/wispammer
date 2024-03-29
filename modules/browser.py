import selenium
import json
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules import youtube


class BrowserDriver:

    def __init__(self, browser: str) -> None:
        self.driver = None
        self.silent = True
        self.youtube_player = None
        if "chrome" in browser.lower():
            self.driver = self.get_chrome_browser()

    def get_chrome_browser(self) -> webdriver:
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--mute-audio")

        profile_path = "./profiles/chrome"
        if not os.path.exists("./profiles"):
            os.mkdir("./profiles")

        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)
            os.mkdir(profile_path)

        options.add_argument(f'--user-data-dir={profile_path}')

        if self.silent:
            options.add_argument("--log-level=3");
        driver = webdriver.Chrome(executable_path="./webdrivers/chromedriver.exe", chrome_options=options)
        driver.delete_all_cookies()
        return driver

    def google_login(self) -> bool:
        self.driver.get("https://accounts.google.com/signin/v2/identifier?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&flowEntry=ServiceLogin")

        email = ""
        password = ""

        with open("config.json") as f:
            config = json.load(f)
            email = config["credentials"]["email"]
            password = config["credentials"]["password"]

        valid_credentials = email != "" and "@" in email and password != ""
        try:
            if not valid_credentials:
                email = input("Put the email you want to login to here: ")
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "identifierId"))).send_keys(email)
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button"))).click()
            if not valid_credentials:
                password = input("Put here the password for this account (you can put it on config.json to log in automatically): ")
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
        except Exception as e:
            return e
        return True

    def get_youtube(self, video_id) -> youtube.Youtube:
        self.driver.get(
            f"https://www.youtube.com/watch?v={video_id}?autoplay=0")
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[7]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string")))
        return youtube.Youtube(self.driver)
