from colorama import Fore

publications_elements = ['publication', 'article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
publications_fields = ['author', 'title', 'year']
venues_fields = ['title', 'publisher']

def get_queries(user_query):
    """take the input text from user and split it in valid queries"""

    """every user_splitted_query list's element is a query. They will be joined with OR operator later"""
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
        """If we think something is strange with the query, we ask user to look at our translation before continue."""
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

    """Removing empty elements from the list"""
    return filter(None, user_splitted_query), True


def get_whoosh_queries(user_splitted_query):
    """Take every query and translate it from FTSE-4-DBLP syntax into Whoosh's query language"""

    publications_whoosh_query = ""
    venues_whoosh_query = ""
    query_warnings = {}

    for query in user_splitted_query:
        """If an element/field has been successfully translated here we store TRUE and it's translation"""
        query_element = "*", False
        query_field = "*", False
        query_text = "*"
        """Store warnings for the current query..."""
        warnings = []

        """Here we start to analyze the query, looking for a valid element and/or field"""
        if ("." not in query and ":" not in query) or (query.startswith("\"") and query.endswith("\"")):
            query_text = query
        else:
            if ":" in query:
                query_analysis = query.partition(":")
                if "." in query_analysis[0]:
                    if str(query_analysis[0]).partition(".")[0].lower() == 'venue':
                        query_element = ('venue', True)
                    else:
                        query_element = get_element(str(query_analysis[0]).partition(".")[0].lower())
                    query_field = get_field(str(query_analysis[0]).partition(".")[-1].lower())
                    query_text = query_analysis[-1]
                else:
                    if str(query_analysis[0]).lower() == 'venue':
                        query_element = ('venue', True)
                    else:
                        query_element = get_element(query_analysis[0].lower())
                    query_field = get_field(query_analysis[0].lower())
                    query_text = query_analysis[-1]
            elif "." in query:
                query_analysis = query.partition(".")
                if str(query_analysis[0]).lower() == 'venue':
                    query_element = ('venue', True)
                else:
                    query_element = get_element(query_analysis[0].lower())
                query_field = get_field(query_analysis[-1].lower())
                if not query_field[1]:
                    query_text = query_analysis[-1]


        """Here we translate the previously found element and field in Whoosh's language"""
        if not query_element[1] and query_element[0] != '*':
            warnings.append(Fore.YELLOW + str(query_element[0]) + Fore.CYAN + " is not a valid element so"
                                                                              " the rest of the query will be searched among every element. ")
        if query_element[1] and query_element[0] != '*':
            if query_element[0] in publications_elements:
                publications_whoosh_query = publications_whoosh_query + "( "
                if query_element[0] != "*" and query_element[0] in publications_elements:
                    publications_whoosh_query = publications_whoosh_query + "pubtype:" + query_element[0] + " AND "
                if query_field[0] != "*":
                    if query_field[0] in publications_fields:
                        if query_field[1]:
                            publications_whoosh_query = publications_whoosh_query + query_field[0] + ":"
                    else:
                        warnings.append(
                            Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                            "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among " + Fore.YELLOW +
                            query_element[0])
                publications_whoosh_query = publications_whoosh_query + query_text + " ) OR "
            elif query_element[0] == 'venue':
                venues_whoosh_query = venues_whoosh_query + "( "
                if query_field[0] != "*":
                    if query_field[0] in venues_fields:
                        if query_field[1]:
                            venues_whoosh_query = venues_whoosh_query + query_field[0] + ":"
                    else:
                        warnings.append(
                            Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                            "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every " + Fore.YELLOW + "venue")
                venues_whoosh_query = venues_whoosh_query + query_text + " ) OR "
        else:
            if query_field[0] not in publications_fields and query_field[0] not in venues_fields and \
                    query_field[0] != '*':
                if query_element[0] == "*" and query_element[1]:
                    warnings.append(Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                                    "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every " + Fore.YELLOW + "publication")
                else:
                    warnings.append(Fore.YELLOW + str(query_field[0]) + Fore.CYAN + " is not a valid field so "
                                                                                    "it will be ignored. " + Fore.YELLOW + query_text + Fore.CYAN + " will be searched among every element.")
            if query_field[1] and query_field[0] != "*":
                if query_field[0] in publications_fields:
                    publications_whoosh_query = publications_whoosh_query + "( " + query_field[
                        0] + ":" + query_text + " ) OR "
                if not query_element[1] and query_field[0] in venues_fields:
                    venues_whoosh_query = venues_whoosh_query + "( " + query_field[0] + ":" + query_text + " ) OR "
            else:
                publications_whoosh_query = publications_whoosh_query + "( " + query_text + " ) OR "
                if not query_element[1]:
                    venues_whoosh_query = venues_whoosh_query + "( " + query_text + " ) OR "

        if warnings:
            """...add current query's warnings to the global warnings"""
            query_warnings.update({query: warnings})

    """Finally, return translated queries and warnings"""
    return publications_whoosh_query[:-3], venues_whoosh_query[:-3], query_warnings


def get_element(query_analysis):
    """Check if the current query string is a valid element or not"""

    if query_analysis in publications_elements:
        if query_analysis == "publication":
            """A valid element has been found so we set TRUE state but we keep * because publication generic element
            means that user want to search among every publication's element. In Whoosh's query language * is a 
            special character used to search every, just like regular expressions."""
            return "*", True
        else:
            return query_analysis, True
    elif query_analysis in publications_fields or query_analysis in venues_fields:
        return "*", False
    else:
        return query_analysis, False


def get_field(query_analysis):
    """Check if the current query string is a valid field or not"""

    if query_analysis in publications_fields or query_analysis in venues_fields:
        return query_analysis, True
    return query_analysis, False