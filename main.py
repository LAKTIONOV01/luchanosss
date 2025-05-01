from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from api.handlers import user_router, login_router

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
app = FastAPI(title="luchanos-oxford-university")

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
