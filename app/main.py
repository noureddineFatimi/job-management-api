from fastapi import FastAPI, Request
from routers import file, job, user, auth

app = FastAPI(title="Job Offers Management API")

app.include_router(auth.router)
app.include_router(job.router)
app.include_router(user.router)
app.include_router(file.router)

@app.get("/", include_in_schema=False)
def redirection(request: Request):
    return {"message": "Oups! c'est par là 😊 " + str(request.base_url) + "docs"}