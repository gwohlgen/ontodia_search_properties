# ontodia_search_properties

Here you find the code to get **suggestions on properties** related to an entity in Wikidata -- based on a user search term.
It has so far only been tested with Wikidata, but an adaption to other data sets should be straightforward.

## Main parts:

a) To create a model use script `1_do_all_preprocessing.py`

b) To get suggestions for a user input, see script `get_similar_properties.py`

There are also scripts included for clustering properties, and for evaluating the system against predefined
aliases ("also known as") as a gold standard.

## Web service
Placed in `web_service.py` file. Contains simple Tornado-based web-server, that serves `POST` requests on `/` path.

To set application port, different from 8888, run script with env variable PORT:

```bash
env PORT=8889 python ./web_service.py
```

To set arbitrary path to `models` dir, that contains trained models, run script with env variable ONTODIA_SEARCH_PROPERTIES_BASEPATH:

```bash
env ONTODIA_SEARCH_PROPERTIES_BASEPATH=./ python ./web_service.py
```

### HTTP API reference
Path: /
Method: POST
Body:
```js
{
    "limit": 10, // optional,
    "threshold": 0.7, // optional
    "term": "hand play with",
    "instance_properties": ["P11", "P12"]
}
```
Response:
```js
{
  "status": "success",
  "data": [
    {
      "id": "P741",
      "value": 0.86217025908427947
    }
  ]
}
```
