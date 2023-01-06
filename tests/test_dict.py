from unittest import TestCase
from uuid import UUID
from mongoshelve import MongoDict, MongoList
from pymongo import MongoClient

class TestMongoDict(TestCase):
    def setUp(self):
        self.collection = MongoClient()["test_db"]["test_collection"]
        pass

    def tearDown(self):
        self.collection.drop()
        pass

    def test_makeDict(self):
        d = MongoDict(self.collection, name="testname")
        self.assertEqual(len(d), 0, "New dict is not empty!")
        self.assertEqual(
            d._collection, self.collection, "Collection not set correctly!"
        )
        self.assertEqual(d, {}, "Value not set correctly!")

    def test_defaultDictValue(self):
        default_dict = {"test": "value"}
        d = MongoDict(self.collection, name="testname", default_value=default_dict)
        self.assertEqual(d, default_dict, "Value not set correctly!")

    def test_buildingDict(self):
        d = MongoDict(self.collection, name="testname")
        d["test"] = "value"
        self.assertEqual(d["test"], "value", "Value not set correctly!")
        d["test2"] = "value2"
        self.assertEqual(d["test2"], "value2", "Value not set correctly!")

        d["test_list"] = ["value1", "value2"]
        self.assertEqual(
            d["test_list"], ["value1", "value2"], "List not set correctly!"
        )

        d["test_dict"] = {"test": "value"}
        self.assertEqual(d["test_dict"], {"test": "value"}, "Dict not set correctly!")

        d["test_nested_dict"] = {"test": {"test": "value"}}
        self.assertEqual(
            d["test_nested_dict"],
            {"test": {"test": "value"}},
            "Nested dict not set correctly!",
        )

        d["test_nested_list"] = {"test": ["value1", "value2"]}
        self.assertEqual(
            d["test_nested_list"],
            {"test": ["value1", "value2"]},
            "Nested list not set correctly!",
        )

    def test_dictMethods(self):
        default = {
            "test": "value",
            "test_list": [1, 2, 3],
            "test_dict": {"test": "value"},
            "test_nested_dict": {"test": {"test": "value"}},
            "test_nested_list": {"test": [1, 2, 3]},
        }
        d = MongoDict(self.collection, name="testname", default_value=default)
        self.assertEqual(len(d), 5, "Length not set correctly!")
        self.assertEqual(d, default, "__eq__ not returning correctly!")
        self.assertEqual(d.keys(), default.keys(), "Keys not set correctly!")

        compare_values = []
        for value in d.values():
            if isinstance(value, MongoDict):
                compare_values.append(value.copy())
            elif isinstance(value, MongoList):
                compare_values.append(value.copy())
            else:
                compare_values.append(value)
        self.assertEqual(
            compare_values, list(default.values()), "Values not set correctly!"
        )
        self.assertEqual(d.get("test"), "value", "Get not set correctly!")
        self.assertEqual(
            d.get("nonexistent_key"),
            None,
            "Get not set correctly for nonexistent keys!",
        )
        self.assertEqual(
            d.get("nonexistent_key", "default"),
            "default",
            "Get not set correctly for nonexistent keys with default value!",
        )
        self.assertEqual(d.pop("test"), "value", "Pop not set correctly!")
        self.assertEqual(len(d), 4, "Length not set correctly after pop!")
        d["last"] = "last_value"
        self.assertEqual(
            d.popitem(),
            ("last", "last_value"),
            "Popitem not set correctly!",
        )

        self.assertEqual(
            d["test_dict"], default["test_dict"], "Dict not set correctly!"
        )

    def test_invalidValues(self):
        d = MongoDict(self.collection, name="testname")
        with self.assertRaises(ValueError):
            d["test"] = [[1, 2]]
        with self.assertRaises(ValueError):
            d["test"] = [{1: 2}]
        with self.assertRaises(ValueError):
            d["test"] = [(1, 2)]
