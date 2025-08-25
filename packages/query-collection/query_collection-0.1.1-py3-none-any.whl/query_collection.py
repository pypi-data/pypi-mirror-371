from os import scandir
from os.path import splitext
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from rdflib.plugins.sparql.sparql import Query


class TemplateQuery:
    def __init__(
        self,
        query_object: Union[str, Query],
        initNs: Optional[Mapping[str, Any]] = None,
    ):
        self.query_object = query_object
        self.initNs = initNs

    def prepare(self, **initBindings):
        return {
            "query_object": self.query_object,
            "initNs": self.initNs,
            "initBindings": initBindings,
        }

    p = prepare


class TemplateQueryCollection(dict):
    def __init__(self, queries: dict = {}, initNs: Optional[Mapping[str, Any]] = None):
        self.queries = queries
        self.initNs = initNs

    def get(self, key):
        query_object = self.queries.get(key)
        if not isinstance(query_object, TemplateQuery):
            return TemplateQuery(query_object=query_object, initNs=self.initNs)
        else:
            return query_object

    def set(self, key, val):
        self.queries[key] = val

    def loadFromDirectory(self, directory: Path):
        """Load a set of queries from .rq files in the given directory."""
        any(
            self.loadFromFile(path)
            for path in scandir(directory)
            if path.is_file() and splitext(path)[1] == ".rq"
        )

    def loadFromFile(self, filename: Path):
        """Load a queriy from an .rq file."""
        with open(filename, "r") as fileobject:
            self.set(splitext(filename)[0], fileobject.read())
