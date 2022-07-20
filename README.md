##########::Instructions to use PERICONTO 0.2::####

Authors:
    Vinay Gautam
    Heinz A Preisig



A brief note about the name: The name PERICONTO has two parts: PERI+ CONTO. 
PERI stands for a term related to Indian Yellow, 
a mysterious transluscnet paint ingredient used untill 19th century (https://en.wikipedia.org/wiki/Indian_yellow).
CONTO stands for coating ontologies.




# how to use PERICONTO_0.2 
    instructions to run the program are based on LiNUX OS, the user can adapt them the used OS

    The program has been tested on Ubuntu 18.04 & 20.04 
        with the the Python3.8.5 python3.8.10 and the latest Python version Python3.10. 
    Under Python 3.10, an error relatd to Qt plateform plugin 'xcb' occured, 
        which was resolved by installing libxcb-xinerama0 ($sudo apt-get install libxcb-xinerama0)

    1. make a project directory
    2. change to project directory
    3. create and activate a virtual invironment as following 
        $ python3 -m venv .venv
        $ source .venv/bin/activate
    4. Install dependencies (there was an unresolvable error with the package PyQtWebEngine,tested in Python 3.6)
        $ pip3 install -r requirements.txt ()
    5. launch the PeriConto's GUI
        $ python3 PeriConto.py


# Information about directories
    #PERICONTO_0.1/src contains the main source code:
    # module ontobuild.py is the main module that should be run (python3 ontobuild.py) to launch the PERICONTO user interface
    # visualizaton user interface can be opened from the perconto ui or it can independently launched by running the script (pythons ontovis.py)
    # Currently, the ontovis is set to deafult (nx.html, which is converted from a ontology in a turtle format)  



        periconto_0.1
        ├── ontologyRepository
        ├── nx.html
        ├── README.md
        └── src
            ├── PeriConto.py
            ├── PeriConto_gui.py
            ├── PeriConto_gui.ui
            ├── ontologybuilder_gui.ui
            ├── ontovis.py
            └── requirements.txt




# What one can do with the periconto?

    Currently it allows:
         1. load an existing ontlogy (select 'load ontology' option from the dropdown list)
            or create a new ontology -- it will ask for
            . file name
            . root identifier, a string
         2. chose an existing sample ontology. 
                Currently the tool takes only a json file
            one can:
                . add subclasses to a class
                . link a class to a subclass --> the subclass is implemented as a class
                    . either define a new class
                    . or choose an existing class
                . add a primitive to a class or a subclass
                    . primitives are integer, string, comment
                . sublcasses can be renamed (double click on name)

        4.  visualize ontology

        5.  currently not functional
              # launches a new GUI, 'ontovis.
              # TODO (EASY) to add more features into it; 
              # TDO (Relatively DIFICULT) to embed ontovis GUI inside the PERICONTO main GUI. This could be very helpful
               to see the chnages dyanmically while editing the ontology or analyzing it. In the long term one can make the ontology visual view interactive!
