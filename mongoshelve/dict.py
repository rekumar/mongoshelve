from typing import Any, Union
from pymongo.collection import Collection
from .list import MongoList

UUID4_PLACEHOLDER = "be8b61ee-48b1-4624-bf7a-2ca31f7c5ef4"


class MongoDict:
    """Class that emulates a dict, but stores the dict in the device database. Useful for working with Device attributes that are dict, so values persist across alabos sessions. This should be instantiated using `alab_management.device_view.device.BaseDevice.dict_in_database`"""

    def __init__(
        self,
        collection: Collection,
        name: str,
        default_value: Union[dict, None] = None,
        _projection: str = "contents",
    ):
        self._collection = collection
        self._projection = _projection
        self.name = name
        if default_value is None:
            self.default_value = {}
        else:
            if not isinstance(default_value, dict):
                raise ValueError(
                    "Default value for DictInDatabase must be a dictionary!"
                )
            self.default_value = default_value

        self.apply_default_value(overwrite=False)

    def apply_default_value(self, overwrite: bool = False):
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
                f"DictInDatabase {self.name} does not contain data at {self.db_projection}!"
            )
        return_value = value
        for key in self.db_projection.split("."):
            return_value = return_value[key]

        for key, val in return_value.items():
            if isinstance(val, dict):
                return_value[key] = MongoDict(
                    collection=self._collection,
                    name=self.name,
                    default_value=val,
                    _projection=f"{self.db_projection}.{key}",
                )
            elif isinstance(val, list):
                return_value[key] = MongoList(
                    collection=self._collection,
                    name=self.name,
                    default_value=val,
                    _projection=f"{self.db_projection}.{key}",
                )
        return return_value

    def as_normal_dict(self) -> dict:
        value = self._collection.find_one(
            {"name": self.name}, projection=[self.db_projection]
        )
        if value is None:
            raise ValueError(
                f"Dict by name {self.name} does not contain data at {self.db_projection}!"
            )
        for key in self.db_projection.split("."):
            value = value[key]
        return value

    def clear(self):
        self._collection.update_one(self.db_filter, {"$set": {self.db_projection: {}}})

    def copy(self):
        return self.as_normal_dict()  # copied by virtue of reading from database

    def fromkeys(self):
        raise NotImplementedError("fromkeys is not implemented for DictInDatabase")

    def get(self, key, default=None):
        return self._value.get(key, default)

    def items(self):
        return self._value.items()

    def keys(self):
        return self.as_normal_dict().keys()

    def values(self):
        return self.as_normal_dict().values()

    def pop(self, key, default=UUID4_PLACEHOLDER):
        current = self.as_normal_dict()
        result = current.pop(key, default)
        if result == UUID4_PLACEHOLDER:  # only fires if default value was not provided
            raise KeyError(f"{key} was not found in the dictionary!")

        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )
        return result

    def popitem(self):
        current = self._value
        result = current.popitem()
        current_dict = self.as_normal_dict()
        current_dict.pop(result[0])
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current_dict}}
        )
        return result

    def setdefault(self, key, default=None):
        raise NotImplementedError("setdefault is not implemented for DictInDatabase")

    def update(self, *args, **kwargs):
        current = self._value
        current.update(*args, **kwargs)
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def __reversed__(self):
        return reversed(self._value)

    def __iter__(self):
        return iter(self._value)

    def __repr__(self):
        return str(self.as_normal_dict())

    def __str__(self):
        return str(self.as_normal_dict())

    def __getitem__(self, x):
        return self._value[x]

    def __setitem__(self, x, val):
        # lists/tuples entered as dict values may be returned later as ListInDatabase objects. ListInDatabase does not support nested iterables! So we will raise an error if we detect values that ListInDatabase cannot handle.
        if any([isinstance(val, t) for t in [tuple, list]]):
            for _val in val:
                MongoList._raise_if_invalid_value(_val)

        current = self.as_normal_dict()
        current[x] = val
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def __delitem__(self, x):
        current = self.as_normal_dict()
        del current[x]
        self._collection.update_one(
            self.db_filter, {"$set": {self.db_projection: current}}
        )

    def __contains__(self, x):
        return x in self.as_normal_dict()

    def __len__(self):
        return len(self.as_normal_dict())

    def __eq__(self, other):
        return self.as_normal_dict() == other
