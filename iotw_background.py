#For fetching iotw
from pathlib import Path
from html.parser import HTMLParser
import urllib.request

#For changing wallpaper
import ctypes
import os
import platform

BACKGROUND_FILE = Path("iotw.jpg")

def get_perseverance_iotw(outputFilepath: Path) -> None :
    """Fetch current perseverance image of the week and save to file indicated

    Keyword Arguments :
        outputFilepath: A Path object to the output file
    """

    parser = find_iotw(outputFilepath)
    with urllib.request.urlopen("https://mars.nasa.gov/mars2020/multimedia/raw-images/image-of-the-week/") as response :
        page = str(response.read())
    try :
        parser.feed(page)
    except find_iotw.FoundIOTW :
        #Successfully parsed page
        pass


def set_background(wallpaper_filepath: Path) -> None :
    """Sets desktop background to supplied file, windows only

    Keyword Arguments:
        wallpaper_filepath: A Path to the image to set as wallpaper
    """

    #Detecting os, using if else so it works on older python versions
    os_name = platform.system()
    if os_name == "Windows" :
        #Windows
        ctypes.windll.user32.SystemParametersInfoW(20, 0, str(wallpaper_filepath.absolute()), 0)
    elif os_name == "Linux" :
        #May not work on all linux setups, currently only tested on Ubuntu 20.04.3 LTS
        os.system("/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + str(wallpaper_filepath.absolute()))
    else :
        print("Unfortunately this tool does not work on your operating system, it is currently tested on Windows 10 and Ubuntu 20.04.03 LTS")


class find_iotw(HTMLParser) :
    """Parses HTML to find URL to current image of the week, raises FoundIOTW if successful

    Keyword Arguments:
        outputFilepath: a Path to the file where the image of the week should be stored
    """

    inside_iotw = False


    class FoundIOTW(Exception) :
        """Dummy exception used to finish successfully, makes HTML parser more efficient as it doesn't continue to parse HTML after image of the week is found"""
        pass


    def __init__(self, outputFilepath: Path, convert_charrefs: bool = ...) -> None:
        """Initialisation function"""

        self.outputFilepath = outputFilepath
        super().__init__(convert_charrefs=convert_charrefs)
        

    def handle_starttag(self, tag: str, attrs: "list[tuple[str, str]]") -> None:
        """Function for handling found html tags"""

        for attribute, value in attrs :
            #The image of the week is enveloped by 2 div tags, outer has class main_iotw, used to differentiate current iotw from other images in page
            if attribute == "class" and value == "main_iotw" :
                #triggering flag to note inside div tag for iotw
                self.inside_iotw = True
            #If inside iotw div and on an image tag and the current attribute is the source of the image
            if self.inside_iotw and tag == "img" and attribute == "src" :
                #Download iotw
                with urllib.request.urlopen(value) as response :
                    with open(self.outputFilepath, "wb") as output :
                        output.write(response.read())
                #Leave function by raising error
                raise self.FoundIOTW
            
        return super().handle_starttag(tag, attrs)


if __name__ == "__main__" :
    #Fetching current iotw
    get_perseverance_iotw(BACKGROUND_FILE)
    #Setting wallpaper
    set_background(BACKGROUND_FILE)
