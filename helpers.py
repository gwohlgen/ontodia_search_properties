import sys, json, codecs, subprocess, string
import numpy as np
import config
import nltk
from nltk.corpus import stopwords
from gensim.models import KeyedVectors
from operator import itemgetter

nltk.download('stopwords')
stop = set(stopwords.words('english'))

def get_properties_by_id(props_file):
    """
        takes the properties json file from https://tools.wmflabs.org/hay/propbrowse/
        and parses it into a more convenient data structure for usage
        currently we only take the fields we need from the file
    """
    properties = {}

    # (1) -- read in labels and do stopword removal 
    with open(props_file) as data_file:
        data = json.load(data_file)

        labels_words = {}

        for d in data:
            id = d['id']
            properties[id] = {}

            stop_free_label = [i.lower() for i in d["label"].split() if i not in stop]
            try:
                stop_free_descr = [i.lower() for i in d["description"].split() if i not in stop]
            except:
                pass
                #print "could not split description text which is:", d["description"]

            if config.USE_DESCR_IN_PROP_VECTORS:
                properties[id]["label_words"] = stop_free_label + stop_free_descr
            else:
                properties[id]["label_words"] = stop_free_label 

            properties[id]["label"] = d['label']
            properties[id]["description"] = d['description']
            properties[id]["aliases"] = d['aliases']

    return properties


def create_alias_label_map(properties, skip_ids=False, lower=True):
    """
        create mapping from "alias" --> "label" for all our wikidata properties
    """
    alias_label_map = {}
    for propid, pvals in properties.iteritems():

        if skip_ids:
            if pvals['label'].find("ID") >= 0 or pvals['label'].find(" id") >= 0:
                continue

        for alias in pvals['aliases']:
            if lower: 
                alias = alias.lower()

            if alias_label_map.has_key(alias):
                alias_label_map[alias].append( (pvals['label'], propid) )
            else:
                alias_label_map[alias] = [ (pvals['label'], propid) ]

            # tmp!!
            if alias == alias_label_map[alias][0][0]:
                print "INFO: alias == label", alias, alias_label_map[alias], "... looks like this is a \"bug\" in WikiData."

    return alias_label_map


def create_property_aliases(properties, skip_ids=False, lower=True):
    """
        similar to create_alias_label_map .. but here we look for a mapping "PROP_ID" --> list of aliases
    """
    property_aliases = {}
    for propid, pvals in properties.iteritems():

        if skip_ids: # skip properties with "ID" in their label (as they might be not important for the user)
            if pvals['label'].find("ID") >= 0 or pvals['label'].find(" id") >= 0:
                continue

        aliases = pvals['aliases']
        if lower: # make aliases lowercase?
            aliases = [alias.lower() for alias in aliases] 

        if aliases:
            property_aliases[propid] = aliases

    return property_aliases





def get_all_property_label_unigrams(properties):
    # create a list of words from all our property labels

    words_set = set()

    for id,pvals in properties.iteritems():
        [words_set.add( word ) for word in pvals["label_words"]]

    print "Number of unique words in the property labels:", len(words_set)
    return list(words_set)

def line_prepender(filename, line):
    """ write a line at the beginning of a file """
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)



def filter_big_model_label_words(property_words):

    ofh = open(config.EMB_FILTERED_TERMS,'wb')

    # open embedding vectors and only keep the ones matching one of the property terms
    numlines = 0
    with open(config.EMB_BIGFILE) as data_file:
        for line in data_file:
            term = line.split(" ")[0]

            if term in property_words:
                #print "match found", term
                ofh.write(line)
                numlines += 1

    ofh.close()
    print "DONE\nNow adding a metadata line in vectors file (num_terms, num_dimensions)"
    line_prepender(config.EMB_FILTERED_TERMS, "%s %s" % (numlines, config.DIMS))



def create_average_property_vectors():
    """
        this creates the representative average vectors for every property and write them
    """
    # load the model of filtered terms  
    model = KeyedVectors.load_word2vec_format(config.EMB_FILTERED_TERMS) # all lowercase
    index2word_set = set(model.index2word)
    ofh = codecs.open(config.EMB_PROP_LABELS,'wb','utf-8')

    properties = get_properties_by_id(config.PROPS_FILE)

    for propid, vals in properties.iteritems():
        
        # create avg vector -- (a) init vector
        featureVec = np.zeros((config.DIMS,),dtype="float32")   

        # collect the vectors for the words in the label
        nwords = 0.
        for word in vals['label_words']: # all lowercase
            if word in index2word_set: 
                print "word found:", word, model[word][0:5]
                nwords = nwords + 1.
                featureVec = np.add(featureVec,model[word])
            else:
                print "word not found:", word, vals['label']
     
        # Divide the result by the number of words to get the average
        featureVec = np.divide(featureVec,nwords)

        # write the average vector to the file 
        print "Average Vec:", featureVec[0:5]
        vecstr= " ".join([str(x) for x in featureVec.tolist()])
        row = propid + " " + vecstr + "\n"
        ofh.write(row)


def create_concat_model():
    """
        create the concated model (trained word embeddings + model of Property embeddings
    """

    print "\t a) copy model to final file:", config.EMB_OUR_MODEL
    subprocess.call(["/bin/cp", config.EMB_BIGFILE, config.EMB_OUR_MODEL])

    print "\t b) adding our property vectors from file:", config.EMB_PROP_LABELS
    subprocess.call("/bin/cat %s >> %s " % (config.EMB_PROP_LABELS,config.EMB_OUR_MODEL), shell=True)

    print "\t c) check if we have a metadata line already, if yes delete it"
    with open(config.EMB_OUR_MODEL) as data_file:
        for line in data_file:
            num_ele = len(line.split(" "))
            if num_ele == 2:
                print "\t\t header found .. need to delete first line from file", config.EMB_OUR_MODEL
                subprocess.call("/usr/bin/tail -n +2 %s > /tmp/abcd77" % (config.EMB_OUR_MODEL), shell=True)
                subprocess.call(["/bin/mv", "/tmp/abcd77", config.EMB_OUR_MODEL])
                print "CHECK THAT IT WORKED!"
                #sys.exit()
            else:
                print "\t\t **** NO header found .. fine ***" 
            break

    print "\t c) count number of lines in file", config.EMB_OUR_MODEL
    wc_call_out =  subprocess.check_output("/usr/bin/wc %s" % (config.EMB_OUR_MODEL,), stderr=subprocess.STDOUT, shell=True).strip()
    num_lines = wc_call_out.split(" ")[0]

    print "\t d) Finally, prepend a line with (num_lines DIMS) to our model:", config.EMB_OUR_MODEL
    line_prepender(config.EMB_OUR_MODEL, "%s %s" % (num_lines, config.DIMS))
    print "\t DONE"



   



def load_model_and_plist():
    """
        used in scripts to finally compute the similary vals between terms and WD Properties

        this just loads our model (with emb word + our property vectors) into memory
        and it also returns a list of all available properties in our model
    """

    #model = KeyedVectors.load_word2vec_format(config.EMB_PROP_LABELS)
    print "Will load the model now:", config.EMB_OUR_MODEL
    model = KeyedVectors.load_word2vec_format(config.EMB_OUR_MODEL)

    plist = []
    for i in xrange(0,10000):
        try:
            prop = "P"+str(i)
            model[prop]
            plist.append(prop)
        except KeyError:
            pass
    print "Done loading the model:", config.EMB_OUR_MODEL
    return model, plist



# find all property ids:
def get_closest_properties(term, model, instance_properties, w2v_plist, properties, lower=True, debug_lookup=False, num_sugg=config.NUM_SUGG_PROPS, add_alias_terms_to_result=False, property_aliases=None):
    """ @param term: a term from the user (term), the instances of the respective entity (instance_properties)
               term should be unicode (preferred) or utf-8 string
        @param w2v_plist: the list of properties in the model (w2v_plist), our properties dict
        @param instance_properties: a list of properities for the instance -- if left empty then we match against ALL properties
               instance_properties can be a list of strings or list of unicode -- both works
        @param properties: just for debugging, not needed in the production version 
        @param add_alias_terms_to_result: additionally to the word embedding-based results, also matches in the aliases (Wikidata: also known as) into the matches
        @param property_aliases: mapping of properties to list of its aliases, needed when add_alias_terms_to_result == True

        returns: the properties most similar to the input term
    """
    sims, words = [], []

    # the term should be unicode, if not, try to decode it (assuming it is utf-8)
    if type(term) == type(""):
        term = term.decode("utf-8")

    if lower:
        term = term.lower()


    # check if we find the words(s) in the model
    for word in term.split(" "): 
        # remove all non-alphanumeric chars from the words -- as those are also not in our embedding models
        word = filter(unicode.isalnum, word) 

        if model.vocab.has_key(word) and word not in stop:
            words.append(word)

    try:
        print "INFO: words used from input phrase (%s): %s" % ( term.encode("utf-8"), str([w.encode("utf-8") for w in words]) )
    except:
        print "encoding error on input term"

    alias_sims = []
    if add_alias_terms_to_result:
        alias_sims = match_in_aliases(term, instance_properties, property_aliases)

    if len(words) == 0:
        print "WARN: Term -- %s -- (or it's parts) not found in the model!. We have no suggestions from word embeddings!" % (term.encode("utf-8"),)
        return alias_sims 

    if instance_properties:
        # only check for given instance_properties
        for propid in instance_properties:
            if not propid in w2v_plist:
                print "propid " + propid + "not in w2v_plist"
                continue
            sim = model.n_similarity(words, [propid])
            if not str(sim) == "nan":
                sims.append((propid,sim))
    else:
        # check for all properties in w2v_plist 
        for propid in w2v_plist:
            sim = model.n_similarity(words, [propid])
            if not str(sim) == "nan":
                sims.append((propid,sim))

    sorted_sims = sorted(sims,key=itemgetter(1))
    sorted_sims.reverse()
    if debug_lookup:
        for i in sorted_sims[:num_sugg]:
            print "\t", properties[i[0]]['label'], i[1]


    return alias_sims + sorted_sims[:num_sugg]

def match_in_aliases(term, instance_properties, property_aliases):
    """
        -- for all parameters see in the outer function: get_closest_properties
        @param term 
        @param instance_properties
        @param property_aliases

        here we look for matches of user input "term" in the aliases of 
        instance properties. if a match is found, we add the instance property to the result set
    """

    ## list of matches in alias strings of the properties
    alias_sims = []

    
    for ip in instance_properties:
        if property_aliases.has_key(ip): 
            aliases = property_aliases[ip]
            found = False
            for alias in aliases: 
                if alias.find(term)>=0:
                    #print alias
                    found = True 
            if found: 
                alias_sims.append( (ip,1.0) )
                
    return alias_sims



def pprint_closest_properties(term, close_props, properties):
    """ just pretty print the term and the suggested properties """

    print "\nTerm:", term
    # input: [(u'P434', 0.3667969984041744), (u'P373', 0.36222223691644562), ... ]
    for cp in close_props:
        label = properties[cp[0]]['label']
        print "\t\t", label, "\t\t", cp[1] 





def sample_output_properties(properties):
    """
        unimportant debugging/testing function
    """
    print "TEST:"
    print "\tLabel:\t\t", properties['P569']['label']
    print "\tAliases:\t", properties['P569']['aliases']

    print "\nTEST2:"
    print "\tLabel:\t\t", properties['P26']['label']
    print "\tAliases:\t", properties['P26']['aliases']

if __name__ == "__main__":

    from config import PROPS_FILE
    properties = get_properties_by_id(PROPS_FILE)
    property_aliases = create_property_aliases(properties)

    print "Number of properties:", len( properties ) 

    num_alias_all      = len(create_alias_label_map(properties, skip_ids=False))
    num_alias_skip_ids = len(create_alias_label_map(properties, skip_ids=True))
    print "Number of aliases (incl ids):", num_alias_all 
    print "Number of aliases (skip ids):", num_alias_skip_ids 
    print "Number of IDs in aliases:",     num_alias_all - num_alias_skip_ids


    pprint_closest_properties("test term", [(u'P434', 0.3667969984041744), (u'P373', 0.36222223691644562)], get_properties_by_id(PROPS_FILE))
   
    print 
    #create_concat_model()

