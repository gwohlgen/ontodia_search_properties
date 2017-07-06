import helpers, config

def get_metrics(eval_data, debug=False):
    """ 
        we start with:
        AVP and Top 5%
    """
    all_ranks = []

    for alias, vals in eval_data.iteritems():

        label_data, close_props = vals
   
        # step 1 .. find rank 
        rank = get_rank(label_data, close_props, debug)
        if debug: print "alias (%s),\t label_data (%s),\t rank: %s" % (alias, label_data, rank)

        all_ranks.append(rank)

    eval_res = {} 
    eval_res['AVP']   = sum(all_ranks) / float(len(all_ranks))
    eval_res['MRR']   = sum( [1.0/rank for rank in all_ranks]) / float(len(all_ranks))
    eval_res['top1']  = perc_top_n(all_ranks, 1)
    eval_res['top2']  = perc_top_n(all_ranks, 2)
    eval_res['top3']  = perc_top_n(all_ranks, 3)
    eval_res['top5']  = perc_top_n(all_ranks, 5)
    eval_res['top10'] = perc_top_n(all_ranks, 10)
    eval_res['top20'] = perc_top_n(all_ranks, 20)
    eval_res['top50'] = perc_top_n(all_ranks, 50)
    return eval_res

def get_rank(label_data, close_props, debug=False):
    """
        label_data .. list of strings and propids (the real gold standard labels)
        close_props .. [(u'P434', 0.3667969984041744), (u'P373', 0.36222223691644562), ... ]       
    """ 
    properties = helpers.get_properties_by_id(config.PROPS_FILE)
    labels = [l[0] for l in label_data]

    default_rank = 150 # default if nothing found 
    n = 1
    for cp in close_props:
        try:
            cp_label = properties[cp[0]]['label']
        except KeyError, e:
            print "Fake property found", cp[0]
            continue

        if cp_label in labels: 
            if debug: print "\t\tFound:\t'", cp_label, "' - in -\t", labels
            return n # return current rank 
        n+=1 

    return default_rank 


 

def perc_top_n(all_ranks, top_n):
    num_inside = 0
    for rank in all_ranks:        
        if rank <= top_n:
            num_inside+=1

    return num_inside / float(len(all_ranks))


if __name__ == "__main__":
    import pickle
    eval_data = pickle.load(open("test_eval.pickle"))
    do_evaluation(eval_data, debug=False)
