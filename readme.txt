Got the property data from there:
    https://tools.wmflabs.org/hay/propbrowse/
    --- download as file ..



1_property_data_complete.json
    this contains all the data from props.json, just nicely reformatted

2_alias_label_map.json
    this is a (alias: label) mapping of all
        alias ("also known as") ---> label
    It was created with:
        my_read_and_convert.py



MISC:
    becker.json -- sample data from testing the w2v-based similarity of input terms and properties


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