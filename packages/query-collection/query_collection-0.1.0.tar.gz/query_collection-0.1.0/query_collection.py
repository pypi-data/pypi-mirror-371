from typing import Any, Mapping, Optional, Union

from rdflib.plugins.sparql.sparql import Query


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
