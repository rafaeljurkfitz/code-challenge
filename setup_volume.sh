#!/bin/bash

VOLUME_NAME="data_inicial_pipeline"

LOCAL_FOLDER="//e//Users//Rafael//Documents//Python//code-challenge//data"

docker volume create $VOLUME_NAME

docker run --rm -v $VOLUME_NAME://data -v "$LOCAL_FOLDER":/origem alpine \
    sh -c "cp -r /origem/order_details.csv /data/"

echo "Volume $VOLUME_NAME configurado com sucesso!"

VOLUME_NAME_2="dataset_filesystem"

docker volume create "$VOLUME_NAME_2"

docker run --rm -v "$VOLUME_NAME_2":/data busybox sh -c "
    mkdir -p /data/csv /data/postgres
"
