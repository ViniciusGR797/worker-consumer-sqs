import os
from mangum import Mangum
from utils.swagger import create_app
from routes import users, messages

app = create_app()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

handler = Mangum(app)

if os.getenv("ENV") == "LOCAL":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
