# mongoshelve
Persistent Python lists and dictionaries in MongoDB.


# Example usage

First, create/access your MongoDB collection using `pymongo`. If you are unfamiliar with `pymongo`, [here are the quickstart docs](https://pymongo.readthedocs.io/en/stable/tutorial.html)!

```
from pymongo import MongoClient

client = MongoClient(
    host='localhost',
    port=27017,
    username='user',
    password='pass',
    authSource='admin',
)
database = client["your_database_name"]
collection = database["your_collection_name"]
```

Then you can create dictionaries or lists that are backed by MongoDB!

## Dictionaries

`MongoDict` supports nearly all dictionary functions, like `.keys()`, `.values()`, `.items()`, `.get()`, `.update()`, `.clear()`, `.copy()`, and `.popitem()`. I believe `.fromkeys()` and `.setdefault()` are the only ones that don't work.

```
from mongoshelve import MongoDict

my_dict = MongoDict(
    collection=collection,
    name="my_dict",
    ) #creates an empty dict
```

Nested dictionaries and lists are also supported!

```
my_dict["first_entry"] = "hello world"
my_dict["second_entry"] = [1,2,3]
my_dict["third_entry"] = {"a": 1, "b": {"hi":"bye"}, "c": [1,2,3]}
```

## Lists
Lists are fully supported except for one limitation. `MongoList` cannot store iterable values (ie `[1,[1,2]]` would not be supported as the second value is an iterable). This limitation arises because indexing specific array elements in MongoDB is tricky. If this is critical to your use case, please submit an issue! 

```
from mongoshelve import MongoList

my_list = MongoList(
    collection=collection,
    name="my_list",
    ) #creates an empty list

my_list.append(1)
my_list.pop()
```

## Default values persistence behavior

Both `MongoList` and `MongoDict` have an optional `default_value` parameter that can be used to set initial value of the list or dict in the MongoDB document. If `default_value` is not specified (default), the list or dict will be empty.

When `MongoList`/`MongoDict` is instantiated, it will check if the document exists in the MongoDB collection. If a document by this name already exists, the stored values will not be changed. If the document does not exist, it will be created using the `default_value` as the value.

If you _want_ to overwrite the values using your default, you can run the following method:


```
from mongoshelve import MongoList

my_list = MongoList(
    collection=collection,
    name="my_list",
    default_value=[1,2,3],
    ) # if document already exists, this will not overwrite the values
my_list.apply_default_values(overwrite=True) # this will overwrite the values
```
