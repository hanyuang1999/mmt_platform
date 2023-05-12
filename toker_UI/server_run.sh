#!/bin/sh
function cleanup {
    echo "Stopping Python processes..."
    kill $PID1 $PID2 $PID3
}
# 当收到退出信号时执行cleanup函数
trap cleanup EXIT

# 运行1.py和2.py并记录它们的进程ID
python server_folder.py &
PID1=$!
python server_socket.py &
PID2=$!
python toker_app.py &
PID3=$!

# 等待所有子进程完成（如果有一个手动停止，其他子进程也会被终止）
wait $PID1 $PID2 $PID3