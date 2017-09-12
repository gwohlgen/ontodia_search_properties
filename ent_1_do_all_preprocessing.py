import json,sys,time
import helpers, config
from pprint import pprint

"""
    this does the necessary proprocessing for a given properties file and a word embeddings non-binary model (.vec)
    if you use a new model -- edit the config file
"""

#new: you can called it with a mode (properties (default) or entities)

print "\n\n***** Step 0: CURRENTY YOU ARE EXPECTED TO TRIM THE MODEL TO THE DESIRED SIZE BEFORE STARTING", time.asctime()
print "Model being build for", config.MODELFN

print "\n\n***** Step 1: create aliases -- labels mapping and write to a file -----", time.asctime()
entities = helpers.get_entities_by_id(config.PICKLED_ENTITIES)
helpers.sample_output_entities(entities)




# create the mapping of aliases to labels
alias_label_map = helpers.create_alias_label_map(entities, skip_ids=True, skip_nums=True) # here we want to keep all IDs, we can filter later  
json.dump(alias_label_map, open(config.E_ALIAS_MAP,"wb"))

sys.exit()

### ------------ Step 2

print "\n\n***** Step 2a .. create the list of all words used in labels", time.asctime()
words_list = helpers.get_all_property_label_unigrams(entities) 

print "\n\n***** Step 2b ..  make a small model with only the words from words_list", time.asctime()
helpers.filter_big_model_label_words(words_list, entities=True)


print "\n\n***** Step 2c ..  finally create the vectors for the property labels", time.asctime()
helpers.create_average_property_vectors(entities)


print """\n\n***** Step 2d .. Concat the main model with the %s file and update the number of vectors in the file metadata!!!
""" % (config.EMB_PROP_LABELS+'entities',)
helpers.create_concat_model(entities=True)
print "\n\n***** FINISHED", time.asctime()

