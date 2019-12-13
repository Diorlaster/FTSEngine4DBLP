from colorama import Fore, Back, Style
from whoosh.qparser import QueryParser, MultifieldParser
import time

def search(indexes, user_output_results):

    publications_elements = ['publication', 'article', 'incollection', 'inproceedings', 'phdthesis', 'mastersthesis']

    print(Back.BLUE + Fore.WHITE + " MENU > CERCA ")
    query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")
    print()
    print(Fore.BLUE + '...la ricerca potrebbe richiedere un po\' di tempo...\n')

    #TODO CONTROLLARE 
    start_time = time.time()
    for p_element in publications_elements:
        if not query.startswith("\""):
            query_s = query.split(".")
            if query_s[0] == p_element:
                print("Ricerca pubblication tramite campo "+query_s[1])

    results_publications = None

    ### RICERCA PUBLICATIONS ###
    with indexes.publications_index.searcher() as publications_searcher:

        qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=indexes.publications_index.schema)
        q = qp.parse("pubtype:"+query_s[0] + " AND " + query_s[1])

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
