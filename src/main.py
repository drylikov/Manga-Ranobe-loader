from colorama import init as coloramaInit
from colorama import Fore, Style

import os
import time
import shutil
from console_progressbar import ProgressBar

from MangaPDFCreator import MangaPDFCreator
from MangaParser import MangaParser
from MangaLoader import MangaLoader
from RanobeEpubCreator import RanobeEpubCreator
from RanobeParser import RanobeParser


coloramaInit()
downloadPath = "download_manga"


def main():
    try:
        while True:
            urls = get_urls()
            sleep = put_to_sleep()

            for typeUrl, url, begin, end, fixedHeight, sizeLimit in urls:
                print()
                print(Fore.BLUE + url)
                print(Style.RESET_ALL, end="")
                try:
                    if typeUrl == "manga":
                        get_manga(url, begin, end, fixedHeight, sizeLimit)
                    else:
                        get_ranobe(url, begin, end)
                except:
                    print()
                    print(Fore.RED + "Invalid link")
                    continue
            print()
            print(Style.RESET_ALL, end="")
            if sleep:
                sleep_pc()

    except:
        try:
            shutil.rmtree(downloadPath)
        except:
            pass


def get_manga(url, begin, end, fixedHeight, sizeLimit):
    manga = parse_manga(url, begin, end)
    if len(manga.chapters) == 0:
        print(
            Fore.RED + "The selected range does not include any chapters")
        return
    download_manga(manga)
    create_manga(manga, fixedHeight, sizeLimit)
    shutil.rmtree(downloadPath)
    print(Fore.GREEN + "Finished: " + manga.title.strip())


def get_ranobe(url, begin, end):
    ranobe = parse_ranobe(url, begin, end)
    if len(ranobe.chapters) == 0:
        print(
            Fore.RED + "The selected range does not include any chapters")
        return
    create_ranobe(ranobe)
    print(Fore.GREEN + "Finished: " + ranobe.title.strip())


def parse_manga(url, begin, end):
    progressBar = ProgressBar(total=100, prefix='Parsing  ',
                              length=50, fill='X', zfill='-')

    def setProgress(progress):
        progressBar.print_progress_bar(progress * 100)
    parser = MangaParser(url, begin, end)
    parser.set_parsing_callback(setProgress)
    return parser.parse()


def download_manga(manga):
    progressBar = ProgressBar(total=100, prefix='Loading  ',
                              length=50, fill='X', zfill='-')

    def setProgress(progress):
        progressBar.print_progress_bar(progress * 100)
    while True:
        try:
            loader = MangaLoader(downloadPath, manga)
            loader.set_loading_callback(setProgress)
            loader.download()
            break
        except:
            print()
            print(Fore.RED + "An error occurred during loading")
            print(Fore.BLUE +
                  "Google Chrome is required for the program to work")
            print(Fore.WHITE + "Try again (y/n): ", end="")
            answer = input()
            if answer == "y" or answer == "н":
                continue
            break


def create_manga(manga, fixedHeight, sizeLimit):
    progressBar = ProgressBar(total=100, prefix='Creating ',
                              length=50, fill='X', zfill='-')

    def setProgress(progress):
        progressBar.print_progress_bar(progress * 100)

    def setSavingProgress(progress):
        if progress == 0:
            print("\rSaving...", end="")
        else:
            print("\r         \r", end="")
    creator = MangaPDFCreator(downloadPath, manga, sizeLimit, fixedHeight)
    creator.set_creating_callback(setProgress)
    creator.set_saving_callback(setSavingProgress)
    creator.create()


def parse_ranobe(url, begin, end):
    progressBar = ProgressBar(total=100, prefix='Parsing  ',
                              length=50, fill='X', zfill='-')

    def setProgress(progress):
        progressBar.print_progress_bar(progress * 100)
    parser = RanobeParser(url, begin, end)
    parser.set_parsing_callback(setProgress)
    return parser.parse()


def create_ranobe(ranobe):
    progressBar = ProgressBar(total=100, prefix='Creating ',
                              length=50, fill='X', zfill='-')

    def setProgress(progress):
        progressBar.print_progress_bar(progress * 100)

    def setSavingProgress(progress):
        if progress == 0:
            print("\rSaving...", end="")
        else:
            print("\r         \r", end="")
    creator = RanobeEpubCreator(ranobe)
    creator.set_creating_callback(setProgress)
    creator.set_saving_callback(setSavingProgress)
    creator.create()


def sleep_pc():
    for i in range(-10, 0):
        print("\rSleep in " + ((str)(-i)) + " seconds ", end="")
        time.sleep(1)
    print("\r                                             \r", end="")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")


def get_urls():
    urls = []
    while True:
        print(Style.RESET_ALL, end="")
        print("Enter a link to the manga/ranobe: ", end="")
        url = input()
        if url == "" and len(urls) > 0:
            break
        elif url == "":
            continue
        if str.find(url, "https://") == -1:
            url = "https://" + url
        begin, end = get_chapters_range()
        if str.find(url, "mangalib") == -1:
            urls.append(("ranobe", url, begin, end, False, 0))
        else:
            fixedHeight = fix_height()
            sizeLimit = get_size_limit()
            urls.append(("manga", url, begin, end, fixedHeight, sizeLimit))

    return urls


def put_to_sleep():
    print("Let the pc sleep after completion (y/n): ", end="")
    return ask()


def get_chapters_range():
    print(
        "Enter a range of chapters (end-to-end numbering from 1): ", end="")
    cut = [int(s) for s in input().split() if s.isdigit()]
    begin = end = 0
    if len(cut) == 1:
        begin = cut[0]
    elif len(cut) > 1:
        begin = cut[0]
        end = cut[1]
    if begin > end and end > 0:
        temp = begin
        begin = end
        end = temp
    return begin, end


def fix_height():
    print("Fixed height (y/n): ", end="")
    return ask()


def get_size_limit():
    sizeLimit = 0
    while True:
        print(Style.RESET_ALL, end="")
        print("Enter the maximum PDF file size (MB): ", end="")
        try:
            size = input()
            if size == "":
                size = 0
            sizeLimit = abs((int)(size) * 1024 * 1024)
            break
        except:
            print(Fore.RED + "The size must be a number")
            continue
    return sizeLimit


def ask():
    answer = input()
    return answer == "y" or answer == "н"


if __name__ == "__main__":
    main()
