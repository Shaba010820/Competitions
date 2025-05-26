from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError


router = APIRouter(prefix='/elastic', tags=['ElasticSearch'])


es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "changeme123"),
    verify_certs=False
)


def index_user_in_elastic(user):
    initials = get_initials(user.username)
    doc = {
        "id": user.id,
        "username": user.username,
        "initials": initials,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }
    es.index(index="users", id=user.id, document=doc)


INDEX_NAME = "users"


def get_initials(text: str) -> str:
    words = text.split()
    initials = ''.join(word[0].lower() for word in words if word)
    return initials



@router.get("/search_users")
def search_users(query: str = Query(..., description="Строка поиска")):
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "username.keyword": {
                                "value": query,
                                "boost": 20
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["username^3", "email"],
                            "analyzer": "autocomplete_analyzer",
                            "boost": 10
                        }
                    },
                    {
                        "wildcard": {
                            "username.keyword": {
                                "value": f"*{query.lower()}*",
                                "case_insensitive": True,
                                "boost": 5
                            }
                        }
                    },
                    {
                        "match_phrase_prefix": {
                            "username": {
                                "query": query,
                                "slop": 2,
                                "boost": 3
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "size": 10
    }
    if len(query) < 3:
        search_body["query"]["bool"]["should"] = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["username^3", "email"],
                    "type": "most_fields",
                    "analyzer": "autocomplete_analyzer"
                }
            }
        ]
    try:
        response = es.search(index=INDEX_NAME, body=search_body)
        results = [hit["_source"] for hit in response["hits"]["hits"]]
        return {"results": results}
    except NotFoundError:
        return {"error": f"Индекс '{INDEX_NAME}' не найден."}

