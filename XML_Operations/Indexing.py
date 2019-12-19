import os
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


class Index:
    indexes_path = 'Indexes/'
    publications_index_path = 'Indexes/PublicationsIndex'
    venues_index_path = 'Indexes/VenuesIndex'
    xml_path = None
    publications_index = None
    venues_index = None

    def load_check_indexes(self):
        try:
            self.publications_index = index.open_dir(self.publications_index_path)
            self.venues_index = index.open_dir(self.venues_index_path)
            publications_number = str(self.publications_index.doc_count())
            venues_number = str(self.venues_index.doc_count())
            print(Style.BRIGHT+Fore.BLUE + "Indici caricati! Sono state trovate: ")
            print(Fore.BLUE+"> "+Fore.WHITE + publications_number + Fore.BLUE + " publications")
            print(Fore.BLUE+"> "+Fore.WHITE + venues_number + Fore.BLUE + " venues")
            print()
        except:
            print(Fore.RED + "Non sono riuscito a caricare gli indici... ")
            xml_path = input(
                Fore.YELLOW + "...per favore, indica il percorso del file XML ed il file stesso per crearli: ")
            self.xml_path = abspath(xml_path)

            start_time = time.time()

            sax_parser = xml.sax.make_parser();
            sax_parser.setFeature(xml.sax.handler.feature_namespaces, 0)

            if os.path.exists(self.indexes_path):
                rmtree(self.indexes_path)

            os.makedirs(self.indexes_path)
            os.makedirs(self.publications_index_path)
            os.makedirs(self.venues_index_path)

            self.xml_indexing(sax_parser,PublicationsHandler,self.get_publications_schema(),self.publications_index_path)
            self.xml_indexing(sax_parser,VenuesHandler,self.get_venues_schema(),self.venues_index_path)

            end_time = time.time()
            print(Fore.BLUE + 'La creazione è stata completata in ', round((end_time - start_time) / 60), Fore.BLUE + ' minuti!')

            self.load_check_indexes()


    def xml_indexing(self, parser, handler, schema, path):
        pe_number = round(cpu_count())
        memory_percetage = 90 / 100
        available_memory = virtual_memory().available / 1024 ** 2
        mb_limit = round(available_memory / pe_number * memory_percetage)

        d = {'pe_number': pe_number, 'mb_limit': mb_limit, 'multisegment': True}

        writer = create_in(path, schema).writer(**d)
        parser.setContentHandler(handler(writer))

        parser.parse(self.xml_path)
        print(Fore.GREEN + "Ho avviato il commit...", end="")
        writer.commit()
        print(Fore.GREEN + "OK!")

    def get_publications_schema(self):
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