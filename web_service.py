import sys, os, json
import tornado.ioloop
import tornado.web
from tornado_json.routes import get_routes
from tornado_json.application import Application
from tornado_json import schema
from tornado_json.requesthandlers import APIHandler

import helpers, config

propsUtils = None
entitiesUtils = None

DEFAULT_ENTITIES_LIMIT = 100

def result_to_json(tuple):
    dict = {}
    dict['id'] = tuple[0]
    dict['value'] = tuple[1]
    return dict

class PropsUtils():
    def __init__(self):
        self.model = []
        self.plist = []
        self.property_aliases = {}
        self.load_model()

    def load_model(self):
        model, plist = helpers.load_model_and_plist()

        properties = helpers.get_properties_by_id(config.PROPS_FILE)
        property_aliases = helpers.create_property_aliases(properties)

        self.model = model
        self.plist = plist
        self.property_aliases = property_aliases

    def get_closest_properties(self, term, instance_properties):
        return helpers.get_closest_properties(term, self.model, instance_properties, self.plist, [], add_alias_terms_to_result=True, property_aliases=self.property_aliases)

class EntitiesUtils():
    def __init__(self):
        self.model = []
        self.load_model()

    def load_model(self):
        model, xxx = helpers.load_model_and_plist(entities=True)

        self.model = model

    def get_closest_entities(self, term, limit):
        return helpers.get_closest_entities(term, self.model, lower=True, num_sugg=limit, add_alias_terms_to_result=False, entity_aliases=None)

class PropsHandler(APIHandler):
    @schema.validate(
        input_schema={
            "term": {"type": "string"},
            "instance_properties": {"type": "stringArray"},
            "threshold": { "type": "number", "optional": "true" },
            "limit": { "type": "integer", "optional": "true" }
        },
        output_schema={
            "type": "array",
            "items": {
                "id": "string",
                "value": "string"
            }
        },
    )
    def post(self):
        attrs = dict(self.body)

        closest_propserties = propsUtils.get_closest_properties(attrs['term'], attrs['instance_properties'])
        
        if 'threshold' in attrs:
            closest_propserties = filter(lambda x: x[1] >= attrs['threshold'], closest_propserties)

        if 'limit' in attrs:
            closest_propserties = closest_propserties[:attrs['limit']]

        return map(result_to_json, closest_propserties)

class EntitiesHandler(APIHandler):
    @schema.validate(
        input_schema={
            "term": {"type": "string"},
            "limit": { "type": "integer", "optional": "true" }
        },
        output_schema={
            "type": "array",
            "items": {
                "id": "string",
                "value": "string"
            }
        },
    )
    def post(self):
        attrs = dict(self.body)

        closest_entities = entitiesUtils.get_closest_entities(attrs['term'], attrs['limit'] if 'limit' in attrs else DEFAULT_ENTITIES_LIMIT)

        return map(result_to_json, closest_entities)

def make_app():
    return tornado.web.Application([
        (r"/", PropsHandler),
        (r"/entities", EntitiesHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    if 'PORT' in os.environ:
        port=os.environ['PORT']
    else:
        port=8888
    app.listen(port)

    print "initializing property model..."
    propsUtils = PropsUtils()

    print "initializing entity model..."
    entitiesUtils = EntitiesUtils()
    
    print "models are loaded; ready to serve requests"

    tornado.ioloop.IOLoop.current().start()
