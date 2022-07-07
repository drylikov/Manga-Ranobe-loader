import os
import io
from PIL import Image
import uuid
import requests
from ebooklib import epub

class RanobeEpubCreator:

    def __init__(self, ranobe):
        self.ranobe = ranobe
        self.title = ranobe.titleEN

    def create(self):
        if hasattr(self, "set_creating_progress"):
            self.set_creating_progress(0)
        book = epub.EpubBook()
        book.set_identifier("urn:uuid:" + (str)(uuid.uuid4()))
        book.set_language('ru')
        book.set_title(self.ranobe.title)
        book.add_author(self.ranobe.author)
        self._set_cover(book)

        chapterLinks = []
        chapters = []
        chapterCount = len(self.ranobe.chapters)
        for index, ch in enumerate(self.ranobe.chapters):
            fileName = ("%05d" % ch.number) + '.xhtml'
            chapter = epub.EpubHtml(
                title=ch.title, file_name=fileName, lang='hr')
            title = "<h1>" + ch.title + "</h1>"
            chapter.content = title + ch.content
            book.add_item(chapter)
            chapters.append(chapter)
            chapterLinks.append(epub.Link(fileName, ch.title, fileName))
            if hasattr(self, "set_creating_progress"):
                self.set_creating_progress((index + 1) / chapterCount)

        book.toc = chapterLinks
        book.spine = ['nav', *chapters]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        if hasattr(self, "set_saving_progress"):
            self.set_saving_progress(0)
        epub.write_epub(self.title + '.epub', book, {})
        if hasattr(self, "set_saving_progress"):
            self.set_saving_progress(1)

    def set_creating_callback(self, callback):
        self.set_creating_progress = callback

    def set_saving_callback(self, callback):
        self.set_saving_progress = callback

    def _set_cover(self, book):
        path = "cover.jpg"
        book.add_metadata(None, 'meta', '', {
                          "name": "cover", "content": "image_0"})

        p = requests.get(self.ranobe.coverLink)
        out = open(path, 'wb')
        out.write(p.content)
        out.close()

        img = Image.open(path)
        b = io.BytesIO()
        img.save(b, 'jpeg')
        b_img = b.getvalue()

        cover = epub.EpubImage()
        cover.file_name = path
        cover.media_type = 'image/jpeg'
        cover.content = b_img
        book.add_item(cover)
        os.remove(path)
