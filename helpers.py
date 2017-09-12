import sys, json, codecs, subprocess, string, pickle, re
import numpy as np
import config
import nltk
from nltk.corpus import stopwords
from gensim.models import KeyedVectors
from operator import itemgetter
from config import DEBUG

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

def get_entities_by_id(ent_file):
    return pickle.load(open(ent_file))


def create_alias_label_map(properties, skip_ids=False, lower=True, skip_nums=False):
    """
        create mapping from "alias" --> "label" for all our wikidata properties
        @param skip_nums .. skip all labels and aliases that have numbers in them
    """
    alias_label_map = {}
    print "create_alias_label_map, number of items:", len(properties)
    for propid, pvals in properties.iteritems():

        if skip_ids:
            if pvals['label'].find("ID") >= 0 or pvals['label'].find(" id") >= 0:
                continue
        if skip_nums:
            if not pvals['label'].replace(" ","").isalpha():
                continue

        for alias in pvals['aliases']:
            if lower: 
                alias = alias.lower()

            if skip_nums:
                if not alias.replace(" ","").isalpha():
                    continue

            if alias_label_map.has_key(alias):
                alias_label_map[alias].append( (pvals['label'], propid) )
            else:
                alias_label_map[alias] = [ (pvals['label'], propid) ]

            # tmp!!
            if alias == alias_label_map[alias][0][0]:
                print "INFO: alias == label", alias, alias_label_map[alias], "... looks like this is a \"bug\" in WikiData."

    print "create_alias_label_map, size of alias_label_map:", len(alias_label_map)
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



def filter_big_model_label_words(property_words, entities=False):

    if entities:
        MODEL = config.EMB_FILTERED_TERMS+'entities'
    else:
        MODEL = config.EMB_FILTERED_TERMS

    ofh = open(MODEL,'wb')

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
    line_prepender(MODEL, "%s %s" % (numlines, config.DIMS))



def create_average_property_vectors(entities=False):
    """
        this creates the representative average vectors for every property and write them
    """
    # load the model of filtered terms  
    if entities:
        model = KeyedVectors.load_word2vec_format(config.EMB_FILTERED_TERMS+'entities') # all lowercase
        ofh = codecs.open(config.EMB_PROP_LABELS+'entities','wb','utf-8')
        entities = get_entities_by_id(config.PICKLED_ENTITIES)
        properties = entities 
    else:
        model = KeyedVectors.load_word2vec_format(config.EMB_FILTERED_TERMS) # all lowercase
        ofh = codecs.open(config.EMB_PROP_LABELS,'wb','utf-8')
        properties = get_properties_by_id(config.PROPS_FILE)

    model.init_sims(replace=True)  
    index2word_set = set(model.index2word)


    for propid, vals in properties.iteritems():
        
        # create avg vector -- (a) init vector
        featureVec = np.zeros((config.DIMS,),dtype="float32")   

        # collect the vectors for the words in the label
        nwords = 0.
        for word in vals['label_words']: # all lowercase
            if word in index2word_set: 
                if DEBUG: print "word found:", word, model[word][0:5]
                nwords = nwords + 1.
                featureVec = np.add(featureVec,model[word])
            else:
                try:
                    if DEBUG: print "word not found:", word, vals['label']
                except:
                    print "word not found"
     
        # Divide the result by the number of words to get the average
        featureVec = np.divide(featureVec,nwords)

        # write the average vector to the file 
        print "Average Vec:", featureVec[0:5]
        vecstr= " ".join([str(x) for x in featureVec.tolist()])
        row = propid + " " + vecstr + "\n"
        ofh.write(row)


def create_concat_model(entities=False):
    """
        create the concated model (trained word embeddings + model of Property embeddings
    """

    if entities:
        OUR_MODEL=config.EMB_OUR_ENT_MODEL
        OUR_LABELS= config.EMB_PROP_LABELS+'entities'
    else:
        OUR_MODEL=config.EMB_OUR_MODEL
        OUR_LABELS= config.EMB_PROP_LABELS

    print "\t a) copy model to final file:", OUR_MODEL 
    subprocess.call(["/bin/cp", config.EMB_BIGFILE, OUR_MODEL])

    ## support for entities stops here

    print "\t b) adding our property vectors from file:", OUR_LABELS 
    subprocess.call("/bin/cat %s >> %s " % (OUR_LABELS, OUR_MODEL), shell=True)

    print "\t c) check if we have a metadata line already, if yes delete it"
    with open(OUR_MODEL) as data_file:
        for line in data_file:
            num_ele = len(line.split(" "))
            if num_ele == 2:
                print "\t\t header found .. need to delete first line from file", OUR_MODEL
                subprocess.call("/usr/bin/tail -n +2 %s > /tmp/abcd77" % (OUR_MODEL), shell=True)
                subprocess.call(["/bin/mv", "/tmp/abcd77", OUR_MODEL])
                print "CHECK THAT IT WORKED!"
                #sys.exit()
            else:
                print "\t\t **** NO header found .. fine ***" 
            break

    print "\t c) count number of lines in file", OUR_MODEL 
    wc_call_out =  subprocess.check_output("/usr/bin/wc %s" % (OUR_MODEL,), stderr=subprocess.STDOUT, shell=True).strip()
    num_lines = wc_call_out.split(" ")[0]

    print "\t d) Finally, prepend a line with (num_lines DIMS) to our model:", OUR_MODEL
    line_prepender(OUR_MODEL, "%s %s" % (num_lines, config.DIMS))
    print "\t DONE"



def load_model_and_plist(entities=False):
    """
        used in scripts to finally compute the similary vals between terms and WD Properties

        this just loads our model (with emb word + our property vectors) into memory
        and it also returns a list of all available properties in our model
    """

    if entities:
        MODELFN = config.EMB_OUR_ENT_MODEL
    else:
        MODELFN = config.EMB_OUR_MODEL
        
    print "Will load the model now:", MODELFN 
    model = KeyedVectors.load_word2vec_format(MODELFN)

    plist = []

    if not entities:
        for i in xrange(0,10000):
            try:
                prop = "P"+str(i)
                model[prop]
                plist.append(prop)
            except KeyError:
                pass

    print "Done loading the model:", MODELFN 
    return model, plist


def preprocess_query(term, lower, model):
    words = []

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

    return words



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

    words = preprocess_query(term, lower, model)


    sims, alias_sims = [], []
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


def get_closest_entities(term, model, lower=True, num_sugg=config.NUM_SUGG_PROPS, add_alias_terms_to_result=False, entity_aliases=None):
    """ @param term: a term from the user (term), the instances of the respective entity (instance_properties)
               term should be unicode (preferred) or utf-8 string
        @param properties: just for debugging, not needed in the production version 
        @param add_alias_terms_to_result: additionally to the word embedding-based results, also matches in the aliases (Wikidata: also known as) into the matches
        @param property_aliases: mapping of properties to list of its aliases, needed when add_alias_terms_to_result == True

        returns: the properties most similar to the input term
    """

    words = preprocess_query(term, lower, model)


    sims, alias_sims = [], []
    if add_alias_terms_to_result:
        alias_sims = match_in_entity_aliases(term, entity_aliases, lower=lower)

    if len(words) == 0:
        print "WARN: Term -- %s -- (or it's parts) not found in the model!. We have no suggestions from word embeddings!" % (term.encode("utf-8"),)
        return alias_sims 


    # get closest results from the model 
    sims = model.most_similar(positive=words, topn=num_sugg*2)
    print "Before filtering", sims
    
    # filter non-entities
    sims = [s for s in sims if s[0].startswith('Q') and s[0][1:].isdigit()]
    sims = sims[:num_sugg]
    print "Alter filtering", sims
    sorted_sims = sorted(sims,key=itemgetter(1))
    sorted_sims.reverse()

    return alias_sims + sorted_sims[:num_sugg]


def get_classic_search_res(alias, entities, lower=True, num_sugg=100, add_alias_terms_to_result=False, classic_mode=''):


    if lower:
        alias = alias.lower()


    if classic_mode == 'complex':
        # split into words and remove stopwords
        alias_words = [ w for w in alias.split(" ") if w not in stop]
        print "\n\nalias words", alias_words
    else:
        alias_words = [alias]


    res = {}    
    for alias_word in alias_words:
        p = re.compile( "(\W|^)%s(\W|$)" % (alias_word,) )

        for e_id, e_vals in entities.iteritems():
            
            if p.search( e_vals['label'] ):
                _add_to_res(res, e_id, 0.8)
                try:
                    print "Found in label", e_vals['label']
                except:
                    print "Found in label -- encoding error"

            if p.search( e_vals['description'] ):
                _add_to_res(res, e_id, 0.2) 
                try:
                    print "Found in description", e_vals['description']
                except:
                    print "Found in description -- encoding error"

    found_ents = []
    for k,v in res.iteritems():
        found_ents.append( (k, v) )

    sorted_ents = sorted(found_ents,key=itemgetter(1))
    sorted_ents.reverse()

    ## debugging:
    print "\n\nWe found:", sorted_ents
    print "Input data: Alias (%s)" % (alias,)
    
    return sorted_ents
        
    
        

def _add_to_res(res, e_id, val):
    num_id = int(e_id[1:])
    discount = float(num_id) / 10000000 # normalize discount to a value 0.0 to 0.1 (dep on id of entity)
    val = val-discount
    if res.has_key(e_id):
        res[e_id] += val
    else:
        res[e_id] = val





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

def match_in_entity_aliases(term, entity_aliases,lower=True, debug=False):
    """
        -- for all parameters see in the outer function: get_closest_properties
        @param term 
    """


    ## list of matches in alias strings of the properties
    entities = []
    if lower: term=term.lower()
    if debug: print "\n\n\n\nsearch term", term

    for alias in entity_aliases.keys():
        found = False

        if lower: alias=alias.lower()

        if alias.find(term)>=0:
            found = True
        if found:
            if debug: print alias, entity_aliases[alias]
            entities.append( entity_aliases[alias][0][1] )


    entities = list(set(entities)) # make results unique
    alias_sims = [(e,1.0) for e in entities]
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

def sample_output_entities(entities):
    """
        unimportant debugging/testing function
    """
    print "TEST:"
    print "\tLabel:\t\t", entities['Q22']['label']
    print "\tAliases:\t", entities['Q22']['aliases']
    print "\tdescription:\t", entities['Q22']['description']
    print "\tLabelDescAliasesWords:\t", entities['Q22']['label_words']




if __name__ == "__main__":

    from config import PROPS_FILE
    properties = get_properties_by_id(PROPS_FILE)


    property_aliases1 = create_property_aliases(properties, skip_ids=True)
    property_aliases2 = create_property_aliases(properties, skip_ids=False)

    from pprint import pprint; pprint(property_aliases1)




    print "*****Some statistics *****"
    print "Number of properties:", len( properties ) 
    print "Number of properties with aliases without IDs:", len( property_aliases1) 
    print "Number of properties with aliases incl IDs", len( property_aliases2) 


    num_alias_all      = len(create_alias_label_map(properties, skip_ids=False))
    num_alias_skip_ids = len(create_alias_label_map(properties, skip_ids=True))
    print "Number of aliases (incl ids):", num_alias_all 
    print "Number of aliases (skip ids):", num_alias_skip_ids 
    print "Number of IDs in aliases:",     num_alias_all - num_alias_skip_ids


    pprint_closest_properties("test term", [(u'P434', 0.3667969984041744), (u'P373', 0.36222223691644562)], get_properties_by_id(PROPS_FILE))
   
    print 
    #create_concat_model()

