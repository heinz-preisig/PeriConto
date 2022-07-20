##########::Instructions to use PERICONTO 0.1::####

A brief note about the name: The name PERICONTO has two parts: PERI+ CONTO. 
PERI stands for a term related to Indian Yellow, 
a mysterious transluscnet paint ingredient used untill 19th century (https://en.wikipedia.org/wiki/Indian_yellow).
CONTO stands for coating ontologies.





# how to use PERICONTO_0.1 (instructions to run the program are based on LiNUX OS, the user can adapt them as per her/his OS)

    #The program has been tested on Ubuntu 18.04 with the the Python3.8.5 and the latest Python version Python3.10. Under Python 3.10, an error relatd to Qt plateform plugin 'xcb' occured, which was resolved by installing libxcb-xinerama0 ($sudo apt-get install libxcb-xinerama0)

    STEP-1: Go to the directory PERICONTO_0.1 and create a virtual invironment as following 
        $ python3 -m venv .venv
        $ source .venv/bin/activate
    STEP-2: Install dependencies (there was an unresolvable error with the package PyQtWebEngine,tested in Python 3.6)
        $ pip3 install -r requirements.txt ()

    STEP-3: launch the peroconto GUI
        $ python3 ontobuild.py


# Information about directories
    #PERICONTO_0.1/src contains the main source code:
    # module ontobuild.py is the main module that should be run (python3 ontobuild.py) to launch the PERICONTO user interface
    # visualizaton user interface can be opened from the perconto ui or it can independently launched by running the script (pythons ontovis.py)
    # Currently, the ontovis is set to deafult (nx.html, which is converted from a ontology in a turtle format)  



        periconto_0.1
        ├── coatingOntology
        │   ├── cfo_ver01.ttl
        │   └── cfo_ver01.txt
        ├── nx.html
        ├── README.md
        └── src
            ├── graph.py
            ├── ontobuild.py
            ├── ontologybuilder_gui.py
            ├── ontologybuilder_gui.ui
            ├── ontovis.py
            └── requirements.txt




# What one can do with the periconto?

  Currently it allows:
         1. load an existing ontlogy (select 'load ontology' option from the dropdown list)
         2. chose an existing sample ontology (cfo_ver01.txt). Currently the tool takes only a text file where ontology triples are listed per line
                # one can edit the tree, f.ex, select nodes and add classes and subclasses 
                # adding a class is only possible by selecting the ontology root node (cfo). 
                # However in the knowledge graph these are actually subclasses of the root 'cfo'.
                # Once done with editing, the user can save the current ontology by selecting 'save ontology' from the dropdown list of select options.
                # Closing the application will also promt user to save the changes to a new file or to the existing file.

                # Currently, remove node option is disbale. There was some issue when the class nodes were selected for removing; It working fine with removing child nodes (#TODO).
                #

         3. create ontology (select 'create ontology' option from the dropdown list of select options)
                # the user can create the class-subclass strucure. In create mode, ontology tree starts with a default root node named as 'cfo'.
                #TODO: the idea is to keep the ontology tree view as class-subclass and allow user to edit other relations for example, between a 
                 child node of one class to another class (relatesTo or any other relation). This is immediatedly written into the ontology knowledge graph 
                  and the nested dictioanry, so this is also available for visualization. I think we may not neccessarily need to make the tree view crowded.
                
         3. Save ontology

         4. visualize ontology
              # launches a new GUI, 'ontovis.
              # TODO (EASY) to add more features into it; 
              # TDO (Relatively DIFICULT) to embed ontovis GUI inside the PERICONTO main GUI. This could be very helpful
               to see the chnages dyanmically while editing the ontology or analyzing it. In the long term one can make the ontology visual view interactive!
