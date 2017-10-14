import os

#### edit here for new installation or basic conf for usage as service ####

# the path to the installation of the service / tool
if 'ONTODIA_SEARCH_PROPERTIES_BASEPATH' in os.environ:
    BASEPATH=os.environ['ONTODIA_SEARCH_PROPERTIES_BASEPATH']
else:
    # BASEPATH="/home/ontology/itmo/ontodia_search_properties/"
    BASEPATH="./"

# the maximum number of properties that will be suggested by the service
NUM_SUGG_PROPS = 20





################################################################################################
################### basic service config END ###################################################
################################################################################################

MODELPATH= BASEPATH + "models/"
PROPS_FILE= BASEPATH + "datafiles/props.json" ## json file with all the properties
P_ALIAS_MAP = BASEPATH + "datafiles/2_alias_label_map.json"
E_ALIAS_MAP = BASEPATH + "datafiles/2_entity_alias_label_map.json"

# use the description text for the property word embeddings? (addit. to the labels)
USE_DESCR_IN_PROP_VECTORS = True
#USE_DESCR_IN_PROP_VECTORS = False
#SKIP_LABELS_WITH_IDS = True # currently we evaluate both variants


#### edit here for new model or properties ####
#MODELFN = "lexvec.enwiki+newscrawl.300d.W.pos.vectors.all.369000"; DIMS=300 # lexvec wikipedia + newscrawl
#MODELFN = "glove.6B.300d.txt.small.10000.lines"; DIMS=300 # Wikipedia 2014 + Gigaword 5
#MODELFN = "glove.6B.100d.txt"; DIMS=100 # Wikipedia 2014 + Gigaword 5
#MODELFN = "lexvec.enwiki+newscrawl.300d.W.pos.vectors.small.10000.lines"; DIMS = 300 # lexvec wikipedia + newscrawl
MODELFN = "fasttext.wiki.en.vec.small.300000.lines"; DIMS=300 # Wikipedia, 2016?
#MODELFN = "fasttext.wiki.en.vec.small.10000.lines"; DIMS=300 # Wikipedia, 2016?
# MODELFN = "fasttext.wiki.en.vec"; DIMS=300 # Wikipedia, 2016?
# MODELFN = "glove.6B.50d.txt"; DIMS=50 # Wikipedia 2014 + Gigaword 5
# MODELFN = "glove.840B.300d.txt.small.300000.lines"; DIMS=300 # do in all 4 variants
# MODELFN = "glove.6B.50d.txt.small.10000.lines"; DIMS=50 # Wikipedia 2014 + Gigaword 5
# MODELFN = "glove.6B.100d.txt.small.10000.lines"; DIMS=100 # Wikipedia 2014 + Gigaword 5
# MODELFN = "glove.6B.300d.txt"; DIMS=300 # Wikipedia 2014 + Gigaword 5
# #///MODELFN = "meta_O2M_plus_oov.txt.small.300000.lines"; DIMS=300 # Wikipedia, 2016?
#////MODELFN = "meta_O2M_plus_oov.txt.small.10000.lines"; DIMS=300 # Wikipedia, 2016?


# for the evalation of the system quality against the gold standard
CORPORA_TO_EVAL = (
    "lexvec.enwiki+newscrawl.300d.W.pos.vectors.all.369000",
    "glove.6B.300d.txt.small.10000.lines",
    "glove.6B.100d.txt",
    "lexvec.enwiki+newscrawl.300d.W.pos.vectors.small.10000.lines",
    "fasttext.wiki.en.vec.small.300000.lines",
    "fasttext.wiki.en.vec.small.10000.lines",
    "glove.6B.50d.txt",
    "glove.840B.300d.txt.small.300000.lines",
    "glove.6B.50d.txt.small.10000.lines",
    "glove.6B.100d.txt.small.10000.lines",
    "glove.6B.300d.txt",
    "fasttext.wiki.en.vec"
)

#PICKLED_ENTITIES="/home/ontology/itmo/parse_dump/863af69690fb44eb22a4/filtered_entities_data_orig2.pickle"
PICKLED_ENTITIES="/home/ontology/itmo/parse_dump/863af69690fb44eb22a4/NEW_filtered_entities.pickle"



#### word embedding configs
EMB_BIGFILE        = MODELPATH + MODELFN
EMB_FILTERED_TERMS = MODELPATH + MODELFN + "-Desc." + str(USE_DESCR_IN_PROP_VECTORS) +"__filtered.for.wikidata.properties.vec"
EMB_PROP_LABELS    = MODELPATH + MODELFN + "-Desc." + str(USE_DESCR_IN_PROP_VECTORS) + "__property-id-only.vec"

if 'MODEL_FILE' in os.environ:
    EMB_OUR_MODEL = os.environ['MODEL_FILE']
else:
    EMB_OUR_MODEL  = MODELPATH + MODELFN + "-Desc." + str(USE_DESCR_IN_PROP_VECTORS) + "__w-prop-ids.FINAL.vec"

if 'ENTITIES_MODEL_FILE' in os.environ:
    EMB_OUR_ENT_MODEL = os.environ['ENTITIES_MODEL_FILE']
else:
    EMB_OUR_ENT_MODEL = MODELPATH + MODELFN + "-Desc." + str(USE_DESCR_IN_PROP_VECTORS) + "__w-prop-ids.FINAL.ENTITIES.vec"

DEBUG=False
