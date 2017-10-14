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

To set arbitrary path to properties model file, run script with env variable MODEL_FILE:

```bash
env MODEL_FILE=./models/fasttext.wiki.en.vec.small.300000.lines-Desc.True__w-prop-ids.FINAL.vec python ./web_service.py
```

To set arbitrary path to entities model file, run script with env variable ENTITIES_MODEL_FILE:

```bash
env ENTITIES_MODEL_FILE=../entities.model python ./web_service.py
```

### HTTP API reference

#### 1. Get properties, similar to passed term

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

#### 2. Get entities, similar to passed term

Path: /entities

Method: POST

Body:
```js
{
    "limit": 5, // optional, default is 100
    "term": "stadium"
}
```
Response:
```js
{
  "status": "success",
  "data": [
    {
      "id": "Q379306",
      "value": 1.0
    },
    {
      "id": "Q945548",
      "value": 1.0
    },
    {
      "id": "Q673598",
      "value": 1.0
    },
    {
      "id": "Q285983",
      "value": 1.0
    },
    {
      "id": "Q285074",
      "value": 1.0
    }
  ]
}
```

# trained models 
The model based on the fasttext Wikipedia model, which we extended with Wikidata properties
is found at:
https://aic.ai.wu.ac.at/~wohlg/ontodia_property_search/
