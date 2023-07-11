import pytest
import asyncio
import websockets
import json
import time

async def log_socket(cur_step, remark):
        async with websockets.connect("ws://10.8.146.24:19799") as ws:
            data = {
                "cur_step": cur_step,
                "remark": remark
            }
            message = json.dumps(data)
            await ws.send(message)
            time.sleep(2)

async def result_socket(test_name, result_status, result_remark):
        async with websockets.connect("ws://10.8.146.24:19799") as ws:
            log_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            data = {
                "log_time": log_time,
                "test_name": test_name,
                "result_status": result_status,
                "result_remark": result_remark
            }
            message = json.dumps(data)
            await ws.send(message)
            time.sleep(2)