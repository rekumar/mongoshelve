from unittest import TestCase
from uuid import UUID
from mongoshelve import MongoDict, MongoList
from pymongo import MongoClient


class TestMongoList(TestCase):
    def setUp(self):
        self.collection = MongoClient()["test_db"]["test_collection"]
        pass

    def tearDown(self):
        self.collection.drop()
        pass

    def makeList(self):
        d = MongoList(self.collection, name="testname")
        self.assertEqual(len(d), 0, "New list is not empty!")
        self.assertEqual(
            d._collection, self.collection, "Collection not set correctly!"
        )
        self.assertEqual(d, [], "Value not set correctly!")

    def test_defaultListValue(self):
        default_list = [1, 2]
        d = MongoList(self.collection, name="testname", default_value=default_list)
        self.assertEqual(d, default_list, "Value not set correctly!")

        invalid_default = [1, [1, 2]]
        with self.assertRaises(ValueError):
            d = MongoList(
                self.collection, name="invaliddefault", default_value=invalid_default
            )

    def test_buildingList(self):
        d = MongoList(self.collection, name="testname", default_value=[1, 2, 3])
        self.assertEqual(d[0], 1, "Value not set correctly!")
        self.assertEqual(d[2], 3, "Value not set correctly!")
        self.assertEqual(d, [1, 2, 3], "Value not set correctly!")

    def test_listMethods(self):
        default = [1, 2, 3, 4, 5]
        d = MongoList(self.collection, name="testname", default_value=default)
        self.assertEqual(len(d), 5, "Length not set correctly!")
        self.assertEqual(d, default, "__eq__ not returning correctly!")

        self.assertEqual(d.pop(), default[-1], "Values not set correctly!")

        d.append(6)
        self.assertEqual(d[-1], 6, "Append not set correctly!")
        d.extend([10, 11, 12])
        self.assertEqual(d[-3:], [10, 11, 12], "Extend not set correctly!")

        self.assertEqual(d.index(2), 1, "Index not set correctly!")
        self.assertEqual(d.count(2), 1, "Count not set correctly!")

        d.insert(5, 100)
        self.assertEqual(d[5], 100, "Insert not set correctly!")
        d.remove(100)
        self.assertFalse(100 in d, "Remove or in not set correctly!")

    def test_invalidValues(self):
        d = MongoList(self.collection, name="testname", default_value=[0])
        with self.assertRaises(ValueError):
            d[0] = [1, 2]
        with self.assertRaises(ValueError):
            d.append([1, 2])
        with self.assertRaises(ValueError):
            d.append({"test": "value"})
