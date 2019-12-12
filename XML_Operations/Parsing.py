import xml.sax
from colorama import Fore, Back, Style

publications = ['article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
venues = ['book', 'proceedings']


class PublicationsHandler(xml.sax.ContentHandler):
    """Class for handle parsing events and adding documents to the publication index"""

    saxWriter = None
    isPublication = False

    # per conservare l'elemento che si sta analizzando
    __onGoingElement = None

    # lista degli attributi di una publication che si è deciso di mostrare
    key = ''
    tag = ''
    crossref = ''
    author = ''
    title = ''
    year = ''
    journal = ''
    volume = ''
    pages = ''
    url = ''

    def __init__(self, sax_writer):
        self.saxWriter = sax_writer
        self.__reset_attributes()

    def __reset_attributes(self):
        """A function for resetting the class attributes"""

        self.isPublication = False
        self.key = ''
        self.tag = ''
        self.crossref = ''
        self.author = ''
        self.title = ''
        self.year = ''
        self.journal = ''
        self.volume = ''
        self.pages = ''
        self.url = ''

    def startDocument(self):
        """Called when the XML Parser starts reading the file"""
        print(Fore.GREEN + "Ho avviato l'indicizzazione delle publications...", end="")

    def startElement(self, tag, attributes):
        """Called when a publication is parsed"""

        self.__onGoingElement = tag
        for publicationTag in publications:
            if tag == publicationTag:
                self.isPublication = True
                self.tag = tag
                self.key = str(attributes['key'])

    def characters(self, content):
        """Called to assign the attributes of a publication document"""

        if self.isPublication:
            if self.__onGoingElement == "crossref":
                self.crossref += str(content)
            elif self.__onGoingElement == 'author':
                self.author += str(content)
            elif self.__onGoingElement == "title":
                self.title += str(content)
            elif self.__onGoingElement == "year":
                self.year += str(content)
            elif self.__onGoingElement == "journal":
                self.journal += str(content)
            elif self.__onGoingElement == "volume":
                self.volume += str(content)
            elif self.__onGoingElement == "pages":
                self.pages += str(content)
            elif self.__onGoingElement == "url":
                self.url += str(content)

    def endElement(self, tag):
        """Called when the parsing of the publication ends"""

        if self.tag == tag:
            self.saxWriter.add_document(pubtype=self.tag,
                                        key=self.key,
                                        crossref=self.crossref,
                                        author=self.author,
                                        title=self.title,
                                        year=self.year,
                                        journal=self.journal,
                                        volume=self.volume,
                                        pages=self.pages,
                                        url=self.url
                                        )
            self.__reset_attributes()

    def endDocument(self):
        """Called when the parsing is completed"""
        print(Fore.GREEN + "OK!")


class VenuesHandler(xml.sax.ContentHandler):
    """Class for handle parsing events and adding documents to the venue index"""

    saxWriter = None
    isVenue = False

    # per conservare l'elemento che si sta analizzando
    __onGoingElement = None

    # lista degli attributi di una venue che si è deciso di mostrare
    key = ''
    tag = ''
    author = ''
    title = ''
    year = ''
    journal = ''
    publisher = ''
    url = ''
    parent = False

    def __init__(self, sax_writer):
        self.saxWriter = sax_writer
        self.__reset_attributes()

    def __reset_attributes(self):
        """A function for resetting the class attributes."""

        self.isVenue = False
        self.key = ''
        self.tag = ''
        self.author = ''
        self.title = ''
        self.year = ''
        self.journal = ''
        self.publisher = ''
        self.url = ''
        self.parent = False

    def startDocument(self):
        """Called when the XML Parser starts reading the file"""
        print(Fore.GREEN + "Ho avviato l'indicizzazione delle venues...", end="")

    def startElement(self, tag, attributes):
        """Called when a venue is parsed"""

        self.__onGoingElement = tag
        for venueTag in venues:
            if tag == venueTag:
                self.isVenue = True
                self.tag = tag
                self.key = str(attributes['key'])

    def characters(self, content):
        """Called to assign the attributes of a venue document"""

        if self.isVenue:
            if self.__onGoingElement == "author":
                self.author += str(content)
            elif self.__onGoingElement == "title":
                self.title += str(content)
            elif self.__onGoingElement == "year":
                self.year += str(content)
            elif self.__onGoingElement == 'journal':
                self.journal += content
            elif self.__onGoingElement == "publisher":
                self.publisher += str(content)
            elif self.__onGoingElement == "url":
                self.url += str(content)

    def endElement(self, tag):
        """Called when the parsing of the venue ends"""

        if self.tag == tag:
            self.saxWriter.add_document(pubtype=self.tag,
                                        key=self.key,
                                        author=self.author,
                                        title=self.title,
                                        year=self.year,
                                        journal=self.journal,
                                        publisher=self.publisher,
                                        url=self.url
                                        )
            self.__reset_attributes()

    def endDocument(self):
        """Called when the parsing is completed"""
        print(Fore.GREEN + "OK!")
