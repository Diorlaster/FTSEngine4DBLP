from colorama import Fore, Style, Back

from XML_Operations import Parsing

def print_threshold_results(threshold_results, user_output_results, user_score):
    """Print results that have been selected via the Threshold Algorithm"""

    if not threshold_results:
        print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")
        return

    """Removing duplicates"""
    threshold_results = [i for n, i in enumerate(threshold_results) if i not in threshold_results[n + 1:]]

    """Check user's output preferences"""
    if len(threshold_results) < user_output_results:
        user_output_results = len(threshold_results)

    print()
    i = 0
    while i < user_output_results and len(threshold_results) > 0:
        venue_i = threshold_results[0]["v"]
        pub_i = threshold_results[0]["p"]
        if venue_i != None:
            """If we have a venue as relevant result, we decided to print under the same result every relevant related 
            publication. Related means that we have a cross-reference between a venue and a publication."""
            total_score = venue_i["score"]
            for j in range(len(threshold_results)):
                pub_j = threshold_results[j]["p"]
                if pub_j != None and "crossref" in pub_j and pub_j["crossref"] == venue_i["key"]:
                    total_score = total_score + pub_j["score"]
            print("\n\t" + Back.MAGENTA + Fore.BLACK + "\tResult #" + str(i + 1) + "\t", end="\t")
            if user_score:
                print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                    round(total_score, 3)))
            print_element(venue_i, -1, user_score)
            printed_counter = 1
            for j in range(len(threshold_results)):
                pub_j = threshold_results[j]["p"]
                if pub_j != None and "crossref" in pub_j and pub_j["crossref"] == venue_i["key"]:
                    total_score = total_score + pub_j["score"]
                    print_element(pub_j, printed_counter, user_score)
                    printed_counter = printed_counter + 1
            threshold_results[:] = [d for d in threshold_results if d.get('v') != venue_i]
        elif pub_i != None:
            """Otherwise, we print the single publication result"""
            print("\n\t" + Back.MAGENTA + Fore.BLACK + "\tResult #" + str(i + 1) + "\t", end="\t")
            if user_score:
                print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Total Score: " + Style.BRIGHT + Fore.BLACK + str(
                    round(pub_i["score"], 3)))
            print_element(pub_i, -1, user_score)
            threshold_results[:] = [d for d in threshold_results if d.get('p') != pub_i]

        i = i + 1


def print_results(results_set, user_output_results, user_score):
    """Print results in case the Threshold Algorithm has not been used which means that publications OR venues results
    set was empty. In this case we print results individually."""

    if len(results_set) > 0:
        results_shown = 0
        print()
        for result in results_set:
            if results_shown < user_output_results:
                print("\n\t" + Back.MAGENTA + Style.BRIGHT + Fore.BLACK + "\tResult #" + str(results_shown + 1) + "\t",
                      end="\t")
                if user_score:
                    print(Style.BRIGHT + Fore.LIGHTMAGENTA_EX + "Score:\t" + Style.BRIGHT + Fore.BLACK + str(
                        round(result['score'], 3)), end="")
                print()
                print_element(result, -1, user_score)
                results_shown += 1
    else:
        print(Style.BRIGHT + Fore.MAGENTA + "\tNo result found")


def print_element(element, j, user_score):
    """For a cleaner code, we choose to create a generic function to print a single publication or venue.
    Some fields may be empty or not exists so we check before print them."""

    if not user_score:
        print()
    if element["pubtype"] in Parsing.publications:
        if j >= 0:
            print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tPUBLICATION #" + str(j))
        else:
            print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tPUBLICATION")
    elif element["pubtype"] in Parsing.venues or element["pubtype"] == "journal":
        print(Style.BRIGHT + Fore.MAGENTA + "\n\t\tVENUE")

    print(Style.BRIGHT + Fore.BLACK + "\t\t\tTitle: " + Style.RESET_ALL + str(element["title"]), end="")
    if not str(element["title"]).endswith("\n"):
        print()
    if element['author']:
        print(Style.BRIGHT + Fore.BLACK + "\t\t\tAuthors: ", end="")
        authors = element["author"].split("\n")
        print(*(author for author in authors if author != ""), sep=", ", end="\n")
    if element["year"] != '':
        print(Style.BRIGHT + Fore.BLACK + "\t\t\tYear: " + Style.RESET_ALL + element['year'], end="")
    if element["pubtype"] in Parsing.publications:
        if element['journal'] != '' and element['volume'] != '':
            print(Style.BRIGHT + Fore.BLACK + "\t\t\tJournal: " + Style.RESET_ALL + element['journal'], end="")
            print(Style.BRIGHT + Fore.BLACK + "\t\t\tVolume: " + Style.RESET_ALL + element['volume'], end="")
    if "publisher" in element and element["publisher"] != "":
        print(Style.BRIGHT + Fore.BLACK + "\t\t\tPublisher: " + Style.RESET_ALL + element['publisher'], end="")
    print(Style.BRIGHT + Fore.BLACK + "\t\t\tType: " + Style.RESET_ALL + element['pubtype'])