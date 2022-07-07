import os
from fpdf import FPDF
from PIL import Image, ImageFilter
from console_progressbar import ProgressBar


class MangaPDFCreator:

    def __init__(self, path, manga, sizeLimit=0, fixedHeight=False):
        self.path = path
        self.manga = manga
        self.title = manga.titleEN
        self.sizeLimit = sizeLimit
        self.sizeIsLimited = sizeLimit != 0
        self.fixedHeight = fixedHeight
        self.PDFList = []

    def create(self):
        if self.fixedHeight:
            self._create(self._add_image_a4, self._add_title_a4)
        else:
            self._create(self._add_image, self._add_title)
        self._save_files()
        self.PDFList.clear()

    def set_creating_callback(self, callback):
        self.set_creating_progress = callback

    def set_saving_callback(self, callback):
        self.set_saving_progress = callback

    def _create(self, addImage, addTitle):
        currentSize = 0
        pdf = self._create_pdf()
        totalNumChapters = len(self.manga.chapters)
        lastNumChapter = self.manga.chapters[0].number - 1
        
        if hasattr(self, "set_creating_progress"):
                self.set_creating_progress(0)

        for index, chapter in enumerate(self.manga.chapters):
            chapterSize = self._convert_images(chapter.pages)

            if self.sizeIsLimited and currentSize != 0 and currentSize + chapterSize > self.sizeLimit:
                chapterCut = ((str)(lastNumChapter + 1))
                if lastNumChapter + 1 < chapter.number - 1:
                    chapterCut += "-" + ((str)(chapter.number - 1))
                self.PDFList.append((pdf, chapterCut))
                pdf = self._create_pdf()

                lastNumChapter = chapter.number - 1
                currentSize = chapterSize
            else:
                currentSize += chapterSize

            addTitle(pdf, chapter.title)
            for page in chapter.pages:
                addImage(pdf, os.path.join(self.path, page.title))

            if hasattr(self, "set_creating_progress"):
                self.set_creating_progress((index + 1) / totalNumChapters)

        chapterCut = ((str)(lastNumChapter + 1))
        if lastNumChapter + 1 < chapter.number:
            chapterCut += "-" + ((str)(chapter.number))
        self.PDFList.append((pdf, chapterCut))

    def _save_files(self):
        if hasattr(self, "set_saving_progress"):
                self.set_saving_progress(0)

        if len(self.PDFList) == 1:
            file, _ = self.PDFList[0]
            file.output(self.title + ".pdf")
        else:
            if not os.path.exists(self.title):
                os.mkdir(self.title)
            for file, rangeChapters in self.PDFList:
                path = os.path.join(
                    self.title, self.title + "_" + rangeChapters + ".pdf")
                file.output(path)
        
        if hasattr(self, "set_saving_progress"):
                self.set_saving_progress(1)

    def _create_pdf(self):
        pdf = FPDF("P", "mm")
        pdf.set_author(self.manga.author)
        pdf.set_display_mode("real")
        pdf.set_font("Arial", size=12)
        if self.manga.coverLink != "":
            self._add_image_a4(pdf, os.path.join(self.path, self.manga.cover))
        return pdf

    # returns the size of converted images
    def _convert_images(self, pages):
        size = 0
        for p in pages:
            imagePath = os.path.join(self.path, p.title)
            newPath = imagePath + ".jpg"
            image = Image.open(imagePath)
            jpg = image.convert("RGB")
            jpg.save(newPath)
            size += os.path.getsize(newPath)
            p.title += ".jpg"
            os.remove(imagePath)
        return size

    def _add_image(self, pdf, imagePath):
        image = Image.open(imagePath)
        (width, height) = image.size
        pdf.add_page(format=(pdf.w,
                             height / width * pdf.w))
        pdf.image(imagePath, x=0, y=0, h=pdf.h)

    def _add_image_a4(self, pdf, imagePath):
        image = Image.open(imagePath)
        (width, height) = image.size
        pdf.add_page()
        imageHeightOnPage = height * pdf.w / width
        imageWidthOnPage = width * pdf.h / height
        if imageHeightOnPage > pdf.h:
            x = (pdf.w - imageWidthOnPage) / 2
            pdf.image(imagePath, x=x, y=0, h=pdf.h)
        else:
            y = (pdf.h - imageHeightOnPage) / 2
            pdf.image(imagePath, x=0, y=y, w=pdf.w)

    def _add_title(self, pdf, title):
        pdf.add_page(format=(pdf.w, 20))
        x = (pdf.w - pdf.get_string_width(title)) / 2
        pdf.text(x, 12, title)

    def _add_title_a4(self, pdf, title):
        tempPDF = FPDF()
        tempPDF.set_font(pdf.font_family, size=pdf.font_size)
        tempPDF.add_page()
        tempPDF.text(0, 0, title)
        pdf.add_page()
        x = (pdf.w - pdf.get_string_width(title)) / 2
        y = (pdf.h - tempPDF.y) / 2
        pdf.text(x, y, title)
