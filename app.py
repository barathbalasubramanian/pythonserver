from fastapi import FastAPI
import save_selfie
import get_images
import get_names
import start_predict
import get_data


app = FastAPI()


app.include_router(save_selfie.router)
app.include_router(start_predict.router)
app.include_router(get_images.router)
app.include_router(start_predict.router)
app.include_router(get_names.router)
app.include_router(get_data.router)

