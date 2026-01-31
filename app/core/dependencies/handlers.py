from typing import Annotated
from fastapi import Query, Depends
from fastapi.responses import JSONResponse
from .validation import ValidationException


async def validation_exception_handler(exc: ValidationException):
    """Return a validation exception using data from ValidationException."""
    return JSONResponse(
        status_code=406,
        content={
            "detail":f"The field '{exc.field}' must be longer than {exc.min_length} characters"
        },
    )


async def common_parameters(q: str | None = None,
                            skip: Annotated[int, 
                                Query(deprecated = True,
                                    title = 'Offset of lost')]
                                = 0,
                            limit: int = 10
                            ):
    """Return common query parameters as skip, limit etc."""
    return {"q": q, "skip": skip, "limit": limit}

CommonsDep = Annotated[dict, Depends(common_parameters)]
