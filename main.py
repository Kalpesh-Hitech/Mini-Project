from fastapi import FastAPI
from Exception.exception import integrity_exception_handler,global_exception_handler
from Routes.AdminCreate import admin_router

app=FastAPI()
app.exception_handler(integrity_exception_handler)
app.exception_handler(global_exception_handler)
app.include_router(admin_router)
# app.include_router(router)