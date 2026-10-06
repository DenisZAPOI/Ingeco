"""
DTOs: Pydantic models of what enters and leaves the API.

One file per resource, `<resource>_dto.py`. Input models inherit from
InputModel, output models from ApiModel (see base.py).

A DTO is the single source of the validation, the typing and the OpenAPI
documentation, from which the front-end generates its TypeScript types.

Template to copy: health_dto.py
"""
