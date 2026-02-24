from fastapi import FastAPI
from Exception.exception import (
    integrity_exception_handler,
    global_exception_handler,
    request_validation_exception_handler,
    response_validation_exception_handler,
)

# from Routes.AdminCreate import admin_router
from Routes.User.PostAPI import create_router
from Routes.Task.PostAPI import task_post
from Routes.Task.PatchAPI import task_patch
from Routes.Team.PostAPI import team_post
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError, ResponseValidationError

app = FastAPI()
app.add_exception_handler(IntegrityError, integrity_exception_handler)
# app.add_exception_handler(ResponseValidationError, request_validation_exception_handler)
# app.add_exception_handler(
#     ResponseValidationError, response_validation_exception_handler
# )
app.add_exception_handler(Exception, global_exception_handler)
app.include_router(create_router)
app.include_router(team_post)
app.include_router(task_post)
app.include_router(task_patch)
# app.include_router(router)
