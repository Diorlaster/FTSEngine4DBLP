from colorama import init
from colorama import Fore, Back, Style
from XML_Operations import Indexing
from Search_Operations import Searching
import FAQ

if __name__ == "__main__":
    """The program starts its execution here"""

    user_command = None;
    user_output_results = 3
    user_ranking_models = {'Frequency': False,
                           'BM25F': True,
                           }
    user_warnings = True
    user_score = True

    """Main title for the menu"""
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
    print("     "+Back.BLUE + Fore.LIGHTWHITE_EX+ "                                FULL-TEXT Search Engine for DBLP                               ")
    print()

    indexes = Indexing.Index();
    indexes.load_check_indexes()

    while True:
        """Main menu for the program"""

        print(Back.BLUE+Fore.BLACK+" MAIN MENU ")
        print(Style.BRIGHT+Fore.BLUE+"\nWhat would you like to do?")
        print(Fore.BLUE+"\t1 > Search")
        print(Fore.BLUE+"\t2 > Change ranking model         [", end="")
        if user_ranking_models['BM25F']:
            print(Style.BRIGHT+Fore.WHITE+" OKAPI BM25F "+Style.RESET_ALL+Fore.BLUE+"| FREQUENCY ]")
        else:
            print(Fore.BLUE+" OKAPI BM25F | "+Style.BRIGHT+Fore.WHITE+"FREQUENCY"+Style.RESET_ALL+Fore.BLUE+" ]")
        print(Fore.BLUE+"\t3 > Set output results limit     [ "+Style.BRIGHT+Fore.WHITE+str(user_output_results)+Style.RESET_ALL+Fore.BLUE+" ]")
        if user_warnings:
            print(Fore.BLUE+"\t4 > Switch warnings preference   [ "+Style.BRIGHT+Fore.WHITE+"SHOW"+Style.NORMAL+Fore.BLUE+" | HIDE ]")
        else :
            print(Fore.BLUE+"\t4 > Switch warnings preference   [ SHOW | "+ Style.BRIGHT + Fore.WHITE + "HIDE"+ Style.RESET_ALL+Fore.BLUE+" ]")
        if user_score:
            print(Fore.BLUE+"\t5 > Switch score preference      [ "+Style.BRIGHT+Fore.WHITE+"SHOW"+Style.NORMAL+Fore.BLUE+" | HIDE ]")
        else :
            print(Fore.BLUE+"\t5 > Switch score preference      [ SHOW | "+ Style.BRIGHT + Fore.WHITE + "HIDE"+ Style.RESET_ALL+Fore.BLUE+" ]")
        print(Fore.BLUE+"\t6 > FAQ")
        print(Fore.BLUE+"\t7 > Exit")
        print()
        user_command = input(Fore.YELLOW+">>> ")
        print()

        if user_command == '1':
            if user_ranking_models['BM25F']:
                Searching.Searcher(indexes, user_output_results, user_warnings, user_score, "BM25F").search()
            elif user_ranking_models['Frequency']:
                Searching.Searcher(indexes, user_output_results, user_warnings, user_score, "Frequency").search()
        elif user_command == '2':
            if user_ranking_models['BM25F']:
                print(Style.BRIGHT+Fore.BLUE + "Ranking model switched from OKAPI BM25F to FREQUENCY!\n")
                user_ranking_models['BM25F'] = False
                user_ranking_models['Frequency'] = True
            else:
                print(Style.BRIGHT+Fore.BLUE + "Ranking model switched from FREQUENCY to OKAPI BM25F!\n")
                user_ranking_models['Frequency'] = False
                user_ranking_models['BM25F'] = True
        elif user_command == '3':
            while True:
                try:
                    user_output_results = int(input(Fore.YELLOW + "Enter your limit >>> "))
                    break
                except ValueError:
                    print(Fore.RED+"Invalid number...please, try again! ", end="")
        elif user_command == '4':
            user_warnings = not user_warnings
            if user_warnings:
                print(Style.BRIGHT + Fore.BLUE + "Warnings will be displayed!\n")
            else:
                print(Style.BRIGHT + Fore.BLUE + "Warnings won't be displayed!\n")
        elif user_command == '5':
            user_score = not user_score
            if user_score:
                print(Style.BRIGHT + Fore.BLUE + "Scores will be displayed!\n")
            else:
                print(Style.BRIGHT + Fore.BLUE + "Scores won't be displayed!\n")
        elif user_command == '6':
            FAQ.faqs_menu()
        elif user_command == '7':
            print(Style.BRIGHT+Fore.BLUE+"Come back soon!")
            print()
            break;
        else:
            print(Fore.RED+"Invalid option...please, try again!\n")
