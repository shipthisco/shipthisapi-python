from pydantic import BaseModel, validator, constr
from typing import Any

class get_Collection(BaseModel):
    collection_name: constr(min_length=3)

class update_delete(BaseModel):
    collection_name: str
    object_id: constr(min_length=3)

class get_search_list_collection(BaseModel):
    collection_name: str
    query_filter: str

    @validator('query_filter')
    def check_query_filter_length(cls, query_filter):
        if len(query_filter) == 0:
            raise ValueError("Query filter cannot be empty.")
        return query_filter

class get_full_search_list_collection(BaseModel):
    collection_name: str
    query_params: dict[str, Any]

    @validator('query_params', pre=True, each_item=True)
    def check_query_params_structure(cls, query_params):
        if not isinstance(query_params, dict):
            raise ValueError("Query parameters should be of type dictionary.")
        for key, value in query_params.items():
            if not isinstance(key, str):
                raise ValueError(f"Key '{key}' is not a string.")
        return query_params
