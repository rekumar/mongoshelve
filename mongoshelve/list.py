from typing import Any, Union
from pymongo.collection import Collection

UUID4_PLACEHOLDER = "be8b61ee-48b1-4624-bf7a-2ca31f7c5ef4"


class MongoList:
    """Class that emulates a list, but stores the list in the device database. Useful for working with Device attributes that are lists, so values persist across alabos sessions. This should be instantiated using `alab_management.device_view.device.BaseDevice.list_in_database`"""

    def __init__(
        self,
        collection: Collection,
        name: str,
        default_value: Union[list, None] = None,
        _projection: str = "contents",
    ):
        self._collection = collection
        self._projection = _projection
        self.name = name
        self.default_value = default_value or []

        if not any([isinstance(self.default_value, x) for x in [list, tuple]]):
            raise ValueError("ListInDatabase must be initialized with a list or tuple!")
        for val in self.default_value:
            self._raise_if_invalid_value(val)
        self.apply_default_value(overwrite=False)

    @classmethod
    def _raise_if_invalid_value(cls, val: Any):
        """We do not support nesting iterables within ListInDatabase. This is tricky to implement in pymongo so we have opted to not support for now. This function checks for iterabls and raises an error if it finds any.

        Args:
            val (Any): Value that we would like to store in the ListInDatabase.

        Raises:
            ValueError: Nested iterables are not supported for a ListInDatabase. Elements within a ListInDatabase must be single values (ie not a dict, list, or tuple). Note that this affects lists nested within DictInDatabase as well!
        """
        if any([isinstance(val, x) for x in [dict, list, tuple]]):
            raise ValueError(
                "Nested iterables are not supported for a ListInDatabase. Elements within a ListInDatabase must be single values (ie not a dict, list, or tuple). Note that this affects lists nested within DictInDatabase as well!"
            )

    def apply_default_value(self, overwrite=False):
        """This is called within `alab_management.scripts.setup_lab()` to ensure that all devices have the correct default values for their attributes. This should not be called manually.

        Raises:
            ValueError: Device is not found in the database. This should only occur if this function is called out of order (i.e. before the device is created in the db).
        """
        result = self._collection.find_one(self.db_filter)
        if result is None:
            self._collection.insert_one({"name": self.name, "contents": {}})
        else:
            if not overwrite:
                return

        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: self.default_value}}
        )

    @property
    def db_projection(self):
        return self._projection

    @property
    def db_filter(self):
        return {"name": self.name}

    @property
    def _value(self):
        value = self._collection.find_one(
            {"name": self.name}, projection=[self.db_projection]
        )
        if value is None:
            raise ValueError(
                f"Entry {self.name} does not contain data at {self.db_projection}!"
            )
        return_value = value
        for key in self.db_projection.split("."):
            return_value = return_value[key]

        return return_value

    def append(self, x):
        self._raise_if_invalid_value(x)
        self._collection.update_one(self.db_filter, {"$push": {self.db_projection: x}})

    def extend(self, x):
        for val in x:
            self._raise_if_invalid_value(val)
        current = self._value
        current.extend(x)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def clear(self):
        self._collection.update_one(self.db_filter, {"$set": {self.db_projection: []}})

    def copy(self):
        return self._value  # copied by virtue of reading from database

    def index(self, x, start=0, stop=-1):
        return self._value.index(x, start, stop)

    def count(self, x):
        return self._value.count(x)

    def insert(self, i, x):
        self._raise_if_invalid_value(x)
        current = self._value
        current.insert(i, x)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def pop(self, i=-1):
        current = self._value
        result = current.pop(i)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )
        return result

    def remove(self, x):
        current = self._value
        current.remove(x)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def reverse(self):
        current = self._value
        current.reverse()
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def sort(self, key=None, reverse=False):
        current = self._value
        current.sort(key, reverse)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def __repr__(self):
        return str(self._value)

    def __str__(self):
        return str(self._value)

    def __add__(self, x):
        self._raise_if_invalid_value(x)
        return self._value + x

    def __iadd__(self, x):
        self._raise_if_invalid_value(x)
        new = self._value + x
        self._collection.update_one(self.db_filter, {"$set": {self.db_projection: new}})
        return self

    def __mul__(self, x):
        return self._value * x

    def __imul__(self, x):
        new = self._value * x
        self._collection.update_one(self.db_filter, {"$set": {self.db_projection: new}})
        return self

    def __getitem__(self, x):
        return self._value[x]

    def __setitem__(self, x, val):
        self._raise_if_invalid_value(val)
        current = self._value
        current[x] = val
        if any(isinstance(val, t) for t in [dict, list, tuple]):
            raise TypeError(
                "Elements within a ListInDatabase cannot be iterable. Spefically, values of the ListInDatabase cannot be a dict, list, or tuple!"
            )
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def __len__(self):
        return len(self._value)

    def __contains__(self, x):
        return x in self._value

    def __eq__(self, x):
        return self._value == x
