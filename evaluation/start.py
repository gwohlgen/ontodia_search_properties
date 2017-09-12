import config, helpers,pickle
import evaluation.tools
from pprint import pprint


def do_evaluation(skip_ids=False, skip_where_alias_same_as_label=False, entities=False, skip_nums=False, lower=None, MAX_EVAL_NUM=None, classic_search=False, classic_mode=""):
    """ call the evaluation process
        
        params: 
            with_ids ... you can skip labels that contain "ID" or " id" as they may not be so interesting
    """
    
    print "\n\n############### (1) .. setup and initalize ... ################################"

    if entities:
        ## we misleadingly call it properties here .. to not have to change too much code
        properties = helpers.get_entities_by_id(config.PICKLED_ENTITIES)
    else:
        properties = helpers.get_properties_by_id(config.PROPS_FILE)

    alias_labels_map = helpers.create_alias_label_map(properties, skip_ids=skip_ids, skip_nums=skip_nums)

    if not classic_search:
        print "     now loading the model"
        model, w2v_plist = helpers.load_model_and_plist(entities=entities)


    num_found, num_not_found = 0, 0
    eval_data = {} # here we will collect the data to be evaluated


    print "\n\n############### (2) .. compute similarity of aliases with word embeddings ################################"
    for alias, label_data in alias_labels_map.iteritems():

        # format: alias is a string, label is a list of strings
        if entities:
            if classic_search:
                close_props = helpers.get_classic_search_res(alias, properties, lower=lower, num_sugg=100, add_alias_terms_to_result=False, classic_mode=classic_mode)
            else:
                close_props = helpers.get_closest_entities(alias, model, lower=lower, num_sugg=100, add_alias_terms_to_result=False)
        else:
            close_props = helpers.get_closest_properties(alias, model, [], w2v_plist, properties, debug_lookup=False, num_sugg = 100)


        if close_props:
            num_found += 1
            eval_data[alias] = (label_data, close_props) 
        else:
            num_not_found += 1
            print "Nothing found for alias:", alias, num_found, num_not_found

        if MAX_EVAL_NUM and (num_found + num_not_found) > MAX_EVAL_NUM: 
            break

    #import pickle; pickle.dump(eval_data, open("test_eval.pickle","wb"))


    print "\n\n############### (3) get all the eval results / metrics ################################"
    eval_res = evaluation.tools.get_metrics(eval_data, properties=properties)

    # add some more data into the eval results
    eval_res['num_found'] = ("Number aliases found in model", num_found)
    eval_res['num_not_found'] = ("Number aliases NOT found in model", num_not_found)
    eval_res['settings'] = {'skip_ids': skip_ids, 'skip_where_alias_same_as_label': skip_where_alias_same_as_label,
                            'model': config.EMB_OUR_MODEL, 'use_descr_in_emb':config.USE_DESCR_IN_PROP_VECTORS}

    print "\n\n############### (4) log EVALUATION RESULTS to console and to a file ################################"
    pprint (eval_res)
 
    fn = config.BASEPATH + "evaluation/eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
    fn2 = config.BASEPATH + "evaluation/eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s.pickle" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
 
    with open(fn, 'wt') as out:
        pprint(eval_res, stream=out)
    pickle.dump( eval_res, open(fn2,'wb') )


if __name__=="__main__":
        
    ### for properties
    #do_evaluation(skip_ids=False)
    #do_evaluation(skip_ids=True)

    ### for entities
    #do_evaluation(skip_ids=False, entities=True, skip_nums=True, lower=True, MAX_EVAL_NUM=10000)
    #do_evaluation(skip_ids=False, entities=True, skip_nums=True, lower=True, MAX_EVAL_NUM=20000, classic_search=True)
    do_evaluation(skip_ids=False, entities=True, skip_nums=True, lower=True, MAX_EVAL_NUM=20000, classic_search=True, classic_mode='complex')

        
