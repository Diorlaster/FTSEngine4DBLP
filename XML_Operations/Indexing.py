import os
import sys
import xml
import time
from os.path import abspath
from shutil import rmtree

from whoosh import index

from .Parsing import PublicationsHandler, VenuesHandler
from psutil import cpu_count, virtual_memory
from colorama import Fore, Back, Style
from whoosh.fields import Schema, STORED, TEXT
from whoosh.index import create_in

journals = []

class Index:
    """Indexes support class. Here We check, load and create indexes"""

    indexes_path = 'Indexes/'
    publications_index_path = 'Indexes/PublicationsIndex'
    venues_index_path = 'Indexes/VenuesIndex'
    xml_path = None
    publications_index = None
    venues_index = None
    sentinel = False

    def load_check_indexes(self):
        """Check if indexes exists and load them. If not, launch parsing and indexing process"""

        try:
            """Try to load indexes... """
            self.publications_index = index.open_dir(self.publications_index_path)
            self.venues_index = index.open_dir(self.venues_index_path)
            publications_number = str(self.publications_index.doc_count())
            venues_number = str(self.venues_index.doc_count())
            print(Style.BRIGHT+Fore.BLUE + "Indexes successfully loaded! Elements found: ")
            print(Fore.BLUE+"> "+Fore.WHITE + publications_number + Fore.BLUE + " publications")
            print(Fore.BLUE+"> "+Fore.WHITE + venues_number + Fore.BLUE + " venues")
            print()
        except:
            """... but if indexes cannot be loaded, ask for XML file path and create them"""
            if not self.sentinel:
                print(Fore.RED + "Indexes not found... ")
                self.sentinel = True

            while True:
                xml_path = input(
                    Fore.YELLOW + "Invalid path...please, insert a valid path for the XML file: ")
                self.xml_path = abspath(xml_path)
                if os.path.exists(self.xml_path) and xml_path.endswith(".xml"):
                    break

            start_time = time.time()

            sax_parser = xml.sax.make_parser();
            sax_parser.setFeature(xml.sax.handler.feature_namespaces, 0)

            if os.path.exists(self.indexes_path):
                rmtree(self.indexes_path)

            os.makedirs(self.indexes_path)
            os.makedirs(self.publications_index_path)
            os.makedirs(self.venues_index_path)

            try:
                self.xml_indexing(sax_parser,PublicationsHandler,self.get_publications_schema(),self.publications_index_path, False)
                self.xml_indexing(sax_parser, VenuesHandler, self.get_venues_schema(), self.venues_index_path, True)
                end_time = time.time()
                print(Fore.BLUE + 'Indexes creation completed in ', round((end_time - start_time) / 60),
                      Fore.BLUE + ' minutes!')
            except:
                """Interrupting indexing process can create damaged indexes and unpredictable behavior so we prefer to 
                kill the program and start all over again, deleting damaged indexes's directory"""
                print( Fore.RED + "Something went wrong during the indexing process... FTSE4DBLP will shut down to prevent damaged indexes")
                sys.exit(0)

            self.load_check_indexes()


    def xml_indexing(self, parser, handler, schema, path, journal ):
        """Indexes support class. Here We check, load and create indexes"""

        """Set resources in order to minimize the time required by parsing and indexing process"""
        pe_number = round(cpu_count())
        memory_percetage = 90 / 100
        available_memory = virtual_memory().available / 1024 ** 2
        mb_limit = round(available_memory / pe_number * memory_percetage)
        d = {'pe_number': pe_number, 'mb_limit': mb_limit, 'multisegment': True}

        writer = create_in(path, schema).writer(**d)
        parser.setContentHandler(handler(writer))

        """Create journals's venues from the ones found during the parsing process"""
        parser.parse(self.xml_path)
        if journal:
            for j in journals:
                writer.add_document(pubtype="journal",
                                    key=j,
                                    author="",
                                    title=j,
                                    year="",
                                    publisher="",
                                    url=""
                                    )

        print(Fore.GREEN + "Committing...", end="")
        writer.commit()
        print(Fore.GREEN + "OK!")


    def get_publications_schema(self):
        """publications indexing schema"""

        publications_schema = Schema(
            pubtype=TEXT(stored=True),
            key=STORED,
            author=TEXT(stored=True, phrase=True),
            title=TEXT(stored=True, phrase=True),
            pages=STORED,
            year=TEXT(stored=True),
            journal=STORED,
            volume=STORED,
            url=STORED,
            crossref=STORED
        )
        return publications_schema

    def get_venues_schema(self):
        """venues indexing schema"""

        venues_schema = Schema(
            pubtype=STORED,
            key=STORED,
            author=STORED,
            title=TEXT(stored=True),
            journal=STORED,
            publisher=TEXT(stored=True),
            url=STORED,
            year=STORED,
        )
        return venues_schema