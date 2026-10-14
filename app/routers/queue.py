from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/queue", tags=["Live Queue"])


class QueueConnectionManager:
    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(self, doctor_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections.setdefault(doctor_id, []).append(websocket)

    def disconnect(self, doctor_id: int, websocket: WebSocket):
        if doctor_id in self.connections:
            if websocket in self.connections[doctor_id]:
                self.connections[doctor_id].remove(websocket)

            if not self.connections[doctor_id]:
                del self.connections[doctor_id]

    async def broadcast(self, doctor_id: int, message: dict):
        disconnected = []

        for websocket in self.connections.get(doctor_id, []):
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(doctor_id, websocket)


manager = QueueConnectionManager()


@router.websocket("/{doctor_id}")
async def live_queue(websocket: WebSocket, doctor_id: int):
    await manager.connect(doctor_id, websocket)

    try:
        await websocket.send_json({
            "message": "Connected to the live appointment queue",
            "doctor_id": doctor_id,
        })

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(doctor_id, websocket)