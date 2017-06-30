import sys
import helpers,config
import timeit


def inititalize_get_similar_properties():
    model, plist = helpers.load_model_and_plist()
    properties = helpers.get_properties_by_id(config.PROPS_FILE)
    return model, plist, properties


if __name__ == "__main__":

    start_time = timeit.default_timer()
    # code you want to evaluate
    model, plist, properties = inititalize_get_similar_properties()
    print "Time to load the model", timeit.default_timer() - start_time

    # the properties of the entity "Boris Becker", https://www.wikidata.org/wiki/Q76334
    instance_properties = [u'P646', u'P1447', u'P536', u'P641', u'P373', u'P269', u'P434', u'P213', u'P214', u'P741', u'P2641', u'P551', u'P599', u'P555', u'P1266', u'P1284', 
                           u'P1285', u'P691', u'P856', u'P54', u'P19', u'P31', u'P2048', u'P734', u'P735', u'P345', u'P1006', u'P349', u'P1412', u'P2067', u'P2163', u'P18', 
                           u'P2639', u'P569', u'P1263', u'P564', u'P2924', u'P1344', u'P3417', u'P244', u'P106', u'P268', u'P166', u'P227', u'P27', u'P26', u'P21', u'P866', u'P3363'] 

    ## term is the input given by the user (into the searchbox)
    term = u"hand played with"

    ## close_props is the result given by the service, format list of tuples (property, similarity)
    #       for example: [(u'P434', 0.3667969984041744), (u'P373', 0.36222223691644562), ... ]
    start_time = timeit.default_timer()
    close_props = helpers.get_closest_properties(term, model, instance_properties, plist, properties) 
    print "Time to get the suggestions", timeit.default_timer() - start_time

    ## just printing the result below here
    print close_props
    helpers.pprint_closest_properties(term, close_props, properties)

    ## one more test -- time against all properties
    start_time = timeit.default_timer()
    close_props = helpers.get_closest_properties(term, model, [], plist, properties) 
    print "Time to get the suggestions", timeit.default_timer() - start_time
    print "close_props[:10]", close_props[:10]
    helpers.pprint_closest_properties(term, close_props[:10], properties)

