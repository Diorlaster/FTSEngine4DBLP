from colorama import Fore, Back, Style
from whoosh.qparser import QueryParser, MultifieldParser
import time

def search(indexes, user_output_results):
    print(Back.BLUE + Fore.WHITE + " MENU > CERCA ")
    query = input(Fore.YELLOW + "Che cosa vuoi cercare? >>> ")
    print()
    print(Fore.BLUE + '...la ricerca potrebbe richiedere un po\' di tempo...\n')

    with indexes.publications_index.searcher() as publications_searcher:

        start_time = time.time()
        qp = MultifieldParser(["author", "title", "year", "pubtype"], schema=indexes.publications_index.schema)
        q = qp.parse(query)

        results = publications_searcher.search(q)

        if len(results) > 0:
            results_shown = 0
            for result in results:
                if results_shown < user_output_results:
                    if result['pubtype'] != '':
                        authors = result['author'].split('\n')
                        print(Back.MAGENTA + Style.BRIGHT + Fore.WHITE + "Risultato #" + str(results_shown + 1))
                        print(Style.BRIGHT + Fore.MAGENTA + "Score:\t"+Style.BRIGHT+Fore.WHITE+ str(result.score)+"\n")
                        print(Style.BRIGHT + Fore.MAGENTA + "Authors")
                        for auth in authors:
                            print("\t" + Style.BRIGHT + Fore.WHITE + auth)
                        print(Style.BRIGHT + Fore.MAGENTA + "Title")
                        print("\t" + Style.BRIGHT + Fore.WHITE + result['title'])
                        print(Style.BRIGHT + Fore.MAGENTA + "Pub-Type")
                        print("\t" + Style.BRIGHT + Fore.WHITE + result['pubtype']+"\n")
                        results_shown += 1
                    else:
                        continue
            if results_shown == 0:
                print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato")
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "Nessun risultato trovato")

        end_time = time.time()
        print(Fore.BLUE + '\nLa ricerca è stata completata in', round((end_time - start_time)), Fore.BLUE + 'secondi!\n')