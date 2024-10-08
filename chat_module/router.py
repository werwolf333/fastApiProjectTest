from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from auth_module.auth import verify_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from chat_module.connection_manager import ConnectionManager
from chat_module.models import Room
from database import get_db, SessionLocal
from fastapi import WebSocket, WebSocketDisconnect, FastAPI, APIRouter, HTTPException, Depends

manager = ConnectionManager()
router = APIRouter()
app = FastAPI()
templates = Jinja2Templates(directory="templates")


@router.get("/rooms", response_class=HTMLResponse)
async def get_main(request: Request, db: Session = Depends(get_db)):
    token = verify_token(request)
    username = token.get("sub")
    rooms = db.query(Room).all()
    room_names = [room.name for room in rooms]
    return templates.TemplateResponse("chat_module/main.html",
                                      {"request": request, "room_names": room_names, "username": username})


@router.post("/rooms/submit", response_class=HTMLResponse)
async def handle_form(request: Request, roomName: str = Form(...), db: Session = Depends(get_db)):
    try:
        room = db.query(Room).filter(Room.name == roomName).first()
        if room:
            return RedirectResponse(url=f"/rooms/{roomName}", status_code=303)
        else:
            new_room = Room(name=roomName)
            db.add(new_room)
            db.commit()
            db.refresh(new_room)
            return RedirectResponse(url=f"/rooms/{roomName}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_name}", response_class=HTMLResponse)
async def get_chat_room(
    request: Request,
    room_name: str,
    db: Session = Depends(get_db)
):
    token = verify_token(request)
    username = token.get("sub")
    room = db.query(Room).filter(Room.name == room_name).first()
    if room:
        return templates.TemplateResponse("chat_module/chat.html", {"request": request, "room_name": room_name, "username": username})
    else:
        return templates.TemplateResponse("chat_module/404.html", {"request": request})


@router.delete("/rooms/{room_name}")
async def delete_room(room_name: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.name == room_name).first()
    if room:
        await manager.disconnect_all(room_name)
        db.delete(room)
        db.commit()
        return RedirectResponse(url="/rooms", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Комната не найдена")

app.include_router(router)


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close()
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        await websocket.close()
        return

    await manager.connect(websocket, room, username)

    db = SessionLocal()
    room_in_db = db.query(Room).filter(Room.name == room).first()
    if not room_in_db:
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room, username)  # Передаем имя пользователя
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
