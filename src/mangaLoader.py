import os
import shutil
import requests
import time
from selenium import webdriver
from MangaEntities import Page
from PIL import Image

servers = [
    "img2.emanga.ru",       # classic
    "img3.mangalib.org",    # may be
    "img4.imgslib.ru"       # test
    "img3.ranobelib.me",    # compress
]


class MangaLoader:
    def __init__(self, path, manga):
        self.path = path
        self.manga = manga

    def set_loading_callback(self, callback):
        self.set_loading_progress = callback

    def download(self):
        if hasattr(self, "set_loading_progress"):
                    self.set_loading_progress(0)
        current_server = 0
        self._create_dir()
        pages = self._get_pages()

        while len(pages) > 0:
            driver = self._get_driver()
            self._enable_download_in_headless_chrome(driver)
            for index, page in enumerate(pages):
                link = "https://" + servers[current_server] + page.link
                self._download_image(driver, link, page.title)
                if hasattr(self, "set_loading_progress"):
                    self.set_loading_progress((index + 1) / len(pages))
            self._download_image(
                driver, self.manga.coverLink, self.manga.cover)

            time.sleep(2)
            self._remove_downloaded(pages)
            current_server += 1
            if current_server > len(servers):
                raise Exception()

    def _enable_download_in_headless_chrome(self, driver):
        path = os.path.join(os.getcwd(), self.path)
        driver.command_executor._commands["send_command"] = (
            "POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {
            'behavior': 'allow', 'downloadPath': path}}
        driver.execute("send_command", params)

    def _get_driver(self):
        attempts = 0
        while attempts < 5:
            try:
                options = webdriver.ChromeOptions()
                options.add_experimental_option(
                    "prefs", {'profile.default_content_setting_values.automatic_downloads': 1})
                options.add_argument("headless")
                options.add_experimental_option(
                    'excludeSwitches', ['enable-logging'])
                driver = webdriver.Chrome(chrome_options=options)
                return driver
            except:
                attempts += 1

    def _download_image(self, driver, link, name):
        driver.get(link)
        driver.execute_script(
            "var gh = '%s';var a  = document.createElement('a');a.href = gh;a.download = '%s';a.click()" %
            (link, name))

    def _remove_downloaded(self, pages):
        downloaded = os.listdir(self.path)
        temp = []
        broken = []
        for p in pages:
            for file in downloaded:
                if p.title == file:
                    try:
                        img = Image.open(os.path.join(self.path, file))
                        img.verify()
                        temp.append(p)
                    except:
                        broken.append(os.path.join(self.path, file))
        for t in temp:
            pages.remove(t)
        for b in broken:
            while True:
                try:
                    os.remove(b)
                    break
                except:
                    time.sleep(2)

    def _get_pages(self):
        pages = []
        for chapter in self.manga.chapters:
            for page in chapter.pages:
                pages.append(page)
        return pages

    def _create_dir(self):
        try:
            os.mkdir(self.path)
        except Exception:
            shutil.rmtree(self.path)
            os.mkdir(self.path)
