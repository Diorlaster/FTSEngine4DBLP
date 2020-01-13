from colorama import Fore, Back, Style
from whoosh.qparser import MultifieldParser
from XML_Operations import Parsing
from whoosh.scoring import Frequency, BM25F
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
        if ranking == "BM25F":
            self.ranking = BM25F
        elif ranking == "Frequency":
            self.ranking = Frequency

    def search(self):
        print(Back.BLUE + Fore.BLACK + " MAIN MENU > SEARCH ")
        user_query = input(Fore.YELLOW + "\n\tWhat are you looking for? >>> ")
        print()

        user_splitted_query, user_continue = self.get_queries(user_query)

        if not user_continue:
            return

        user_p_query, user_v_query = self.get_whoosh_queries(user_splitted_query);
        #print("\n>> P >> " + user_p_query + "\n")
        #print("\n>> V >> " + user_v_query + "\n")

        if self.user_warnings:
            if self.query_warnings:
                print("\t"+Back.CYAN + Fore.BLACK + "\tWARNINGS\t"+Style.RESET_ALL+"\n")
                for query, warnings in self.query_warnings.items():
                    for warning in warnings:
                        print(Fore.CYAN + "\t\tin " + Fore.YELLOW + query + Fore.CYAN + " | " + warning)
                print("\n")

        print(Fore.BLUE + '\t...your request may require some time...\n')
        start_time = time.time()

        # RICERCA INDICE PUBLICATIONS
        with self.publications_index.searcher(weighting=self.ranking) as publications_searcher:
            try:
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
            except:
                print(
                    Fore.CYAN + "Due to anomalies in the query format that FTSE4DBLP was unable to handle,"+ Fore.YELLOW + " publications " + Fore.CYAN + "results could be not 100% accurate. "
                               "\nPlease, use a correct query format ( more infos can be found in FAQ section )\n")

        # RICERCA INDICE VENUES
        with self.venues_index.searcher(weighting=self.ranking) as venues_searcher:
            try:
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
            except:
                print(
                    Fore.CYAN + "Due to anomalies in the query format that FTSE4DBLP was unable to handle,"+ Fore.YELLOW + " venues " + Fore.CYAN + "results could be not 100% accurate. "
                               "\nPlease, use a correct query format ( more infos can be found in FAQ section )\n")

        if len(self.publications_results) > 0 and len(self.venues_results) > 0:
            threshold_results = self.threshold_algorithm(self.publications_results, self.venues_results)
            print( "\t" + Style.BRIGHT + Fore.BLACK + str(len(self.publications_results)+len(self.venues_results))
                   + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ", end="")
            self.print_threshold_results(threshold_results)
        elif len(self.publications_results) <= 0 and len(self.venues_results) > 0:
            print("\t" + Style.BRIGHT + Fore.BLACK + str(len(self.venues_results))
                  + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ",
                  end="")
        elif len(self.publications_results) > 0 and len(self.venues_results) <= 0:
            print("\t" + Style.BRIGHT + Fore.BLACK + str(len(self.publications_results))
                    + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ",
                  end="")
            self.print_results(self.publications_results)
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")

        end_time = time.time()

        print("\n\t" + Fore.BLUE + 'Request completed in ', round((end_time - start_time),1), Fore.BLUE + 'seconds!\n')

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
                # TODO specificare nelle FAQ che dopo una phrase individuata, la parola successiva viene automaticamente staccata e assegnata ad una nuova query
                if phrase_count == 2:
                    user_splitted_query.append(user_query[query_start:c + 1])
                    query_start = c + 1
                    phrase_count = 0
            if user_query[c] == " " and phrase_count == 0:
                user_splitted_query.append(user_query[query_start:c])
                query_start = c + 1
        if phrase_count != 0 and phrase_count != 2:
            print(
                Fore.RED + "\nThere where anomalies in the query format that could lead to showing you what you're not looking for."
                           "\nYour request has been translated has follow:\n")
            for query in filter(None, user_splitted_query):
                print("\t" + query)
            while True:
                user_continue = input(Fore.YELLOW + "\nContinue? [Y/N] >>> ")
                if user_continue.upper() == 'Y':
                    print()
                    return filter(None, user_splitted_query), True
                elif user_continue.upper() == 'N':
                    print()
                    return "STOP", False
                else:
                    print(Fore.LIGHTRED_EX + "Please, select a valid option", end="")

        #print("\n" + str(user_splitted_query) + "\n")

        # rimuovo gli elementi vuoti dalla lista e la ritorno
        return filter(None, user_splitted_query), True

    def get_whoosh_queries(self, user_splitted_query):
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
                warnings.append(Fore.YELLOW + str(query_element[0]) + Fore.CYAN + " is not a valid element so"
                                                                                  " the rest of the query will be searched among every element. ")

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
                                Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so"
                                                                                "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among " + Fore.YELLOW +
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
                                Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                                " it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every " + Fore.YELLOW + "venue")
                    venues_whoosh_query = venues_whoosh_query + query_text + " ) OR "
            else:
                if query_field[0] not in self.publications_fields and query_field[0] not in self.venues_fields and \
                        query_field[0] != '*':
                    if query_element[0] == "*" and query_element[1]:
                        warnings.append(Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                                        "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every "+ Fore.YELLOW+ "publication")
                    else:
                        warnings.append(Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                                        "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every element.")
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

    def threshold_algorithm(self, publications, venues):
        i = 0
        threshold_results = []

        #print(">>>>>> "+str(len(pubs)))
        #print(">>>>>> "+str(len(venues)))
        while True:

            if i >= len(publications) or i >= len(venues):
                break

            pub_to_ven = {}
            ven_to_pub = {}
            score_v = venues[i]["score"]
            score_p = publications[i]["score"]
            threshold = score_p + score_v

            venue_found = False
            #cerco se la crossref è nelle venues
            for v in venues:
                if "crossref" in publications[i] and publications[i]["crossref"] != "" and publications[i]["crossref"] == v["key"]:
                    # ho trovato una corrispondenza. Prendo lo score della venue, lo sommo allo score della pub i-esima
                    pub_to_ven.update({ "p":publications[i] ,  "v":v ,  "combined_score":publications[i]["score"]+v["score"]} )
                    venue_found = True
                    break
            if not venue_found:
                pub_to_ven.update({ "p": publications[i], "v": None, "combined_score":publications[i]["score"]  })

            threshold_results.append(pub_to_ven)

            publication_found = False
            # cerco se la crossref è nelle pubs
            for p in publications:
                if "crossref" in p and p["crossref"] != "" and venues[i]["key"] == p["crossref"]:
                    # ho trovato una corrispondenza. Prendo lo score della pub, lo sommo allo score della venue i-esima
                    ven_to_pub.update({ "p":p , "v":venues[i], "combined_score":p["score"]+venues[i]["score"]})
                    publication_found = True
                    break
            if not publication_found:
                ven_to_pub.update( { "p":None , "v": venues[i], "combined_score":venues[i]["score"] })

            # ho messo le due righe nella tabella

            threshold_results.append(ven_to_pub)

            threshold_results = sorted(threshold_results, key = lambda i: i['combined_score'], reverse=True)

            if threshold_results[0]['combined_score'] > threshold:
                break
            else:
                i = i+1

        #print(">>>>> FERMO DOPO "+str(i+1)+" ITERAZIONI.")
        return threshold_results

    def print_threshold_results(self, threshold_results):

        if not threshold_results:
            print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")
            return

        # rimozione duplicati
        threshold_results = [i for n, i in enumerate(threshold_results) if i not in threshold_results[n + 1:]]

        if len(threshold_results) < self.user_output_results:
            self.user_output_results = len(threshold_results)

        print()
        i=0
        while i < self.user_output_results and len(threshold_results) > 0:
            venue_i = threshold_results[0]["v"]
            pub_i = threshold_results[0]["p"]
            if venue_i != None:
                punti = venue_i["score"]
                for j in range(len(threshold_results)):
                    pub_j = threshold_results[j]["p"]
                    if pub_j != None and "crossref" in pub_j and pub_j["crossref"] == venue_i["key"]:
                        punti = punti + pub_j["score"]
                print("\n\t" +Back.MAGENTA + Fore.BLACK + "\tResult #" + str(i+1) + "\t", end="\t")
                if self.user_score:
                    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                        round(punti, 3)))
                self.print_element(venue_i, -1)
                for j in range(len(threshold_results)):
                    pub_j = threshold_results[j]["p"]
                    if pub_j != None and "crossref" in pub_j and pub_j["crossref"] == venue_i["key"]:
                        punti = punti + pub_j["score"]
                        self.print_element(pub_i, j)
                threshold_results[:] = [d for d in threshold_results if d.get('v') != venue_i]
            elif pub_i != None:
                print("\n\t" +Back.MAGENTA + Fore.BLACK + "\tResult #" + str(i + 1) + "\t", end="\t")
                if self.user_score:
                    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                        round(pub_i["score"], 3)))
                self.print_element(pub_i, -1)
                threshold_results[:] = [d for d in threshold_results if d.get('p') != pub_i]

            i = i + 1

    def print_results(self, results_set):
        if len(results_set) > 0:
            results_shown = 0
            print()
            for result in results_set:
                if results_shown < self.user_output_results:
                    print("\n\t" + Back.MAGENTA + Style.BRIGHT + Fore.BLACK + "\tResult #" + str(results_shown + 1)+"\t", end="\t")
                    if self.user_score:
                        print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Score:\t" + Style.BRIGHT + Fore.BLACK + str(
                            round(result['score'], 3)), end="")
                    print()
                    self.print_element(result, -1)
                    results_shown += 1
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")

    def print_element(self, element, j):
        if not self.user_score:
            print()
        if element["pubtype"] in Parsing.publications:
            if j >= 0:
                print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tPUBLICATION #" + str(j + 1))
            else:
                print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tPUBLICATION")
        elif element["pubtype"] in Parsing.venues or element["pubtype"] == "journal":
            print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tVENUE")

        print(Style.BRIGHT + Fore.BLACK + "\t\t\tTitle: " + Style.RESET_ALL + str(element["title"]), end="")
        if not str(element["title"]).endswith("\n"):
            print()
        if element['author']:
            print(Style.BRIGHT + Fore.BLACK + "\t\t\tAuthors: ", end="")
            authors = element["author"].split("\n")
            print(*(author for author in authors if author != ""), sep=", ", end="\n")
        if element["year"] != '':
            print(Style.BRIGHT + Fore.BLACK + "\t\t\tYear: " + Style.RESET_ALL + element['year'], end="")
        if element["pubtype"] in Parsing.publications:
            if element['journal'] != '' and element['volume'] != '':
                print(Style.BRIGHT + Fore.BLACK + "\t\t\tJournal: " + Style.RESET_ALL + element['journal'], end="")
                print(Style.BRIGHT + Fore.BLACK + "\t\t\tVolume: " + Style.RESET_ALL + element['volume'], end="")
        if "publisher" in element and element["publisher"] != "":
            print(Style.BRIGHT + Fore.BLACK + "\t\t\tPublisher: " + Style.RESET_ALL + element['publisher'], end="")
        print(Style.BRIGHT + Fore.BLACK + "\t\t\tType: " + Style.RESET_ALL + element['pubtype'])

# TODO: commentare il codice
# TODO: pulire il codice

# article.title:"An Evaluation of Object-Oriented" venue.title:GTE
"""
article.title:"An Evaluation of Object-Oriented" venue.title:GTE article.title:"the Incremental Migration"

"performance evaluation of object" venue.title:"ACM SIGSOFT"

"ware Engineering Notes" "performance evaluation of object"
"""

# inproceedings.title:"Database Systems 2.0" inproceedings.title:"Structured Data Meets News" venue.title:"Proceedings of the VLDB 2019 PhD Workshop" venue:VLDB