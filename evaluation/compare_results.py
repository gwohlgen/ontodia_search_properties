import pickle, pprint, sys, re
from operator import itemgetter
from os import listdir
from os.path import isfile, join
import config

mypath = config.BASEPATH+"evaluation/"


def load_results(debug_log=False):
    """
        just load all the evaluation results from the pickle files into the all_data variable
        @returns all_data
    """
    picklefiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('pickle')]
    if debug_log: pprint.pprint(picklefiles)
    all_data = {}

    for f in picklefiles:

        eval_res = pickle.load(open( config.BASEPATH+"evaluation/"+f))
        if debug_log: print eval_res

        for metric, metric_val in eval_res.iteritems():
            if all_data.has_key(metric):
                all_data[metric].append( (f, metric_val) )
            else:
                all_data[metric] = []
                all_data[metric].append( (f, metric_val) )

    return all_data


def pprint_results(all_data, debug=False):
    """ just pretty print the all_data var"""

    for metric, vals in all_data.iteritems():
        if debug: print "\n\nMETRIC:", metric
        sorted_vals = sorted(vals,key=itemgetter(1))
        sorted_vals.reverse()
        if debug: pprint.pprint(sorted_vals)
        print "\n\nMetric:", metric
        pprint.pprint(sorted_vals)



def evaluate_feature(all_data, feature=None, fixed=None, debug=False):
    """
        evaluate the results for a specific feature,
        which other features "fixed" (given)
    """
    print "\nNEW CALL to evaluate_feature for feature:", feature, " -- fixed:", fixed

    results = {}       
 
    for metric, vals in all_data.iteritems():
        results[metric]={}
        if debug: print "\n\nMETRIC:", metric

        if metric == "settings": continue

        for corpus in config.CORPORA_TO_EVAL:
            results[metric][corpus]={}

            local_result = {}
            if debug: print corpus
            for val in vals: 
                if debug: print val
                if type(val[1]) == type(()): continue

               
                # look for a specific corpus which we matches our input features -- and then collect the results 
                if val[0].find(corpus)>0 and val[0].find(fixed)>0:
                    if val[0].find(feature+".True")>0:
                        if debug: print "TTTTT", val
                        results[metric][corpus]["True"] = val[1]
                    if val[0].find(feature+".False")>0:
                        if debug: print "FFFFF", val
                        results[metric][corpus]["False"] = val[1]

        # and now aggrate the results
        results[metric]["winner_true"], results[metric]["winner_false"], results[metric]["true-false"] = 0, 0, 0.0
        for corpus in config.CORPORA_TO_EVAL:   
            if debug: print corpus, metric 
            if debug: print results[metric][corpus]

            if metric.startswith("n"): continue

            if debug: print results[metric][corpus]["True"]
            if results[metric][corpus]["True"] >= results[metric][corpus]["False"]:
                results[metric]["winner_true"] += 1                
            if results[metric][corpus]["True"] <= results[metric][corpus]["False"]:
                results[metric]["winner_false"] += 1                

            diff = results[metric][corpus]["True"] - results[metric][corpus]["False"]
            results[metric]["true-false"] += diff 
        num_res = results[metric]["winner_false"] + results[metric]["winner_true"]
        if num_res: results[metric]["true-false-avg"] = results[metric]["true-false"] / num_res

    #pprint.pprint(results["AVP"])
    pprint.pprint(results)

#lexvec.enwiki+newscrawl.300d.W.pos.vectors.*(skip-ids)(.*) 
#lexvec.enwiki+newscrawl.300d.W.pos.vectors.small.10000.lines.skip-ids.True.use_descr_text.False.skip_alias_same_as_label.False.pickle

all_data = load_results(debug_log=False)
pprint_results(all_data)

#evaluate_feature(all_data, feature="skip-ids", fixed="use_descr_text.False", debug=False)
#evaluate_feature(all_data, feature="skip-ids", fixed="use_descr_text.True")
evaluate_feature(all_data, feature="use_descr_text", fixed="skip-ids.True",debug=True)
#evaluate_feature(all_data, feature="use_descr_text", fixed="skip-ids.Fals")

