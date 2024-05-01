from fastapi import FastAPI
import save_selfie
import get_images
import get_names
import start_predict
import get_data
import get_profile
import create_folder
import bulk_image_upload
import favourite
import face_match
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(save_selfie.router)
app.include_router(start_predict.router)
app.include_router(get_images.router)
app.include_router(start_predict.router)
app.include_router(get_names.router)
app.include_router(get_data.router)
app.include_router(get_profile.router)
app.include_router(create_folder.router)
# app.include_router(face_match.router)
# app.include_router(bulk_image_upload.router)
favourite = favourite.router


# Define router for bulk image upload
bulk_image_router = bulk_image_upload.router
face_match_process = face_match.router
# Register bulk image upload router with event name in URL path
app.include_router(
    favourite,
    prefix="/favourites_to_zip",
    tags=["Bulk Image Upload"]
)

app.include_router(
    face_match_process,
    prefix="/face_match",
    tags=["face match"]
)