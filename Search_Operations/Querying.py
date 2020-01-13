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

    # print("\n" + str(user_splitted_query) + "\n")

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
                                                                                    "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every " + Fore.YELLOW + "publication")
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