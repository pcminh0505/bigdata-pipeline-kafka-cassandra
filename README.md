# Data Pipeline with Docker, Kafka, and Cassandra

The resources in this GitHub can be used to deploy an end-to-end data pipeline on your local computer using Docker containerized Kafka (data streaming), Cassandra (NoSQL database) and Jupyter Lab (data analysis visualization).

This bases on the repo https://github.com/salcaino/sfucmpt733/tree/main/foobar-kafka Substantial changes and bug fixes have been made.

## ⚙️ Installation and Launch Script

### 🔸 Pre-requisite

You need to obtain the API from [OpenWeatherMap API](https://openweathermap.org/api) and Binance API (please follow [Getting Started with python-binance](https://python-binance.readthedocs.io/en/latest/overview.html)) for more detail.

After successfully obtaining the API, please create new files `openweathermap_service.cfg` and `binance_service.cfg` based on the `...-test.cfg` files provided.

### 🔺 Known issue on MacOS M1 with Docker

There will be `kafka-connect` and `kafka-manager` containers will be run in an unstable condition due to incompatibility of M1 Chip with Docker. Please check the tag `Troubleshoot` for M1 unstable condition in the recommended flow.

### 📄 Script Description

`run.sh` will help you to start the project more easily.
**Note** In MacOS, you may need to grant permission to run the file

```bash
chmod +x ./run.sh
```

```bash
./run.sh [build|setup|start|stop|bash|clean]
```

- **build**: automatically build the according image to the required container for the project (can be selected with y/N options)
- **setup**: automatically setup Cassandra and Kafka (including Kafka Connect) sequentially and effectively link necessary services together for a functional flow
- **start**: automatically launch the producers and consumers.
- **stop**: automatically stop all running containers and remove networks
- **bash**: ask for the name of the container you want to access and open an interactive bash (for Cassandra container, there's an extra option for accessing CQLSH directly)
- **clean**: remove all pre-built images

### 🧬 Recommended flow:

Make sure Docker 🐳 is running in your local machine before executing the below flow

0. (Optional) Pre-`build` all the images first

```bash
./run.sh build
```

1. `setup` Kafka & Cassandra network

```bash
./run.sh setup
```

2. Kafka-Manager front end is available at http://localhost:9000 (you may need to wait a while to get this online - please check the container's log with `bash`). Create a cluster with `Cluster Zookeeper Hosts` = `zookeeper:2181`

> For first-time user, username = admin, password = bigbang to access the site

3. `Troubleshoot` Check for the `kafka/connect` container. If the `./start-and-wait.sh` script were down (not successfully create sink and return HTML error 404), please retry with the below command. You need to make sure that the sink connection was established. Otherwise Cassandra cannot receive any data.

```bash
docker exec -it kafka-connect bash ./start-and-wait.sh
```

`Troubleshoot`: If the **"Kafka Connect listener HTTP state: 000"** took so much time, jump to step 6 to `stop` all containers and retry from step 1.

4. `Start` the producers and consumers

```bash
./run.sh start
```

5. Access any container's shell with `bash`. Cassandra's shell is already supported with a shortcut to `cqlsh`

```bash
./run.sh bash
```

`Troubleshoot`: Please always check log on `kafka-connect` at this time. If it stop for a long time, jump to step 6 to `stop` all containers and retry from step 1. (This should happen once only)

6. After finish running, `stop` all the containers

```bash
./run.sh stop
```

or `clean` everything

```bash
./run.sh clean
```

## 🧱 Pipeline's containers and architecture

<div align="center">
  <img src="https://i.imgur.com/r4qZb9N.png" alt="docker-container">
</div>
