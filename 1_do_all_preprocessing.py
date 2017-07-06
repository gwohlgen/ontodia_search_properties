import json,sys
import helpers, config
from pprint import pprint

"""
    this does the necessary proprocessing for a given properties file and a word embeddings non-binary model (.vec)
    if you use a new model -- edit the config file
"""

print "\n\n***** Step 0: CURRENTY YOU ARE EXPECTED TO TRIM THE MODEL TO THE DESIRED SIZE BEFORE STARTING"
print "Model being build for", config.MODELFN

print "\n\n***** Step 1: create aliases -- labels mapping and write to a file -----"
properties = helpers.get_properties_by_id(config.PROPS_FILE)
helpers.sample_output_properties(properties)

# create the mapping of aliases to labels
alias_label_map = helpers.create_alias_label_map(properties, skip_ids=False) # here we want to keep all IDs, we can filter later  
json.dump(alias_label_map, open(config.P_ALIAS_MAP,"wb"))


sys.exit()

### ------------ Step 2

print "\n\n***** Step 2a .. create the list of all words used in labels" 
words_list = helpers.get_all_property_label_unigrams(properties) 

print "\n\n***** Step 2b ..  make a small model with only the words from words_list"
helpers.filter_big_model_label_words(words_list)

print "\n\n***** Step 2c ..  finally create the vectors for the property labels"
helpers.create_average_property_vectors()

print """\n\n***** Step 2d .. Concat the main model with the %s file and update the number of vectors in the file metadata!!!
""" % (config.EMB_PROP_LABELS,)
helpers.create_concat_model()


