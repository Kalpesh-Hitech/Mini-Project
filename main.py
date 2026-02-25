from fastapi import FastAPI
from Exception.exception import (
    integrity_exception_handler,
    global_exception_handler,
    request_validation_exception_handler,
    response_validation_exception_handler,
)

# from Routes.AdminCreate import admin_router
from Routes.User.PostAPI import create_router
from Routes.User.GetAPI import userRouter
from Routes.Task.PostAPI import task_post
from Routes.Task.PatchAPI import task_patch
from Routes.Team.PostAPI import team_post
from Routes.Team.UpdateAPI import team_patch
from Routes.Team.GetAPI import get_teamrouter
from Routes.Team.DeleteAPI import delete_teamrouter
from Routes.Task.DeleteAPI import delete_taskrouter
from Routes.User.PatchAPI import userUpdateRouter
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
app.include_router(userRouter)
app.include_router(team_patch)
app.include_router(get_teamrouter)
app.include_router(delete_teamrouter)
app.include_router(delete_taskrouter)
app.include_router(userUpdateRouter)
# app.include_router(router)
