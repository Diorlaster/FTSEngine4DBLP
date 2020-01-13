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



# TODO: commentare il codice
# TODO: pulire il codice

# article.title:"An Evaluation of Object-Oriented" venue.title:GTE
"""
article.title:"An Evaluation of Object-Oriented" venue.title:GTE article.title:"the Incremental Migration"

"performance evaluation of object" venue.title:"ACM SIGSOFT"

"ware Engineering Notes" "performance evaluation of object"
"""

# inproceedings.title:"Database Systems 2.0" inproceedings.title:"Structured Data Meets News" venue.title:"Proceedings of the VLDB 2019 PhD Workshop" venue:VLDB