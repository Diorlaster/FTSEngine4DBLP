from colorama import Fore, Style, Back


def faqs_menu():
    """For a cleaner code, we preferred to move FAQS text from main file to another one"""

    while True:
        """FAQ's menu"""

        print(Back.BLUE + Fore.BLACK + " MAIN MENU > FAQ ")
        print(Style.BRIGHT + Fore.BLUE + "\n\tWhat would you like to know?")
        print(Fore.BLUE + "\t\t1 > About FTSE-4-DBLP")
        print(Fore.BLUE + "\t\t2 > How research works")
        print(Fore.BLUE + "\t\t3 > Differences between ranking models")
        print(Fore.BLUE + "\t\t4 > About warnings")
        print(Fore.BLUE + "\t\t5 > Back to main menu")
        print()
        user_command = input(Fore.YELLOW + ">>> ")
        print()
        if user_command == '1':
            about_ftse4dblp()
        elif user_command == '2':
            research_infos()
        elif user_command == '3':
            ranking_models_differences()
        elif user_command == '4':
            about_warnings()
        elif user_command == '5':
            break
        else:
            print(Fore.RED + "Invalid option...please, try again!")
    return


def about_ftse4dblp():
    print(Back.BLUE + Fore.BLACK + " MAIN MENU > FAQ > ABOUT FTSE-4-DBLP ")
    print("\n\t"+Fore.BLUE +"FTSE-4-DBLP"+ Fore.RESET+" is a full-text search engine for "+Fore.YELLOW+"DBLP"+Fore.RESET+
          " developed in Python by "+Fore.RED+"Angelo Di Franco"+Fore.RESET+" and "+Fore.RED+"Francesco Franco"+Fore.RESET+".\n\tIt uses "
        + Fore.YELLOW+"Sax" + Fore.RESET + " to parse the DBLP XML file and "+Fore.YELLOW+"Whoosh"+Fore.RESET+" to query, search and rank the elements.\n")
    print( "\t" + "The "+Fore.YELLOW+"DBLP"+Fore.RESET+" computer science bibliography provides open bibliographic information on major computer science journals and proceedings."
           "\n\tOriginally created at the University of Trier in 1993, DBLP is now operated and further developed by Schloss Dagstuhl. ")
    print( "\n\t" + Fore.YELLOW+"Sax" + Fore.RESET + " is an XML parser that operates element by element, line by line and emits events as it goes step by step through the file.")
    print( "\t" + Fore.YELLOW+"Whoosh"+ Fore.RESET +" is a fast, pure Python programmer library for creating a search engine.")
    print()


def research_infos():
    print(Back.BLUE + Fore.BLACK + " MAIN MENU > FAQ > HOW RESEARCH WORKS ")
    print("\n\tResearch in "+Fore.BLUE+"FTSE-4-DBLP"+Fore.RESET+" follow some simple rules.")
    print("\n\tYou can search: \n\t\tsingle words with a "+Fore.YELLOW+"keyword-query"+Fore.RESET+" which is a alphanumeric character sequence delimited by "+Fore.YELLOW+"spaces "+Fore.RESET+
          "\n\t\tphrases with a "+Fore.YELLOW+"phrase-query"+ Fore.RESET+" which is a sequence of keywords delimited by "+Fore.YELLOW+"\""+Fore.RESET+" ( double quote )" )
    print("\n\tYou can search a word or a phrase among specific "+Fore.YELLOW+"elements"+Fore.RESET+" and/or "+Fore.YELLOW+"fields"+Fore.RESET+" as follow: \n")
    print("\t\t"+Fore.GREEN+"[element].[field]:[keyword/phrase] ")
    print("\n\t\tYou don\'t have to specify both! For example, you can look for the keyword "+Fore.GREEN+"information"+Fore.RESET+" among the "+Fore.YELLOW+"field title"+Fore.RESET+" of every element by typing "+Fore.GREEN+"title:information "+Fore.RESET+
          "\n\t\t\tor for the phrase "+Fore.GREEN+"\"information retrieval\""+Fore.RESET+" among a specific element without specifying the field by typing "+Fore.GREEN+"article.\"information retrieval\""+Fore.RESET+" or "+Fore.GREEN+"article:\"information retrieval\".")
    print("\t\tAs you can see, when you are not specifying a field you can both use "+Fore.YELLOW+"."+Fore.RESET+" or "+Fore.YELLOW+":"+Fore.RESET+" to specify an element because FTSE-4-DBLP is smart enough to understand when you do specify an element or a field and when you don\'t.")
    print("\n\t\tBut what do we mean with "+Fore.YELLOW+"elements"+Fore.RESET+" and "+Fore.YELLOW+"fields"+Fore.RESET+"?")
    print("\n\t\tDBLP provides two big type of data: "+Fore.YELLOW+"publications"+Fore.RESET+" and "+Fore.YELLOW+"venues"+Fore.RESET+"."
          "Each one has elements ( such as article for publications and book for venues ) each of which has fields but you can only specify some of them!")
    print("\n\t\tAs "+Fore.YELLOW+"publication elements"+Fore.RESET+", you can use "+Fore.MAGENTA+"article incollection inproceedings phdthesis mastersthesis "+Fore.RESET+"and a special one: "+Fore.MAGENTA+"publication"+Fore.RESET+" which is used to specify that you"
          "are looking for a publication with a generic element.")
    print("\n\t\tAs "+Fore.YELLOW+"venue elements"+Fore.RESET+" you can only use the special element "+Fore.MAGENTA+"venue"+Fore.RESET+" to specify that you are looking for a venue.")
    print("\n\t\tAs "+Fore.YELLOW+"publication fields"+Fore.RESET+", you can use "+Fore.MAGENTA+"author title year"+Fore.RESET+".")
    print("\n\t\tAs "+Fore.YELLOW+"venues fields"+Fore.RESET+", you can use "+Fore.MAGENTA+"title publisher"+Fore.RESET+".")
    print("\n\t\tIf an "+Fore.YELLOW+"element is not specified"+Fore.RESET+", FTSE-4-DBLP will search among "+Fore.YELLOW+"every element"+Fore.RESET+".")
    print("\n\t\tIf a "+Fore.YELLOW+"field"+Fore.RESET+" is not specified, FTSE-4-DBLP will search among "+Fore.YELLOW+"every field of every element ( if element is not specified )"+Fore.RESET+".")
    print("\n\t\tSo, in short:\n"+Fore.GREEN+""
          "\n\t\t\tf-t-s : ([field:] search-pattern)+"
		  "\n\t\t\tsearch-pattern : keyword | \"phase\""
		  "\n\t\t\tfield: pub-search | venue-search"
		  "\n\t\t\tpub-search : pub-ele[.pub-field]"
		  "\n\t\t\tpub-ele: publication | article | incollection | inproc | phThesis | masterThesis"
		  "\n\t\t\tpub-field: author | title | year"
		  "\n\t\t\tvenue-search: venue[.venue-field]"
		  "\n\t\t\tvenue-field: title | publisher "+Fore.RESET )
    print("\n\tWe did our best to prevent failures or unexpected behavior so FTSE-4-DBLP will handle possible problems and show some "+Fore.YELLOW+"warnings"+Fore.RESET+" ( if enabled ) when you don't follow these rules but nothing is perfect so you may get unwanted or unoptimized results if you type something strange.")
    print()


def ranking_models_differences():
    print(Back.BLUE + Fore.BLACK + " MAIN MENU > FAQ > DIFFERENCES BETWEEN RANKING MODELS ")
    print("\n\t"+Fore.BLUE+"FTSE-4-DBLP"+Fore.RESET+" provides two different ranking models for your results: "+Fore.YELLOW+"Okapi BM25F"+Fore.RESET+" and "+Fore.YELLOW+"Frequency"+Fore.RESET+".")
    print("\n\t\t"+Fore.YELLOW+"Okapi BM25F"+Fore.RESET+" is a modified version of Okapi BM25. It has an extension to multiple weighted fields. "
        "Unlike BM25, the model is applicable to structured documents consisting of multiple fields. The model "
        "preserves term frequency non-linearity and removes the independence assumption between same term occurrences.")
    print("\n\t\t"+Fore.YELLOW+"Frequency"+Fore.RESET+" ranking estimate the relevance of documents to a given search query by counting its occurrences: the higher the number, the higher the score.")
    print("\n\tTo combine publications and venues score when both are in the results set, FTSE-4-DBLP use the "+Fore.YELLOW+"Threshold Algorithm"+Fore.RESET+". More infos can be found in the following paper:")
    print("\n\t\t"+Fore.GREEN+"R. Fagin, A. Lotem and M. Naor, Optimal aggregation algorithms for middleware, Journal of Computer and System Sciences 66, p. 614-656, 2003")
    print()

def about_warnings():
    print(Back.BLUE + Fore.BLACK + " MAIN MENU > FAQ > ABOUT WARNINGS \n")
    print("\tWe did our best to prevent and handle failures or unexpected behavior but "+Fore.BLUE+"FTSE-4-DBLP"+Fore.YELLOW+" will show some "+Fore.YELLOW+"warnings "+Fore.RESET+"in case something is wrong with the query syntax. ")
    print("\tYou can choose to show possible warnings or not by switching the "+Fore.YELLOW+"option"+Fore.RESET+" in the menu despite is "+Fore.YELLOW+"highly recommended"+Fore.RESET+" not to change it.")
    print("\n\tSome "+Fore.YELLOW+"critical warnings"+Fore.RESET+" cannot be turned off in order to increase the "+Fore.YELLOW+"software's robustness"+Fore.RESET+".")
    print()
