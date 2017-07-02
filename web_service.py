import sys, os

import json
import tornado.ioloop
import tornado.web
from tornado_json.routes import get_routes
from tornado_json.application import Application
from tornado_json import schema
from tornado_json.requesthandlers import APIHandler

import helpers, config

model = []
plist = []

def inititalize_get_similar_properties():
    global model
    global plist
    model, plist = helpers.load_model_and_plist()
    return model, plist


def to_json(tuple):
    dict = {}
    dict['id'] = tuple[0]
    dict['value'] = tuple[1]
    return dict

class MainHandler(APIHandler):
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
        global model, plist
        attrs = dict(self.body)

        closest_propserties = helpers.get_closest_properties(attrs['term'], model, attrs['instance_properties'], plist, []) 
        
        if 'threshold' in attrs:
            closest_propserties = filter(lambda x: x[1] >= attrs['threshold'], closest_propserties)

        if 'limit' in attrs:
            closest_propserties = closest_propserties[:attrs['limit']]

        return map(to_json, closest_propserties) # [{'id':k, 'value': v} for k, v in mapping.iteritems()]

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    if 'PORT' in os.environ:
        port=os.environ['PORT']
    else:
        port=8888
    app.listen(port)

    print "loading model (it can take a while)"
    inititalize_get_similar_properties()
    print "model is loaded; ready to serve requests"

    tornado.ioloop.IOLoop.current().start()