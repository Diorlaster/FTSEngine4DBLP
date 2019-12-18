from colorama import init
from colorama import Fore, Back, Style
from XML_Operations import Indexing
from Search_Operations import Searching
user_command = None;
user_output_results = 3
user_ranking_models = {'frequency': False,
                       'okapi': True,
                       }

def faqs():
    while True:
        print(Back.BLUE+Fore.WHITE+" MENU > FAQ "+Style.RESET_ALL+Style.BRIGHT + Fore.BLUE + " Che cosa vuoi sapere?")
        print(Fore.BLUE+"1 > Cos'è FTSE-4-DBLP?")
        print(Fore.BLUE+"2 > Come funziona la ricerca?")
        print(Fore.BLUE+"3 > Cosa cambia tra i due modelli di ranking?")
        print(Fore.BLUE+"4 > Torna al menu principale")
        print()
        user_command = input(Fore.YELLOW + ">>> ")
        print()

        if user_command == '1':
            print(Fore.RED+"Lavori in corso...")
            print()
        elif user_command == '2':
            print(Fore.RED+"Lavori in corso...")
            print()
        elif user_command == '3':
            print(Fore.RED+"Lavori in corso...")
            print()
        elif user_command == '4':
            break
        else:
            print(Fore.RED+"Non hai selezionato un comando valido...riprova!")
    return

if __name__ == "__main__":

    init(autoreset=True)
    print()
    print("     " + Back.BLUE + Fore.LIGHTWHITE_EX + "                                                                                               ")
    print(Style.BRIGHT + Fore.BLUE + "      ______________________________________ " + Fore.WHITE + "        _____   " + Fore.BLUE + "     _______  _______  __     ________ ")
    print(Style.BRIGHT + Fore.BLUE + "     |    _______    ____    ________    ___|" + Fore.WHITE + "       /     |  " + Fore.BLUE + "    |   __  \|   _   \|  |   |    _   |")
    print(Style.BRIGHT + Fore.BLUE + "     |   |__     |  |    |  |____    |  |___ " + Fore.WHITE + "      /  /|  |  " + Fore.BLUE + "    |  |  \  |  |/   /|  |   |   |_|  |")
    print(Style.BRIGHT + Fore.BLUE + "     |    __|    |  |    |____   |   |   ___|" + Fore.WHITE + "     /  /_|  |_ " + Fore.BLUE + "    |  |  |  !   _  | |  |   |    ____|")
    print(Style.BRIGHT + Fore.BLUE + "     |   |       |  |     ____|  |   |  |___ " + Fore.WHITE + "    |_____    _|" + Fore.BLUE + "    |  |__/  |  |/   \|  |___|   |     ")
    print(Style.BRIGHT + Fore.BLUE + "     |___|       |__|    |_______|   |______|" + Fore.WHITE + "          |__|  " + Fore.BLUE + "    |_______/|_______/|______|___|     ")
    print()
    print("     "+Back.BLUE + Fore.LIGHTWHITE_EX+ "                              Motore di ricerca FULL-TEXT per DBLP                             ")
    print()

    indexes = Indexing.Index();
    indexes.load_check_indexes()

    while True:
        print(Back.BLUE+Fore.WHITE+" MENU "+Style.RESET_ALL+Style.BRIGHT+Fore.BLUE+" Che cosa posso fare?")
        print(Fore.BLUE+"1 > Cerca")
        print(Fore.BLUE+"2 > Cambia modello di ranking    [", end="")
        if user_ranking_models['okapi']:
            print(Style.BRIGHT+Fore.WHITE+" OKAPI BM25F "+Style.RESET_ALL+Fore.BLUE+"| FREQUENCY ]")
        else:
            print(Fore.BLUE+" OKAPI BM25F | "+Style.BRIGHT+Fore.WHITE+"FREQUENCY"+Style.RESET_ALL+Fore.BLUE+" ]")
        print(Fore.BLUE+"3 > Imposta numero di risultati  [ "+Style.BRIGHT+Fore.WHITE+str(user_output_results)+Style.RESET_ALL+Fore.BLUE+" ]")
        print(Fore.BLUE+"4 > FAQ")
        print(Fore.BLUE+"5 > Esci")
        print()
        user_command = input(Fore.YELLOW+">>> ")
        print()

        if user_command == '1':
            Searching.Searcher(indexes, user_output_results).search()
        elif user_command == '2':
            if user_ranking_models['okapi']:
                print(Style.BRIGHT+Fore.BLUE + "Modello di ranking cambiato da OKAPI BM25F a FREQUENCY!\n")
                user_ranking_models['okapi'] = False
                user_ranking_models['frequency'] = True
            else:
                print(Style.BRIGHT+Fore.BLUE + "Modello di ranking cambiato da FREQUENCY ad OKAPI BM25F!\n")
                user_ranking_models['frequency'] = False
                user_ranking_models['okapi'] = True
        elif user_command == '3':
            while True:
                try:
                    user_output_results = int(input(Fore.YELLOW + "Quale limite vuoi impostare? >>> "))
                    break
                except ValueError:
                    print(Fore.RED+"Non è un numero valido...riprova! ", end="")
        elif user_command == '4':
            faqs()
        elif user_command == '5':
            print(Style.BRIGHT+Fore.BLUE+"Torna presto!")
            print()
            break;
        else:
            print(Fore.RED+"Non hai selezionato un comando valido...riprova!")
