
# You may have heard of Pylint that helps statically checking Python code. Few people know that it comes with a tool named Pyreverse that draws UML diagrams from the Python code it reads. Pyreverse uses Graphviz as a backend.

# It is used like this:

pyreverse -o png -p yourpackage .

# where the . can also be a single file.



# To analyse one specific file:

# $ pyreverse -o png -p myproject \path\to\myproject\myfile.py 



# cd into PeriConto

$ pyreverse -o png -p src src/PeriContoCoatedProductBackEnd.py





