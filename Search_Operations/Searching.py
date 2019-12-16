from colorama import Fore, Back, Style
from whoosh.qparser import QueryParser, MultifieldParser
import time

publications_elements = ['publication', 'article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']
publications_fields = ['author', 'title', 'year']

def search(indexes, user_output_results):

    publications_elements_search = False

    print(Back.BLUE + Fore.WHITE + " MENU > CERCA ")
    user_query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")

    # ad ogni posizione di user_splitted_query avrò una query. Tutte andranno messe in OR.
    inizio = 0
    frase = 0
    user_splitted_query = []
    for c in range(0, len(user_query)):
        if user_query[c] == "\"":
            frase = frase + 1
            if frase%2 == 0:
                tmp = user_query[inizio:c+1].replace(" ","")
                if tmp != "":
                    user_splitted_query.append(user_query[inizio:c+1])
                inizio = c + 1
    if frase%2 != 0:
        print(Fore.RED+"Errore di digitazione nella query. Per favore, riprova")

    #user_splitted_query = user_query.split(" ")
    user_whoosh_query = "";
    # per ogni query eseguirò lo stesso controllo per tradurre la query per Whoosh
    for query in user_splitted_query:
        query_element = "*"
        query_field = "*"
        query_text = "*"
        query_translated = False
        if "." not in query and ":" not in query:
            print(Fore.CYAN + "--- WORD/PHRASE QUERY ---")
            query_text = query
        else:
            if ":" in query:
                query_analysis = query.partition(":")
                if "." in query_analysis[0]:
                    print("--- ELEMENT SPECIFICO CON FIELD SPECIFICO ---")
                    query_element = get_element(query_analysis[0])
                    if ":" in query_analysis[-1]:
                        query_field = get_field(str(query_analysis[-1]).partition(":")[0])
                        query_text = str(query_analysis[-1]).partition(":")[-1]
                else:
                    print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
                    query_element = get_element(query_analysis[0])
                    if query_element == query_analysis[0]:
                        # non ho trovato l'elemento.. potrebbe essere dunque un field .. controllo
                        query_field = get_field(query_analysis[0])
                    query_text = query_analysis[-1]
        user_whoosh_query = user_whoosh_query + "( "
        if not query_element == "*":
            user_whoosh_query = user_whoosh_query + "pubtype:"+query_element+" AND "
        if not query_field == "*":
            user_whoosh_query = user_whoosh_query + query_field+":"
        user_whoosh_query = user_whoosh_query + query_text+" ) OR "

    print(Fore.BLUE + '\n...la ricerca potrebbe richiedere un po\' di tempo...\n')
    start_time = time.time()

    """
    # se comincia con le ".." allora è una phrase query
    if query.startswith("\""):
        print(Fore.CYAN+"--- PHRASE QUERY ---\n")
    else:
        # altrimenti controllo se è una ricerca tramite campo
        print(query_s)
        for p_element in publications_elements:
            if query_s[0] == p_element:
                print("Ricerca pubblication tramite campo " + query_s[1])
                publications_elements_search = True
                publication_search_element()
                break
    """

    results_publications = None

    ### RICERCA PUBLICATIONS ###
    with indexes.publications_index.searcher() as publications_searcher:

        qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=indexes.publications_index.schema)
        #q = qp.parse("pubtype:"+query_s[0] + " AND " + query_s[1])
        user_whoosh_query = user_whoosh_query[:-3]
        print(user_whoosh_query)
        q = qp.parse(user_whoosh_query)

        results_publications = publications_searcher.search(q, limit=None)
        # controllo se ci sono risultati altrimenti stampo "Nessun risultato trovato"
        if len(results_publications) > 0:
            print(Fore.BLUE+"Sono stati trovati "+Style.BRIGHT+Fore.WHITE+str(len(results_publications))+Style.RESET_ALL+Fore.BLUE+" risultati!\n")
            # scorro i risultati, prendo i campi interessati e li stampo
            results_shown = 0
            for result in results_publications:
                if results_shown < user_output_results:
                    authors = result['author'].split('\n')
                    print(Back.MAGENTA + Style.BRIGHT + Fore.WHITE + "Risultato #" + str(results_shown + 1))
                    print(Style.BRIGHT + Fore.MAGENTA + "Score:\t" + Style.BRIGHT + Fore.WHITE + str(
                        result.score) + "\n")
                    print(Style.BRIGHT + Fore.MAGENTA + "Authors")
                    for auth in authors:
                        print("\t" + Style.BRIGHT + Fore.WHITE + auth)
                    print(Style.BRIGHT + Fore.MAGENTA + "Title")
                    print("\t" + Style.BRIGHT + Fore.WHITE + result['title'])
                    print(Style.BRIGHT + Fore.MAGENTA + "Pub-Type")
                    print("\t" + Style.BRIGHT + Fore.WHITE + result['pubtype'] + "\n")
                    results_shown += 1
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato")

    # TODO applico Threshold sulla lista delle pubs e quella delle venues ( devo tirar fuori la stampa prima )

    end_time = time.time()
    print(Fore.BLUE + 'La ricerca è stata completata in', round((end_time - start_time)), Fore.BLUE + 'secondi!\n')


def get_element(query_analysis):
    for element in publications_elements:
        if query_analysis == element:
            print(Fore.CYAN + "--- ELEMENT QUERY SENZA FIELD SPECIFICO ---")
            if element == "publication":
                return "*"
            return element
    print(Fore.CYAN + "--- ELEMENTO NON VALIDO---")
    #TODO verificare il comportamento
    return query_analysis


def get_field(query_analysis):
    for field in publications_fields:
        if query_analysis[0] == field:
            print(Fore.CYAN + "--- FIELD SPECIFICO ---")
            return field
    print(Fore.CYAN + "--- FIELD NON VALIDO ---")
    #TODO verificare il comportamento
    return query_analysis