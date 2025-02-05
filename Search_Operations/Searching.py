from colorama import Fore, Back, Style
from whoosh.qparser import MultifieldParser
from whoosh.scoring import Frequency, BM25F
from Search_Operations import Printing, Querying
import time


class Searcher:
    """Our program's core. Here we launch translation, search among indexes and launch result's print."""

    user_output_results = None;
    publications_index = None
    publications_results = []
    venues_index = None
    venues_results = []
    user_warnings = None
    user_score = None
    query_warnings = {}
    user_ranking_model = None

    def __init__(self, indexes, user_output_results, user_warnings, user_score, user_ranking_model):
        self.publications_index = indexes.publications_index
        self.venues_index = indexes.venues_index
        self.user_output_results = user_output_results
        self.publications_results = []
        self.venues_results = []
        self.user_warnings = user_warnings
        self.user_score = user_score
        self.query_warnings = {}
        if user_ranking_model == "BM25F":
            self.user_ranking_model = BM25F
        elif user_ranking_model == "Frequency":
            self.user_ranking_model = Frequency

    def search(self):
        """Every search starts here. We ask for multiple queries, we launch translation and we print the results."""

        print(Back.BLUE + Fore.BLACK + " MAIN MENU > SEARCH ")
        user_query = input(Fore.YELLOW + "\n\tWhat are you looking for? >>> ")
        print()

        """We split user's text into individual queries"""
        user_splitted_query, user_continue = Querying.get_queries(user_query)

        """If something went wrong during translation and user didn't want to continue the research is over and we return to the main menu"""
        if not user_continue:
            return

        """Translate individual queries into Whoosh's queries."""
        user_p_query, user_v_query, self.query_warnings = Querying.get_whoosh_queries(user_splitted_query);

        if self.user_warnings:
            if self.query_warnings:
                print("\t"+Back.CYAN + Fore.BLACK + "\tWARNINGS\t"+Style.RESET_ALL+"\n")
                for query, warnings in self.query_warnings.items():
                    for warning in warnings:
                        print(Fore.CYAN + "\t\tin " + Fore.YELLOW + query + Fore.CYAN + " | " + warning)
                print("\n")

        print(Fore.BLUE + '\t...your request may require some time...\n')
        start_time = time.time()

        """Search among publications's index..."""
        with self.publications_index.searcher(weighting=self.user_ranking_model) as publications_searcher:
            try:
                qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=self.publications_index.schema)
                q = qp.parse(user_p_query)
                results = publications_searcher.search(q, limit=None)
                """Due to scope's problems with Whoosh's searcher, we have to store the results's set manually"""
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

        """Search among venues's index..."""
        with self.venues_index.searcher(weighting=self.user_ranking_model) as venues_searcher:
            try:
                qp = MultifieldParser(['title', 'publisher'], schema=self.venues_index.schema)
                q = qp.parse(user_v_query)
                results = venues_searcher.search(q, limit=None)
                """Due to scope's problems with Whoosh's searcher, we have to store the results's set manually"""
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

        """According to the results set's length, we choose the best way to print."""
        if len(self.publications_results) > 0 and len(self.venues_results) > 0:
            threshold_results = self.threshold_algorithm(self.publications_results, self.venues_results)
            print( "\t" + Style.BRIGHT + Fore.BLACK + str(len(self.publications_results)+len(self.venues_results))
                   + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ", end="")
            Printing.print_threshold_results(threshold_results, self.user_output_results, self.user_score)
        elif len(self.publications_results) <= 0 and len(self.venues_results) > 0:
            print("\t" + Style.BRIGHT + Fore.BLACK + str(len(self.venues_results))
                  + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ",
                  end="")
            Printing.print_results(self.venues_results, self.user_output_results, self.user_score)
        elif len(self.publications_results) > 0 and len(self.venues_results) <= 0:
            print("\t" + Style.BRIGHT + Fore.BLACK + str(len(self.publications_results))
                    + Style.RESET_ALL + Fore.BLUE + " elements found. The following are the most relevant results: ",
                  end="")
            Printing.print_results(self.publications_results, self.user_output_results, self.user_score)
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")

        end_time = time.time()

        print("\n\t" + Fore.BLUE + 'Request completed in ', round((end_time - start_time),1), Fore.BLUE + 'seconds!\n')


    def threshold_algorithm(self, publications, venues):
        """Our Threshold Algorithm's implementation. It mixes results from both publications and venues set and return a
        whole new, unique set."""

        i = 0
        threshold_results = []

        while True:
            if i >= len(publications) or i >= len(venues):
                break

            pub_to_ven = {}
            ven_to_pub = {}
            score_v = venues[i]["score"]
            score_p = publications[i]["score"]
            threshold = score_p + score_v

            venue_found = False
            """check if the current publication has a valid crossref to any venue from the venue's results set"""
            for v in venues:
                if "crossref" in publications[i] and publications[i]["crossref"] != "" and publications[i]["crossref"] == v["key"]:
                    pub_to_ven.update({ "p":publications[i] ,  "v":v ,  "combined_score":publications[i]["score"]+v["score"]} )
                    venue_found = True
                    break
            if not venue_found:
                pub_to_ven.update({ "p": publications[i], "v": None, "combined_score":publications[i]["score"]  })

            threshold_results.append(pub_to_ven)

            publication_found = False
            """check if the current venue has a valid crossref to any publication from the publications's results set"""
            for p in publications:
                if "crossref" in p and p["crossref"] != "" and venues[i]["key"] == p["crossref"]:
                    ven_to_pub.update({ "p":p , "v":venues[i], "combined_score":p["score"]+venues[i]["score"]})
                    publication_found = True
                    break
            if not publication_found:
                ven_to_pub.update( { "p":None , "v": venues[i], "combined_score":venues[i]["score"] })


            threshold_results.append(ven_to_pub)

            """Threshold Algorithm needs a ordered set before the comparision."""
            threshold_results = sorted(threshold_results, key = lambda i: i['combined_score'], reverse=True)

            """Ending condition: if true, the threshold has been exceeded so the algorithm is over."""
            if threshold_results[0]['combined_score'] > threshold:
                break
            else:
                i = i+1

        return threshold_results




