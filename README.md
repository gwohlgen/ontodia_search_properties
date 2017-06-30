# ontodia_search_properties

Here you find the code to get **suggestions on properties** related to an entity in Wikidata -- based on a user search term.
It has so far only been tested with Wikidata, but an adaption to other data sets should be straightforward.

## Main parts:

a) To create a model use script `1_do_all_preprocessing.py`

b) To get suggestions for a user input, see script `get_similar_properties.py`

There are also scripts included for clustering properties, and for evaluating the system against predefined
aliases ("also known as") as a gold standard.

