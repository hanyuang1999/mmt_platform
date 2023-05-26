docker rm -f sensorhub_test
docker run --restart=always  -v $PWD/start.sh:/start.sh -v $PWD:/sensorhub_web_toker/web_toker -v /lib/modules:/lib/modules -v /etc/default:/etc/default -v /home/mm/Downloads/calib:/calib -v /dev/:/dev/ -v /etc/localtime:/etc/localtime:ro -e PYTHONPATH=:/sensorhub_web_toker/web_toker/toker_UI/Sensorhub_Test  --name sensorhub_test --ipc=host --add-host `hostname`:127.0.0.1 --add-host foreign:192.168.1.10 --add-host fleet:192.168.2.150 -e CAR_TYPE=Devcar --cap-add SYS_TIME --net=host --privileged=true --entrypoint=/sbin/init -d artifactory.momenta.works/docker-momenta/ve-docker/sensorhub_test:v1.6
docker exec -it sensorhub_test bash 

# docker cp ./sensorhub_web_toker/web_toker  name:/sensorhub_web_toker/web_toker