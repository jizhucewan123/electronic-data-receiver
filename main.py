from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime
import os
import uvicorn

app = FastAPI(
    title="电子数据接收器",
    description="接收电子设备传感器数据的API",
    version="1.0.0"
)

# 从环境变量获取端口
port = int(os.environ.get("PORT", 8000))

class ElectronicData(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    timestamp: Optional[str] = None
    location: Optional[str] = None
    battery_level: Optional[float] = None

received_data = []

@app.get("/")
def read_root():
    return {
        "message": "电子数据接收API已启动", 
        "status": "running",
        "endpoints": {
            "接收数据": "/receive (POST)",
            "查看数据": "/data (GET)", 
            "统计信息": "/stats (GET)"
        }
    }

@app.post("/receive")
async def receive_electronic_data(data: ElectronicData):
    """接收电子设备数据"""
    try:
        receive_time = datetime.datetime.now().isoformat()
        
        record = {
            **data.dict(),
            "received_at": receive_time,
            "data_id": f"data_{len(received_data) + 1}"
        }
        
        received_data.append(record)
        
        return {
            "status": "success",
            "message": "数据接收成功",
            "data_id": record["data_id"],
            "received_at": receive_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据格式错误: {str(e)}")

@app.get("/data")
def get_all_data():
    """获取所有数据"""
    return {
        "total_count": len(received_data),
        "data": received_data
    }

@app.get("/stats")
def get_statistics():
    """获取统计信息"""
    device_stats = {}
    for item in received_data:
        device_id = item.get("device_id")
        device_stats[device_id] = device_stats.get(device_id, 0) + 1
    
    return {
        "total_data_count": len(received_data),
        "device_statistics": device_stats
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)