import config, helpers,pickle
import evaluation.tools
from pprint import pprint


def do_evaluation(skip_ids=False, skip_where_alias_same_as_label=False):
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


    print "\n\n############### (2) .. compute similarity of aliases with word embeddings ################################"
    for alias, label in alias_labels_map.iteritems():

        # format: alias is a string, label is a list of strings
        close_props = helpers.get_closest_properties(alias, model, [], w2v_plist, properties, debug_lookup=False, num_sugg = 100)

        if close_props:
            num_found += 1
            # helpers.pprint_closest_properties(alias + " -- label: " + str(label), close_props, properties)
            eval_data[alias] = (label, close_props) 
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
 
    fn = config.BASEPATH + "evaluation/eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
    fn2 = config.BASEPATH + "evaluation/eval_res.%s.skip-ids.%s.use_descr_text.%s.skip_alias_same_as_label.%s.pickle" % (
        config.MODELFN, str(skip_ids), config.USE_DESCR_IN_PROP_VECTORS, str(skip_where_alias_same_as_label)) 
 
    with open(fn, 'wt') as out:
        pprint(eval_res, stream=out)
    pickle.dump( eval_res, open(fn2,'wb') )


if __name__=="__main__":


    do_evaluation()
