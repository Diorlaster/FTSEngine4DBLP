import xml.sax
from colorama import Fore, Back, Style
from XML_Operations import Indexing

publications = ['article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
venues = ['book', 'proceedings']


class PublicationsHandler(xml.sax.ContentHandler):
    """Handle publications's parsing"""

    saxWriter = None
    isPublication = False

    current_field = None

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
        """Reset class attributes"""

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
        """File is being read by XML parser, searching for publications"""
        print(Fore.GREEN + "Indexing pubblications...", end="")

    def startElement(self, tag, attributes):
        """Publication has been found and is being parsed so we store its tag and its key"""

        self.current_field = tag
        for publicationTag in publications:
            if tag == publicationTag:
                self.isPublication = True
                self.tag = tag
                self.key = str(attributes['key'])

    def characters(self, content):
        """Check which field of publication is being read and then stored"""

        if self.isPublication:
            if self.current_field == "crossref":
                self.crossref += str(content).split('\n')[0]
            elif self.current_field == 'author':
                self.author += str(content)
            elif self.current_field == "title":
                self.title += str(content)
            elif self.current_field == "year":
                self.year += str(content)
            elif self.current_field == "journal":
                self.journal += str(content)
            elif self.current_field == "volume":
                self.volume += str(content)
            elif self.current_field == "pages":
                self.pages += str(content)
            elif self.current_field == "url":
                self.url += str(content)

    def endElement(self, tag):
        """Publication has been fully read so we can store it"""

        if self.tag == tag:
            """ if publication has a journal field its crossref is probably null so we set journal value as crossref.
            Journals is added to a list because it will become a new venue with journal field element as title """
            if self.journal != '' and self.crossref == '':
                if self.journal != '\n' and self.journal.split('\n')[0] not in Indexing.journals:
                    Indexing.journals.append(self.journal.split('\n')[0])
                self.saxWriter.add_document(pubtype=self.tag,
                                            key=self.key,
                                            crossref=self.journal.split('\n')[0],
                                            author=self.author,
                                            title=self.title,
                                            year=self.year,
                                            journal=self.journal,
                                            volume=self.volume,
                                            pages=self.pages,
                                            url=self.url
                                            )
            else:
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
        """File has been fully read"""
        print(Fore.GREEN + "OK!")


class VenuesHandler(xml.sax.ContentHandler):
    """Handle venues's parsing"""

    saxWriter = None
    isVenue = False

    current_field = None

    key = ''
    tag = ''
    author = ''
    title = ''
    year = ''
    journal = ''
    publisher = ''
    url = ''

    def __init__(self, sax_writer):
        self.saxWriter = sax_writer
        self.__reset_attributes()

    def __reset_attributes(self):
        """Reset class attributes"""

        self.isVenue = False
        self.key = ''
        self.tag = ''
        self.author = ''
        self.title = ''
        self.year = ''
        self.journal = ''
        self.publisher = ''
        self.url = ''

    def startDocument(self):
        """File is being read by XML parser, searching for venues"""
        print(Fore.GREEN + "Indexing venues...", end="")

    def startElement(self, tag, attributes):
        """Called when a venue is parsed"""

        self.current_field = tag
        for venueTag in venues:
            if tag == venueTag:
                self.isVenue = True
                self.tag = tag
                self.key = str(attributes['key'])

    def characters(self, content):
        """Check which field of venues is being read and then stored"""

        if self.isVenue:
            if self.current_field == "author":
                self.author += str(content)
            elif self.current_field == "title":
                self.title += str(content)
            elif self.current_field == "year":
                self.year += str(content)
            elif self.current_field == 'journal':
                self.journal += content
            elif self.current_field == "publisher":
                self.publisher += str(content)
            elif self.current_field == "url":
                self.url += str(content)

    def endElement(self, tag):
        """Venue has been fully read so we can store it"""

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
        """File has been fully read"""
        print(Fore.GREEN + "OK!")
