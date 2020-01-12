from colorama import Fore, Back, Style
from whoosh.qparser import MultifieldParser
import time

from whoosh.scoring import Frequency, BM25F  # NON CANCELLARE, VENGONO USATI VIA EVAL()

class Searcher:
    user_output_results = None;
    publications_elements = ['publication', 'article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
    publications_fields = ['author', 'title', 'year']
    publications_index = None
    publications_results = []
    venues_fields = ['title', 'publisher']
    venues_index = None
    venues_results = []
    user_warnings = None
    user_score = None
    query_warnings = {}
    ranking = None

    def __init__(self, indexes, user_output_results, user_warnings, user_score, ranking):
        self.publications_index = indexes.publications_index
        self.venues_index = indexes.venues_index
        self.user_output_results = user_output_results
        self.publications_results = []
        self.venues_results = []
        self.user_warnings = user_warnings
        self.user_score = user_score
        self.query_warnings = {}
        self.ranking = ranking

    def search(self):
        print(Back.BLUE + Fore.BLACK + " MENU > CERCA ")
        user_query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")

        user_splitted_query, user_continue = self.get_queries(user_query)

        if not user_continue:
            return

        user_p_query, user_v_query = self.get_whoosh_query(user_splitted_query);
        print("\n>> P >> " + user_p_query + "\n")
        print("\n>> V >> " + user_v_query + "\n")

        if self.user_warnings:
            if self.query_warnings:
                print(Back.CYAN + Fore.BLACK + "\tWARNINGS\t")
                for query, warnings in self.query_warnings.items():
                    for warning in warnings:
                        print(Fore.CYAN + "in " + Fore.YELLOW + query + Fore.CYAN + " | " + warning)

        print(Fore.BLUE + '\n...la ricerca potrebbe richiedere un po\' di tempo...\n')
        start_time = time.time()

        # RICERCA INDICE PUBLICATIONS
        with self.publications_index.searcher(weighting=eval(self.ranking)) as publications_searcher:
            qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=self.publications_index.schema)
            q = qp.parse(user_p_query)
            results = publications_searcher.search(q, limit=None)
            # ciò che segue è necessario per il seguente motivo:
            # https://stackoverflow.com/questions/19477319/whoosh-accessing-search-page-result-items-throws-readerclosed-exception
            for result in results:
                result_to_store = {}
                for field in result.items():
                    result_to_store.update({field[0]: field[1]})
                result_to_store.update({'score': result.score})
                self.publications_results.append(result_to_store)

        # RICERCA INDICE VENUES
        with self.venues_index.searcher(weighting=eval(self.ranking)) as venues_searcher:
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

        #print(Back.YELLOW + Style.BRIGHT + Fore.BLACK + "\tRISULTATI PUBLICATIONS\t" + Style.RESET_ALL + "\n")
        #self.print_results(self.publications_results)
        #print(Back.YELLOW + Style.BRIGHT + Fore.BLACK + "\tRISULTATI VENUES\t" + Style.RESET_ALL + "\n")
        #self.print_results(self.venues_results)

        if len(self.publications_results) > 0 and len(self.venues_results) > 0:
            lista = self.threshold(self.publications_results, self.venues_results)
            self.print_ts(lista)
        elif len(self.publications_results) <= 0 and len(self.venues_results) > 0:
            self.print_results(self.venues_results)
        elif len(self.publications_results) > 0 and len(self.venues_results) <= 0:
            self.print_results(self.publications_results)
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato\n")

        end_time = time.time()
        print(Fore.BLUE + 'La ricerca è stata completata in', round((end_time - start_time)), Fore.BLUE + 'secondi!\n')

        #self.print_results(lista)

    def get_queries(self, user_query):
        # ad ogni posizione di user_splitted_query avrò una query. Tutte andranno messe in OR.
        query_start = 0
        phrase_count = 0
        user_splitted_query = []
        user_query = user_query + " "
        alert = False
        for c in range(0, len(user_query)):
            if user_query[c] == "\"":
                phrase_count = phrase_count + 1
                # TODO specificare nelle FAQ che dopo una phrase individuata, la parola successiva viene automaticamente staccare e assegnata ad una nuova query
                if phrase_count == 2:
                    user_splitted_query.append(user_query[query_start:c + 1])
                    query_start = c + 1
                    phrase_count = 0
            if user_query[c] == " " and phrase_count == 0:
                user_splitted_query.append(user_query[query_start:c])
                query_start = c + 1
        if phrase_count != 0 and phrase_count != 2:
            print(
                Fore.RED + "\nSono state rilevate delle anomalie nel formato della query che potrebbero portare a mostrarti ciò che non stai cercando."
                           "\nEcco come ho interpretato la tue richieste:\n")
            for query in filter(None, user_splitted_query):
                print("\t" + query)
            while True:
                user_continue = input(Fore.YELLOW + "\nContinuare? [S/N] >>> ")
                if user_continue.upper() == 'S':
                    print()
                    return filter(None, user_splitted_query), True
                elif user_continue.upper() == 'N':
                    print()
                    return "STOP", False
                else:
                    print(Fore.LIGHTRED_EX + "Selezionare un'opzione valida", end="")

        print("\n" + str(user_splitted_query) + "\n")

        # rimuovo gli elementi vuoti dalla lista e la ritorno
        return filter(None, user_splitted_query), True

    def get_whoosh_query(self, user_splitted_query):
        publications_whoosh_query = ""
        venues_whoosh_query = ""

        # per ogni query eseguirò lo stesso controllo per tradurre la query per Whoosh
        for query in user_splitted_query:
            query_element = "*", False
            query_field = "*", False
            query_text = "*"
            warnings = []

            if ("." not in query and ":" not in query) or (query.startswith("\"") and query.endswith("\"")):
                # print(Fore.CYAN + "--- WORD/PHRASE QUERY ---")
                query_text = query
            else:
                if ":" in query:
                    query_analysis = query.partition(":")
                    if "." in query_analysis[0]:
                        # print(Fore.YELLOW + "--- ELEMENT SPECIFICO CON FIELD SPECIFICO ---")
                        if str(query_analysis[0]).partition(".")[0].lower() == 'venue':
                            query_element = ('venue', True)
                        else:
                            query_element = self.get_element(str(query_analysis[0]).partition(".")[0])
                        query_field = self.get_field(str(query_analysis[0]).partition(".")[-1])
                        query_text = query_analysis[-1]
                    else:
                        # print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                        if str(query_analysis[0]).lower() == 'venue':
                            query_element = ('venue', True)
                        else:
                            query_element = self.get_element(query_analysis[0])
                            # if not query_element[1]:
                            # non ho trovato l'elemento.. potrebbe essere dunque un field .. controllo
                        query_field = self.get_field(query_analysis[0])
                        query_text = query_analysis[-1]
                elif "." in query:
                    query_analysis = query.partition(".")
                    if str(query_analysis[0]).lower() == 'venue':
                        query_element = ('venue', True)
                    else:
                        query_element = self.get_element(query_analysis[0])
                    query_field = self.get_field(query_analysis[-1])
                    if not query_field[1]:
                        query_text = query_analysis[-1]

            if not query_element[1] and query_element[0] != '*':
                warnings.append(Fore.YELLOW + str(query_element[0]) + Fore.CYAN + " non è un elemento valido."
                                                                                  " Il resto della query verrà pertanto cercato in tutti gli elementi. ")
            if query_element[1] and query_element[0] != '*':
                if query_element[0] in self.publications_elements:
                    publications_whoosh_query = publications_whoosh_query + "( "
                    if query_element[0] != "*" and query_element[0] in self.publications_elements:
                        publications_whoosh_query = publications_whoosh_query + "pubtype:" + query_element[0] + " AND "
                    if query_field[0] != "*":
                        if query_field[0] in self.publications_fields:
                            if query_field[1]:
                                publications_whoosh_query = publications_whoosh_query + query_field[0] + ":"
                        else:
                            warnings.append(
                                Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " non è un campo valido o ammesso."
                                                                                " Verrà pertanto ignorato, cercando " + Fore.YELLOW + query_text + Fore.CYAN + " in " + Fore.YELLOW +
                                query_element[0])
                    publications_whoosh_query = publications_whoosh_query + query_text + " ) OR "
                elif query_element[0] == 'venue':
                    venues_whoosh_query = venues_whoosh_query + "( "
                    if query_field[0] != "*":
                        if query_field[0] in self.venues_fields:
                            if query_field[1]:
                                venues_whoosh_query = venues_whoosh_query + query_field[0] + ":"
                        else:
                            warnings.append(
                                Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " non è un campo valido o ammesso."
                                                                                " Verrà pertanto ignorato, cercando " + Fore.YELLOW + query_text + Fore.CYAN + " in tutte le " + Fore.YELLOW + "venues")
                    venues_whoosh_query = venues_whoosh_query + query_text + " ) OR "
            else:
                if query_field[0] not in self.publications_fields and query_field[0] not in self.venues_fields and \
                        query_field[0] != '*':
                    warnings.append(Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " non è un campo valido o ammesso. "
                                                                                    "Verrà pertanto ignorato, cercando " + Fore.YELLOW + query_text + Fore.CYAN + " tra tutti gli elementi.")
                if query_field[1] and query_field[0] != "*":
                    if query_field[0] in self.publications_fields:
                        publications_whoosh_query = publications_whoosh_query + "( " + query_field[
                            0] + ":" + query_text + " ) OR "
                    if not query_element[1] and query_field[0] in self.venues_fields:
                        venues_whoosh_query = venues_whoosh_query + "( " + query_field[0] + ":" + query_text + " ) OR "
                else:
                    publications_whoosh_query = publications_whoosh_query + "( " + query_text + " ) OR "
                    if not query_element[1]:
                        venues_whoosh_query = venues_whoosh_query + "( " + query_text + " ) OR "

            if warnings:
                self.query_warnings.update({query: warnings})

        return publications_whoosh_query[:-3], venues_whoosh_query[:-3]

    def get_element(self, query_analysis):
        if query_analysis in self.publications_elements:
            if query_analysis == "publication":
                return "*", True
            else:
                # print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                return query_analysis, True
        elif query_analysis in self.publications_fields or query_analysis in self.venues_fields:
            return "*", False
        # print(Fore.CYAN + "--- ELEMENTO NON VALIDO---")
        else:
            return query_analysis, False

    def get_field(self, query_analysis):
        if query_analysis in self.publications_fields or query_analysis in self.venues_fields:
            # print(Fore.CYAN + "--- FIELD SPECIFICO ---")
            return query_analysis, True
        # print(Fore.CYAN + "--- FIELD NON VALIDO ---")
        return query_analysis, False

    def print_results(self, results_set):
        # controllo se ci sono risultati altrimenti stampo "Nessun risultato trovato"
        if len(results_set) > 0:
            print(Fore.BLUE + "Sono stati trovati " + Style.BRIGHT + Fore.BLACK + str(
                len(results_set)) + Style.RESET_ALL + Fore.BLUE + " risultati!\n")
            # scorro i risultati, prendo i campi interessati e li stampo
            results_shown = 0
            for result in results_set:
                if results_shown < self.user_output_results:
                    print(Back.MAGENTA + Style.BRIGHT + Fore.BLACK + "\tRisultato #" + str(results_shown + 1)+"\t", end="\t")
                    if self.user_score:
                        print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Score:\t" + Style.BRIGHT + Fore.BLACK + str(
                            round(result['score'], 3)), end="")
                    print(Style.BRIGHT + Fore.BLACK + "\n\n\tTitle: " + Style.RESET_ALL + result['title'],end="")
                    print(Style.BRIGHT + Fore.BLACK + "\tAuthors: ", end="")
                    if result['author']:
                        authors = result["author"].split("\n")
                        print(*(author for author in authors if author != ""), sep=", ", end="\n")
                    else:
                        print("N/D\n")
                    print(Style.BRIGHT + Fore.BLACK + "\tYear: " + Style.RESET_ALL + result['year'],end="")
                    print(Style.BRIGHT + Fore.BLACK + "\tPub-Type: " + Style.RESET_ALL + result['pubtype'] + "\n")
                    results_shown += 1
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato\n")

    def threshold(self, pubs, venues):
        soglia = 0
        score_p = 0
        score_v = 0
        i = 0

        lista = []

        print(">>>>>> "+str(len(pubs)))
        print(">>>>>> "+str(len(venues)))
        while True:

            if i >= len(pubs) or i >= len(venues):
                break

            pub_to_ven = {}
            ven_to_pub = {}
            score_v = venues[i]["score"]
            score_p = pubs[i]["score"]
            soglia = score_p + score_v

            v_trovato = False
            #cerco se la crossref è nelle venues
            for ven in venues:
                if "crossref" in pubs[i] and pubs[i]["crossref"] != "" and pubs[i]["crossref"][:-1] == ven["key"]:
                    # ho trovato una corrispondenza. Prendo lo score della venue, lo sommo allo score della pub i-esima
                    pub_to_ven.update({ "p":pubs[i] ,  "v":ven ,  "score_comb":pubs[i]["score"]+ven["score"]} )
                    v_trovato = True
                    break
            if not v_trovato:
                pub_to_ven.update({ "p": pubs[i], "v": None, "score_comb":pubs[i]["score"]  })

            lista.append(pub_to_ven)

            p_trovato = False
            # cerco se la crossref è nelle pubs
            for pub in pubs:
                if "crossref" in pub and pub["crossref"] != "" and venues[i]["key"] == pub["crossref"][:-1]:
                    # ho trovato una corrispondenza. Prendo lo score della pub, lo sommo allo score della venue i-esima
                    ven_to_pub.update({ "p":pub , "v":venues[i], "score_comb":pub["score"]+venues[i]["score"]})
                    p_trovato = True
                    break
            if not p_trovato:
                ven_to_pub.update( { "p":None , "v": venues[i], "score_comb":venues[i]["score"] })

            # ho messo le due righe nella tabella

            lista.append(ven_to_pub)

            lista = sorted(lista, key = lambda i: i['score_comb'], reverse=True)

            if lista[0]['score_comb'] > soglia:
                break
            else:
                i = i+1

        print(">>>>> FERMO DOPO "+str(i+1)+" ITERAZIONI.")
        return lista

    def print_ts(self, lista):

        if not lista:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato\n")
            return

        # rimozione duplicati
        lista = [i for n, i in enumerate(lista) if i not in lista[n + 1:]]

        if len(lista) < self.user_output_results:
            self.user_output_results = len(lista)

        """
        if len(lista) > self.user_output_results:
            lista = lista[:self.user_output_results] 
        """

        print()
        i=0
        while i < self.user_output_results and len(lista) > 0:
            venue_i = lista[0]["v"]
            pub_i = lista[0]["p"]
            if venue_i != None:
                punti = venue_i["score"]
                for j in range(len(lista)):
                    pub_j = lista[j]["p"]
                    if pub_j != None and "crossref" in pub_j and pub_j["crossref"][:-1] == venue_i["key"]:
                        punti = punti + pub_j["score"]
                print(Back.MAGENTA + Fore.BLACK + "\tRisultato #" + str(i+1) + "\t", end="\t")
                if self.user_score:
                    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                        round(punti, 3)), end="")
                print(Style.BRIGHT + Fore.MAGENTA + "\n\n\tVENUE")
                print("\t\t" + Style.BRIGHT + Fore.BLACK + "Title: " + Fore.RESET + str(venue_i["title"][:-1]))
                print("\t\t" + Style.BRIGHT + Fore.BLACK + "Key: " + Fore.RESET + str(venue_i["key"]) + "\n")
                for j in range(len(lista)):
                    pub_j = lista[j]["p"]
                    if pub_j != None and "crossref" in pub_j and pub_j["crossref"][:-1] == venue_i["key"]:
                        punti = punti + pub_j["score"]
                        print(Style.BRIGHT+ Fore.MAGENTA + "\tPUBLICATION #"+str(j+1))
                        print( Style.BRIGHT + Fore.BLACK +"\t\tTitle: " + Style.RESET_ALL + str(pub_j["title"][:-1]))
                        print("\t\t" + Style.BRIGHT + Fore.BLACK + "Crossref: " + Fore.RESET + str(
                            pub_j["crossref"][:-1]))
                        print( Style.BRIGHT + Fore.BLACK +"\t\tAuthors: ", end="")
                        authors = pub_j["author"].split("\n")
                        print(*(author for author in authors if author != ""), sep=", ")
                        print(Style.BRIGHT + Fore.BLACK + "\t\tYear: " + Style.RESET_ALL + pub_j['year'], end="")
                        print(Style.BRIGHT + Fore.BLACK + "\t\tPub-Type: " + Style.RESET_ALL + pub_j['pubtype'])
                        print()
                lista[:] = [d for d in lista if d.get('v') != venue_i]
            elif pub_i != None:
                print(Back.MAGENTA + Fore.BLACK + "\tRisultato #" + str(i + 1) + "\t", end="\t")
                if self.user_score:
                    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                        round(pub_i["score"], 3)), end="")
                print(Style.BRIGHT + Fore.MAGENTA + "\n\n\tPUBLICATION")
                print(Style.BRIGHT + Fore.BLACK + "\t\tTitle: " + Style.RESET_ALL + str(pub_i["title"][:-1]))
                print("\t\t" + Style.BRIGHT + Fore.BLACK + "Crossref: " + Fore.RESET + str(
                    pub_i["crossref"][:-1]))
                print(Style.BRIGHT + Fore.BLACK + "\t\tAuthors: ", end="")
                authors = pub_i["author"].split("\n")
                print(*(author for author in authors if author != ""), sep=", ")
                print(Style.BRIGHT + Fore.BLACK + "\t\tYear: " + Style.RESET_ALL + pub_i['year'], end="")
                print(Style.BRIGHT + Fore.BLACK + "\t\tPub-Type: " + Style.RESET_ALL + pub_i['pubtype'])
                print()
                lista[:] = [d for d in lista if d.get('p') != pub_i]

            i = i + 1

# TODO: testare i warning e sistemare quello relativo alle venue ( test con la query di sotto )

# inproceedings.title:"Database Systems 2.0" inproceedings.title:"Structured Data Meets News" venue.title:"Proceedings of the VLDB 2019 PhD Workshop" venue:VLDB