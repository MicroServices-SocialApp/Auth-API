from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from router import oauth2

# -----------------------------------------------------------------------------------------------

app = FastAPI(root_path="/auth")
app.include_router(oauth2.router)

# -----------------------------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------------------------
