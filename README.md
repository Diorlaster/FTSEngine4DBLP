### ABOUT FTSE-4-DBLP 

FTSE-4-DBLP is a full-text search engine for DBLP developed in Python by Angelo Di Franco and Francesco Franco. 
It uses Sax to parse the dblp XML file and Whoosh to query, search and rank the elements.

### REQUIREMENTS 

Interpreter:

    Python 3.6 or higher 

The following pip packages are required:
 
    colorama==0.4.3
    psutil==5.6.7
    Whoosh==2.7.4

You can run the following command:

    pip3 install -r requirements.txt 

### RUN FTSE-4-DBLP 

When requirements have been installed successfully, run the following command from FTSE4DBLP main directory:

    main.py 
    
### XML AND INDEXING 
    
If indexes cannot be found or loaded, FTSE4DBLP will ask you for a valid XML file path. 
For example, you can place del dblp.xml file ( and its .dtd file ) inside the "XML" directory and digit
    
    XML/dblp.xml
    
If the XML is well-formed, FTSE4DBLP will start parsing and indexing the file. 

The XML dump can be found at the following url: 

    https://dblp.uni-trier.de/xml/
    
REMEMBER: you need to put .xml and .dtd ( with the same name ) files in the same directory!

### FTSE-4-DBLP QUERY SYNTAX 

Research in FTSE-4-DBLP follow some simple rules.

You can search:
	single words with a keyword-query which is a alphanumeric character sequence delimited by spaces
	phrases with a phrase-query which is a sequence of keywords delimited by " ( double quote )

You can search a word or a phrase among specific elements and/or fields as follow:

	[element].[field]:[keyword/phrase]

You don't have to specify both! For example, you can look for the keyword information among the field title of every 
element by typing 

    title:information 
    
or for the phrase "information retrieval" among a specific element but among every field by typing 

    article."information retrieval" 
    
or 

    article:"information retrieval".

As you can see, when you are not specifying a field you can both use . or : to specify an element because FTSE-4-DBLP 
is smart enough to understand when you do specify an element or a field and when you don't.

But what do we mean with elements and fields?

DBLP provides two big type of data: publications and venues.
Each one has elements ( such as article for publications and book for venues ) each of which has fields but you can 
only specify some of them!

As publication elements, you can use 

    article incollection inproceedings phdthesis mastersthesis 
    
and a special one: 

    publication 
    
which is used to specify that you are looking for a publication with a generic element.

As venue elements you can only use the special element 

    venue 
    
to specify that you are looking for a venue.

As publication fields, you can use 

    author title year

As venues fields, you can use 

    title publisher

If an element is not specified, FTSE-4-DBLP will search among every element.

If a field is not specified, FTSE-4-DBLP will search among every field of every element ( if element is not specified )

So, in short:

		f-t-s : ([field:] search-pattern)+
		search-pattern : keyword | “phase”
		field: pub-search | venue-search
		pub-search : pub-ele[.pub-field]
		pub-ele: publication | article | incollection | inproc | phThesis | masterThesis
		pub-field: author | title | year
		venue-search: venue[.venue-field]
		venue-field: title | publisher

We did our best to prevent failures or unexpected behavior so FTSE-4-DBLP will show some warnings ( if enabled ) when 
you don't follow these rules but, as everything, is not perfect so you may get unwanted or unoptimized results if you 
type something strange.

### FAQS 

We added some hints inside the FAQ menu where you can find infos about research, warnings and ranking models.

### RANKING MODELS 

FTSE-4-DBLP provides two different ranking models for your results: Okapi BM25F and Frequency.

Okapi BM25F is a modified version of Okapi BM25 and the default Whoosh ranking model. 
It has an extension to multiple weighted fields and, unlike BM25, is applicable to structured documents consisting of multiple fields. The model
preserves term frequency non-linearity and removes the independence assumption between same term occurrences.

Frequency ranking estimate the relevance of documents to a given search query by counting its occurrences: the higher 
the number, the higher the score.

To combine publications and venues score when both are in the results set, FTSE-4-DBLP use the Threshold Algorithm. 
More infos can be found in the following paper: 
    
    R. Fagin, A. Lotem and M. Naor, Optimal aggregation algorithms for middleware, Journal of Computer and System 
    Sciences 66, p. 614-656, 2003

### DEVELOPMENT AND TESTING 

FTSE-4-DBLP has been developed on PyCharm IDE, using Python 3.6 on a Windows 10 Home machine. 

It has been tested on Windows 10 Home, Ubuntu 18.10 and macOS Mojave. 

Parsing and indexing process required at most 62 minutes on mid-range performance machine. This value may value a lot 
depending on the machine specs. 

Research function as been tested with many different queries and critical points of failure have been handled.

FTSE-4-DBLP gives its best when used on a SSD. Researches required time may vary A LOT if you use an HDD.