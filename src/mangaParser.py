import requests
from bs4 import BeautifulSoup
import re
import json

from MangaEntities import Manga, Chapter, Page

headers = {
    "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "accept": "*/*"
}


class MangaParser:

    def __init__(self, url, begin=0, end=0):
        self.url = url
        self.titleEN = url[url.rfind("/") + 1:]
        self.html = self._get_html(url)
        self.begin = begin
        self.end = end

    def set_parsing_callback(self, callback):
        self.set_parsing_progress = callback

    def parse(self):
        soup = BeautifulSoup(self.html, "html.parser")

        title = self._parse_title(soup)
        author = self._parse_author(soup)
        coverLink, cover = self._parse_cover(soup)
        chapters = self._parse_chapters(soup)

        return Manga(title, self.titleEN, chapters, author, cover, coverLink)

    def _parse_title(self, soup):
        title = soup.find("h1", class_="manga-bg__title")
        if title == None:
            title = soup.find("div", class_="manga-title").find("h1")
        return title.text

    def _parse_author(self, soup):
        author = soup.find_all(
            "div", class_="info-list__row")[1].find("a")
        if author != None:
            return author.text
        return "unknown"

    def _parse_cover(self, soup):
        cover = soup.find("img", class_="manga__cover").get("src")
        return cover, "cover" + cover[cover.rfind("."):cover.rfind("?")]

    def _parse_chapters(self, soup):
        chapters = []
        chapterBlocks = soup.find_all("div", class_="chapter-item")
        chapterBlocks.reverse()

        bIndex = max(1, self.begin) - 1
        eIndex = self.end
        if eIndex == 0:
            eIndex = len(chapterBlocks)
        chapterBlocks2 = chapterBlocks[bIndex:eIndex]
        countChapters = len(chapterBlocks2)

        for index, chapter in enumerate(chapterBlocks2):
            dataId = chapter.get("data-id")
            description = requests.get(
                "https://mangalib.me/download/" + dataId, headers=headers).json()
            descriptionChapter = description.get("chapter")
            namesImages = description.get("images")
            chapterTitle = "Volume %s, chapter %s" % (
                descriptionChapter["volume"], descriptionChapter["number"])

            pages = []
            for i, image in enumerate(namesImages):
                link = "//manga/%s/chapters/%s/%s" % (
                    self.titleEN, descriptionChapter["slug"], image)
                extension = link[link.rfind("."):]
                title = chapterTitle + "_" + '{:04}'.format(i) + extension
                pages.append(Page(title, link))

            chapters.append(Chapter(bIndex + index + 1, chapterTitle, pages))
            
            if hasattr(self, "set_parsing_progress"):
                self.set_parsing_progress((index + 1) / countChapters)

        return chapters

    def _get_html(self, url):
        html = requests.get(url, headers=headers)
        if html.status_code == 200:
            return html.text
        else:
            raise Exception('Invalid link')
