#!/bin/sh
terminate_processes() {
    echo "Terminating both Python processes..."
    pkill -2 -f server_folder.py
    pkill -2 -f server_socket.py
    pkill -2 -f toker_app.py
}
# 当收到退出信号时执行cleanup函数
trap 'terminate_processes' SIGINT

python server_folder.py &

python server_socket.py &

python toker_app.py &

wait