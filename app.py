# modulos externos
from fastapi import FastAPI

# modulos internos
from routes import auth_routes
from routes import user_routes
from routes import category_routes
from routes import item_routes
from routes import auction_routes
from routes import payment_routes
from routes import bid_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(user_routes.router, prefix="/admin/users")
app.include_router(category_routes.router, prefix="/admin/categories")
app.include_router(item_routes.router, prefix="/items")
app.include_router(auction_routes.router, prefix="/auctions")
app.include_router(payment_routes.router, prefix="/payments")
app.include_router(bid_routes.router, prefix="/bids")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de subastas"}

