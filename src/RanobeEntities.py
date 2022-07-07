class Ranobe:
    def __init__(self, title, titleEN, chapters, author = "", cover = "", coverLink = ""):
        self.title = title
        self.titleEN = titleEN
        self.author = author
        self.chapters = chapters
        self.cover = cover
        self.coverLink = coverLink


class Chapter:
    def __init__(self, number, title, content):
        self.number = number
        self.title = title
        self.content = content