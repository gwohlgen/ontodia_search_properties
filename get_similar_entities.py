import sys,json,pickle
import helpers,config
import timeit
from helpers import match_in_entity_aliases

def inititalize_get_similar_entities():
    model, xxx = helpers.load_model_and_plist(entities=True)
    return model



if __name__ == "__main__":

    DEBUG=True
    TEST_TERMS = ["tennis", "Wembley", "stadium", "Wembley Stadium"]


    ############# match_in_entity_aliases ################      

    print "\n\nLoading aliases from file:", config.E_ALIAS_MAP
    aliases = json.load(open(config.E_ALIAS_MAP))   # load alias file


    print "\n\n\n START: match_in_entity_aliases\n"

    for term in TEST_TERMS:
        start_time = timeit.default_timer() 
        print match_in_entity_aliases(term, aliases, debug=DEBUG)
        print "\nTime for the match_in_entity_aliases queries for term: ", term, " --- ", timeit.default_timer() - start_time   

    print "\n\nNumber of Aliases", len(aliases)


    ############## load and test embeddings model ############################
    start_time = timeit.default_timer()
    model = inititalize_get_similar_entities()
    print "\n\nTime for LOADING the model", timeit.default_timer() - start_time

    #### sample queries #####
    res = {}
    for term in TEST_TERMS:
        start_time = timeit.default_timer() 
        res[term] = helpers.get_closest_entities(term, model, lower=True, num_sugg=config.NUM_SUGG_PROPS, add_alias_terms_to_result=False, entity_aliases=None)
        print "\n\nTime for model query for term:", term, " --- ", timeit.default_timer() - start_time


    # --------------------------------------------------------------------------------- 
    ## only for debugging
    if DEBUG:
        our_entities = pickle.load(open(config.PICKLED_ENTITIES))

        def view_res(res, ents):
            print '\n\nsee_res called!'
            for row in res:
                print row[0], ents[row[0]], row[1]

        ### view the results
        [ view_res(res[term], our_entities) for term in TEST_TERMS ]

