from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.routers.queue import manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/queue/{doctor_id}")
async def live_appointment_queue(
    websocket: WebSocket,
    doctor_id: int
):
    await manager.connect(doctor_id, websocket)

    try:
        await websocket.send_json({
            "message": "Connected to the live appointment queue",
            "doctor_id": doctor_id,
            "status": "connected",
        })

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(doctor_id, websocket)