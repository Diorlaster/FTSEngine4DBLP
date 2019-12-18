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

    # TODO attualmente sto usando OKAPI BM25 e fornisco solo l'insieme di risultati nell'indice publications
    # TODO PROSSIMO STEP: valutare una trasformazione in classe, gestire query per le venues, separare in due whoosh query, cercare nei due indici e fornire i due insiemi di risultati

    def __init__(self, indexes, user_output_results):
        self.publications_index = indexes.publications_index
        self.venues_index = indexes.venues_index
        self.user_output_results = user_output_results

    def search(self):
        print(Back.BLUE + Fore.BLACK + " MENU > CERCA ")
        user_query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")

        user_splitted_query = self.get_queries(user_query)
        user_whoosh_query = self.get_whoosh_query(user_splitted_query);

        print(Fore.BLUE + '\n...la ricerca potrebbe richiedere un po\' di tempo...\n')
        start_time = time.time()
        # RICERCA INDICE PUBLICATIONS
        with self.publications_index.searcher() as publications_searcher:
            qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=self.publications_index.schema)
            user_whoosh_query = user_whoosh_query[:-3]
            print(">>>> " + user_whoosh_query)
            q = qp.parse(user_whoosh_query)
            results = publications_searcher.search(q, limit=None)
            # ciò che segue è necessario per il seguente motivo:
            # https://stackoverflow.com/questions/19477319/whoosh-accessing-search-page-result-items-throws-readerclosed-exception
            for result in results:
                result_to_store = {}
                for field in result.items():
                    result_to_store.update({field[0]:field[1]})
                result_to_store.update({'score':result.score})
                self.publications_results.append(result_to_store)

        # TODO applicare Threshold sulla lista delle pubs e quella delle venues
        self.print_results()

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
        user_whoosh_query = ""
        # per ogni query eseguirò lo stesso controllo per tradurre la query per Whoosh
        for query in user_splitted_query:
            query_element = "*", False
            query_field = "*", False
            query_text = "*"
            query_translated = False
            if ("." not in query and ":" not in query) or (query.startswith("\"") and query.endswith("\"")):
                print(Fore.CYAN + "--- WORD/PHRASE QUERY ---")
                query_text = query
            else:
                if ":" in query:
                    query_analysis = query.partition(":")
                    if "." in query_analysis[0]:
                        print(Fore.YELLOW + "--- ELEMENT SPECIFICO CON FIELD SPECIFICO ---")
                        query_element = self.get_element(str(query_analysis[0]).partition(".")[0])
                        query_field = self.get_field(str(query_analysis[0]).partition(".")[-1])
                        query_text = query_analysis[-1]
                    else:
                        print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
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
            user_whoosh_query = user_whoosh_query + "( "
            if query_element[1] and query_element[0] != "*":
                user_whoosh_query = user_whoosh_query + "pubtype:" + query_element[0] + " AND "
            if query_field[1] and query_field[0] != "*":
                user_whoosh_query = user_whoosh_query + query_field[0] + ":"
            user_whoosh_query = user_whoosh_query + query_text + " ) OR "

        return user_whoosh_query

    def get_element(self, query_analysis):
        for element in self.publications_elements:
            if query_analysis == element:
                print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                if element == "publication":
                    return "*", True
                return element, True
        print(Fore.CYAN + "--- ELEMENTO NON VALIDO---")
        return "*", False

    def get_field(self, query_analysis):
        for field in self.publications_fields:
            if query_analysis == field:
                print(Fore.CYAN + "--- FIELD SPECIFICO ---")
                return field, True
        print(Fore.CYAN + "--- FIELD NON VALIDO ---")
        return "*", False

    def print_results(self):
        # controllo se ci sono risultati altrimenti stampo "Nessun risultato trovato"
        if len(self.publications_results) > 0:
            print(Fore.BLUE + "Sono stati trovati " + Style.BRIGHT + Fore.BLACK + str(
                len(self.publications_results)) + Style.RESET_ALL + Fore.BLUE + " risultati!\n")
            # scorro i risultati, prendo i campi interessati e li stampo
            results_shown = 0
            for result in self.publications_results:
                if results_shown < self.user_output_results:
                    authors = result['author'].split('\n')
                    print(Back.MAGENTA + Style.BRIGHT + Fore.BLACK + "Risultato #" + str(results_shown + 1))
                    print(Style.BRIGHT + Fore.MAGENTA + "Score:\t" + Style.BRIGHT + Fore.BLACK + str(
                        result['score']) + "\n")
                    print(Style.BRIGHT + Fore.MAGENTA + "Authors")
                    for auth in authors:
                        print("\t" + Style.BRIGHT + Fore.BLACK + auth)
                    print(Style.BRIGHT + Fore.MAGENTA + "Title")
                    print("\t" + Style.BRIGHT + Fore.BLACK + result['title'])
                    print(Style.BRIGHT + Fore.MAGENTA + "Pub-Type")
                    print("\t" + Style.BRIGHT + Fore.BLACK + result['pubtype'] + "\n")
                    results_shown += 1
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato")

    # TODO scelte implementative in caso di elemento.NON_FIELD ed elemento:NON_FIELD
    # TODO scelte implementative in caso di elemento/field non trovato o sintassi errata
