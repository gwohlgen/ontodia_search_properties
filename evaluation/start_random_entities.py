import config, helpers,pickle
import evaluation.tools
from pprint import pprint
from random import randint


def do_evaluation(random_entities, skip_ids=False, skip_where_alias_same_as_label=False):
    """ call the evaluation process
        
        params: 
            with_ids ... you can skip labels that contain "ID" or " id" as they may not be so interesting
    """
    
    print "\n\n############### (1) .. setup and initalize ... ################################"
    properties = helpers.get_properties_by_id(config.PROPS_FILE)
    alias_labels_map = helpers.create_alias_label_map(properties, skip_ids=skip_ids)
    print "     now loading the model"
    model, w2v_plist = helpers.load_model_and_plist()

    num_found, num_not_found = 0, 0
    eval_data = {} # here we will collect the data to be evaluated

    for entity_key, entity_props in random_entities.iteritems():
    
        print "\n\n############### (2) .. compute similarity of aliases with word embeddings ################################"
        for alias, label_data in alias_labels_map.iteritems():
             
            # check if label used in this entities
            if not property_found_in_entity(entity_props, label_data):
                continue

            # format: alias is a string, label is a list of strings
            close_props = helpers.get_closest_properties(alias, model, entity_props, w2v_plist, properties, debug_lookup=False, num_sugg = 100)
            print close_props

            if close_props:
                num_found += 1
                # helpers.pprint_closest_properties(alias + " -- label: " + str(label), close_props, properties)
                eval_data[entity_key + '___' + alias] = (label_data, close_props) 
            else:
                num_not_found += 1
                print "Nothing found for alias:", alias

    #import pickle; pickle.dump(eval_data, open("test_eval.pickle","wb"))


    print "\n\n############### (3) get all the eval results / metrics ################################"
    eval_res = evaluation.tools.get_metrics(eval_data)

    # add some more data into the eval results
    eval_res['num_found'] = ("Number aliases found in model", num_found)
    eval_res['num_not_found'] = ("Number aliases NOT found in model", num_not_found)
    eval_res['settings'] = {'skip_ids': skip_ids, 'skip_where_alias_same_as_label': skip_where_alias_same_as_label,
                            'model': config.EMB_OUR_MODEL, 'use_descr_in_emb':config.USE_DESCR_IN_PROP_VECTORS}

    print "\n\n############### (4) log EVALUATION RESULTS to console and to a file ################################"
    pprint (eval_res)
 
    fn = config.BASEPATH +  "evaluation/RANDOM.eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
    fn2 = config.BASEPATH + "evaluation/RANDOM.eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s.pickle" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
 
    with open(fn, 'wt') as out:
        pprint(eval_res, stream=out)
    pickle.dump( eval_res, open(fn2,'wb') )

def property_found_in_entity(entity_props, label_data):
    props = [d[1] for d in label_data]

    for prop in props:
        if prop in entity_props:
            print "found", prop, entity_props
            return True

    return False
    

def get_random_entities(num=3000):
    all_entities = pickle.load(open(config.PICKLED_ENTITIES))
    random_entities = {}

    # take from the first 10000 entities in Wikidata
    for x in range(0, num):
        id = "Q" + str(randint(0, 10000))
        try:
            random_entities[id] = all_entities[id]
        except KeyError:
            #print "ID not found", id
            pass
   
    print "Number of random_entities", len(random_entities)
    return random_entities

def stats_avg_num_properties(random_entities):

    avg_num = sum ( [len(v) for k,v in random_entities.iteritems()] ) / float(len(random_entities))
    print "Average number of properties per random entity:", avg_num


if __name__=="__main__":

    # TODO .. get_random_entities function
    random_entities = get_random_entities()

    print stats_avg_num_properties(random_entities)

    do_evaluation(random_entities,skip_ids=True)
