from colorama import Fore, Back, Style
from whoosh.qparser import QueryParser, MultifieldParser
import time

class Searcher:
    user_output_results = None;
    publications_elements = ['publication', 'article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
    publications_fields = ['author', 'title', 'year']
    publications_index = None
    publications_results = []
    venues_fields = ['title', 'publisher']
    venues_index = None
    venues_results = []

    # TODO attualmente sto usando OKAPI BM25 e stampo i risultati in modo separato senza combinare il ranking dei due insiemi
    # TODO PROSSIMO STEP: verificare traduzione

    def __init__(self, indexes, user_output_results):
        self.publications_index = indexes.publications_index
        self.venues_index = indexes.venues_index
        self.user_output_results = user_output_results
        self.publications_results = []
        self.venues_results = []

    def search(self):
        print(Back.BLUE + Fore.BLACK + " MENU > CERCA ")
        user_query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")

        user_splitted_query = self.get_queries(user_query)
        user_p_query, user_v_query = self.get_whoosh_query(user_splitted_query);
        print(">> P >> " + user_p_query)
        print(">> V >> " + user_v_query)

        print(Fore.BLUE + '\n...la ricerca potrebbe richiedere un po\' di tempo...\n')
        start_time = time.time()


        # RICERCA INDICE PUBLICATIONS
        with self.publications_index.searcher() as publications_searcher:
            qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=self.publications_index.schema)
            q = qp.parse(user_p_query)
            results = publications_searcher.search(q, limit=None)
            # ciò che segue è necessario per il seguente motivo:
            # https://stackoverflow.com/questions/19477319/whoosh-accessing-search-page-result-items-throws-readerclosed-exception
            for result in results:
                result_to_store = {}
                for field in result.items():
                    result_to_store.update({field[0]:field[1]})
                result_to_store.update({'score':result.score})
                self.publications_results.append(result_to_store)


        # RICERCA INDICE VENUES
        with self.venues_index.searcher() as venues_searcher:
            qp = MultifieldParser(['title', 'publisher'], schema=self.venues_index.schema)
            q = qp.parse(user_v_query)
            results = venues_searcher.search(q, limit=None)
            # ciò che segue è necessario per il seguente motivo:
            # https://stackoverflow.com/questions/19477319/whoosh-accessing-search-page-result-items-throws-readerclosed-exception
            for result in results:
                result_to_store = {}
                for field in result.items():
                    result_to_store.update({field[0]: field[1]})
                result_to_store.update({'score': result.score})
                self.venues_results.append(result_to_store)

        #TODO applicare Threshold sulla lista delle pubs e quella delle venues
        print(Back.YELLOW+Style.BRIGHT+Fore.BLACK+"\tRISULTATI PUBLICATIONS\t"+Style.RESET_ALL+"\n")
        self.print_results(self.publications_results)
        print(Back.YELLOW+Style.BRIGHT+Fore.BLACK+"\tRISULTATI VENUES\t"+Style.RESET_ALL+"\n")
        self.print_results(self.venues_results)

        end_time = time.time()
        print(Fore.BLUE + 'La ricerca è stata completata in', round((end_time - start_time)), Fore.BLUE + 'secondi!\n')

    def get_queries(self, user_query):
        # ad ogni posizione di user_splitted_query avrò una query. Tutte andranno messe in OR.
        query_start = 0
        phrase_count = 0
        user_splitted_query = []
        user_query = user_query + " "
        for c in range(0, len(user_query)):
            if user_query[c] == "\"":
                phrase_count = phrase_count + 1
                if phrase_count == 2:
                    user_splitted_query.append(user_query[query_start:c + 1])
                    query_start = c + 1
                    phrase_count = 0
            if user_query[c] == " " and phrase_count == 0:
                user_splitted_query.append(user_query[query_start:c])
                query_start = c + 1
        if phrase_count != 0 and phrase_count != 2:
            print(Fore.RED + "La query ha una formattazione errata. Per favore, riprova")

        print(user_splitted_query)

        # rimuovo gli elementi vuoti dalla lista e la ritorno
        return filter(None, user_splitted_query)

    def get_whoosh_query(self, user_splitted_query):
        publications_whoosh_query = ""
        venues_whoosh_query = ""

        # per ogni query eseguirò lo stesso controllo per tradurre la query per Whoosh
        for query in user_splitted_query:
            query_element = "*", False
            query_field = "*", False
            query_text = "*"
            if ("." not in query and ":" not in query) or (query.startswith("\"") and query.endswith("\"")):
                #print(Fore.CYAN + "--- WORD/PHRASE QUERY ---")
                query_text = query
            else:
                if ":" in query:
                    query_analysis = query.partition(":")
                    if "." in query_analysis[0]:
                        #print(Fore.YELLOW + "--- ELEMENT SPECIFICO CON FIELD SPECIFICO ---")
                        if str(query_analysis[0]).partition(".")[0].lower() == 'venue':
                            query_element = ('venue', True)
                        else:
                            query_element = self.get_element(str(query_analysis[0]).partition(".")[0])
                        query_field = self.get_field(str(query_analysis[0]).partition(".")[-1])
                        query_text = query_analysis[-1]
                    else:
                        #print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                        query_element = self.get_element(query_analysis[0])
                        if not query_element[1]:
                            # non ho trovato l'elemento.. potrebbe essere dunque un field .. controllo
                            query_field = self.get_field(query_analysis[0])
                        query_text = query_analysis[-1]
                elif "." in query:
                    query_analysis = query.partition(".")
                    query_element = self.get_element(query_analysis[0])
                    query_field = self.get_field(query_analysis[-1])
                    if not query_field[1]:
                        query_text = query_analysis[-1]

            if query_element[1] and query_element[0] != '*':
                if query_element[0] in self.publications_elements:
                    publications_whoosh_query = publications_whoosh_query + "( "
                    if query_element[0] != "*" and query_element[0] in self.publications_elements:
                        publications_whoosh_query = publications_whoosh_query + "pubtype:" + query_element[0] + " AND "
                    if query_field[1] and query_field[0] != "*" and query_field[0] in self.publications_fields:
                        publications_whoosh_query = publications_whoosh_query + query_field[0] + ":"
                    publications_whoosh_query = publications_whoosh_query + query_text + " ) OR "
                elif query_element[0] == 'venue':
                    venues_whoosh_query = venues_whoosh_query + "( "
                    if query_field[1] and query_field[0] != "*" and query_field[0] in self.venues_fields:
                        venues_whoosh_query = venues_whoosh_query + query_field[0] + ":"
                    venues_whoosh_query = venues_whoosh_query + query_text + " ) OR "
            else:
                #TODO NON FUNZIONA AL 99%
                if query_field[1] and query_field[0] != "*":
                    if query_field[0] in self.publications_fields:
                        publications_whoosh_query = publications_whoosh_query + "( " + query_field[0] + ":" + query_text + " ) OR "
                    if query_field[0] in self.venues_fields:
                        venues_whoosh_query = venues_whoosh_query + "( " + query_field[0] + ":" + query_text + " ) OR "
                else:
                    publications_whoosh_query = publications_whoosh_query + "( " + query_text + " ) OR "
                    venues_whoosh_query = venues_whoosh_query + "( " + query_text + " ) OR "

        return publications_whoosh_query[:-3], venues_whoosh_query[:-3]


    def get_element(self, query_analysis):
        if query_analysis in self.publications_elements:
            if query_analysis == "publication":
                return "*", True
            else:
                #print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                return query_analysis, True
        #print(Fore.CYAN + "--- ELEMENTO NON VALIDO---")
        return "*", False

    def get_field(self, query_analysis):
        if query_analysis in self.publications_fields or query_analysis in self.venues_fields:
            #print(Fore.CYAN + "--- FIELD SPECIFICO ---")
            return query_analysis, True
        #print(Fore.CYAN + "--- FIELD NON VALIDO ---")
        return "*", False

    def print_results(self, results_set):
        # controllo se ci sono risultati altrimenti stampo "Nessun risultato trovato"
        if len(results_set) > 0:
            print(Fore.BLUE + "Sono stati trovati " + Style.BRIGHT + Fore.BLACK + str(
                len(results_set)) + Style.RESET_ALL + Fore.BLUE + " risultati!\n")
            # scorro i risultati, prendo i campi interessati e li stampo
            results_shown = 0
            for result in results_set:
                if results_shown < self.user_output_results:
                    print(Back.MAGENTA + Style.BRIGHT + Fore.BLACK + "Risultato #" + str(results_shown + 1), end="\t")
                    print(Style.BRIGHT + Fore.MAGENTA + "Score:\t" + Style.BRIGHT + Fore.BLACK + str(
                        round(result['score'],3)) + "\n")

                    print(Style.BRIGHT + Fore.MAGENTA + "Authors")
                    if result['author']:
                        authors = result['author'].split('\n')
                        for author in authors:
                            print("\t" + Style.BRIGHT + Fore.BLACK + author)
                    else: print("\t" + Style.BRIGHT + Fore.BLACK + "N/D\n")
                    print(Style.BRIGHT + Fore.MAGENTA + "Title")
                    print("\t" + Style.BRIGHT + Fore.BLACK + result['title'])
                    print(Style.BRIGHT + Fore.MAGENTA + "Pub-Type")
                    print("\t" + Style.BRIGHT + Fore.BLACK + result['pubtype'] + "\n")
                    results_shown += 1
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato\n")

    # TODO scelte implementative in caso di elemento.NON_FIELD ed elemento:NON_FIELD
    # TODO scelte implementative in caso di elemento/field non trovato o sintassi errata
