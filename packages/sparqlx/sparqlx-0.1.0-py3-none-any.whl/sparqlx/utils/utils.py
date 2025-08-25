from collections import UserDict
from collections.abc import Callable, Iterator
from json import JSONDecodeError
from typing import NamedTuple

import httpx
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.plugins.sparql import prepareQuery

from sparqlx.utils.types import _TSPARQLBinding, _TSPARQLBindingValue


def _to_rdflib_bindings(
    response: httpx.Response,
) -> Iterator[_TSPARQLBinding]:
    """Get flat dicts from a SPARQL SELECT JSON response."""

    try:
        json_response = response.json()
    except JSONDecodeError as error:
        error.add_note("Note that to_rdflib=True requires JSON as response format.")
        raise error

    variables = json_response["head"]["vars"]
    response_bindings = json_response["results"]["bindings"]

    def _get_binding_pairs(binding) -> Iterator[tuple[str, _TSPARQLBindingValue]]:
        """Generate key value pairs from response_bindings.

        The 'type' and 'datatype' fields of the JSON response
        are examined to cast values to Python types according to RDFLib.
        """
        for var in variables:
            if (binding_data := binding.get(var, None)) is None:
                yield (var, None)
                continue

            match binding_data["type"]:
                case "uri":
                    yield (var, URIRef(binding_data["value"]))
                case "literal":
                    literal = Literal(
                        binding_data["value"],
                        datatype=binding_data.get("datatype", None),
                    )

                    # call toPython in any case for validation
                    literal_to_python = literal.toPython()

                    if literal.datatype in (XSD.gYear, XSD.gYearMonth):
                        yield (var, literal)
                    else:
                        yield (var, literal_to_python)

                case "bnode":
                    yield (var, BNode(binding_data["value"]))
                case _:  # pragma: no cover
                    assert False, "This should never happen."

    for binding in response_bindings:
        yield dict(_get_binding_pairs(binding))


def _to_rdflib_graph(response: httpx.Response) -> Graph:
    _format, *_ = response.headers["content-type"].split(";")
    graph = Graph().parse(response.content, format=_format)
    return graph


class _MimeTypeMap(UserDict):
    def __missing__(self, key):
        return key


class BindingsResultMimeTypeMap(_MimeTypeMap):
    def __init__(self):
        self.data = {
            "json": "application/sparql-results+json",
            "xml": "application/sparql-results+xml",
            "csv": "text/csv",
            "tsv": "text/tab-separated-values",
        }


class GraphResultMimeTypeMap(_MimeTypeMap):
    def __init__(self):
        self.data = {
            "turtle": "text/turtle",
            "xml": "application/rdf+xml",
            "ntriples": "application/n-triples",
            "json-ld": "application/ld+json",
        }


class QueryParameters(NamedTuple):
    response_format: str
    rdflib_converter: Callable[[httpx.Response], Iterator[_TSPARQLBinding] | Graph]


def get_query_parameters(
    query: str, to_rdflib: bool = False, response_format: str | None = None
) -> QueryParameters:
    query_type = prepareQuery(queryString=query).algebra.name

    match query_type:
        case "SelectQuery" | "AskQuery":
            mime_map = BindingsResultMimeTypeMap()
            _response_format = mime_map[response_format or "json"]
            rdflib_converter = _to_rdflib_bindings
        case "DescribeQuery" | "ConstructQuery":
            mime_map = GraphResultMimeTypeMap()
            _response_format = mime_map[response_format or "turtle"]
            rdflib_converter = _to_rdflib_graph
        case _:
            raise ValueError(f"Unsupported query type: {query_type}")

    return QueryParameters(
        response_format=_response_format, rdflib_converter=rdflib_converter
    )
