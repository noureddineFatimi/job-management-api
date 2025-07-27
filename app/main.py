from fastapi import FastAPI
from routers import file, job, user, auth

app = FastAPI(title="Job offers API")

app.include_router(auth.router)
app.include_router(job.router)
app.include_router(user.router)
app.include_router(file.router)