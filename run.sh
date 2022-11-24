#!/bin/bash

setup() {
  echo "Creating docker networks for Kafka and Cassandra ⏳";

  docker network create kafka-network

  docker network create cassandra-network 

  echo "=> Starting the Cassandra container ⏳";

  docker-compose -f cassandra/docker-compose.yml up -d

  echo "Start the Kafka container ⏳";

  docker-compose -f kafka/docker-compose.yml up -d

  # echo "Run bash inside kafka connect";

  # docker exec -it kafka-connect bash ./start-and-wait.sh

  echo "=> Setup Done. ✅";
}

#### Start process ####
start() {
  echo "Starting OpenWeather Producer 🌤️";

  docker-compose -f owm-producer/docker-compose.yml up -d

  echo "=> OpenWeather Producer launched! ✅";

  echo "Starting Faker Producer 🎭";

  docker-compose -f faker-producer/docker-compose.yml up -d

  echo "=> Faker Producer launched! ✅";

  echo "Starting Binance Producer 📰";

  docker-compose -f binance-producer/docker-compose.yml up -d

  echo "=> Binance Producer launched! ✅";

  echo "Starting all the consumers 🛍️";

  cd consumers

  docker build -t consumer . 

  cd ..

  docker-compose -f consumers/docker-compose.yml up -d

  echo "=> All Consumers launched! ✅";

  echo "Starting data visualization notebook 📊";

  docker-compose -f data-vis/docker-compose.yml up -d

  echo "=> Data Visualization launched! ✅";

  echo "=> Start Done. ✅";
}

# Stop process
stop() {
  echo "Stopping all Containers 🐳";

  docker-compose -f data-vis/docker-compose.yml down 

  docker-compose -f consumers/docker-compose.yml down          

  docker-compose -f owm-producer/docker-compose.yml down

  docker-compose -f faker-producer/docker-compose.yml down   

  docker-compose -f binance-producer/docker-compose.yml down

  docker-compose -f kafka/docker-compose.yml down  

  docker-compose -f cassandra/docker-compose.yml down

  docker network rm kafka-network 

  docker network rm cassandra-network 

  echo "=> Stop DONE ✅";
}

# Build process
build() {
  echo "Pre-building Docker Image 📦";

  # Cassandra
  echo -n "Do you want to build the image for bootstrapcassandra? (y/N) > "
  read -r CASS_OPTION

  if [ "$CASS_OPTION" == "y" ]
  then
    docker build -f cassandra/Dockerfile -t bootstrapcassandra:latest ./cassandra
  fi

  # kafka_connect
  echo -n "Do you want to build the image for kafka_connect? (y/N) > "
  read -r KAFKA_OPTION

  if [ "$KAFKA_OPTION" == "y" ]
  then
    docker build -f kafka/connect.Dockerfile -t kafka_connect:latest ./kafka
  fi

  # owm-producer_openweathermap
  echo -n "Do you want to build the image for owm-producer_openweathermap? (y/N) > "
  read -r OWM_OPTION

  if [ "$OWM_OPTION" == "y" ]
  then
    docker build -f owm-producer/Dockerfile -t owm-producer_openweathermap:latest ./owm-producer
  fi

  # faker-producer_faker
  echo -n "Do you want to build the image for faker-producer_faker? (y/N) > "
  read -r FAKER_OPTION

  if [ "$FAKER_OPTION" == "y" ]
  then
    docker build -f faker-producer/Dockerfile -t faker-producer_faker:latest ./faker-producer
  fi

  # binance-producer_binance
  echo -n "Do you want to build the image for binance-producer_binance (y/N) > "
  read -r BINANCE_OPTION

  if [ "$BINANCE_OPTION" == "y" ]
  then
    docker build -f ./binance-producer/Dockerfile -t binance-producer_binance:latest ./binance-producer
  fi  

  # consumer
  echo -n "Do you want to build the image for consumer? (y/N) > "
  read -r CONSUMER_OPTION

  if [ "$CONSUMER_OPTION" == "y" ]
  then
    docker build -f consumers/Dockerfile -t consumer:latest ./consumers
  fi

  # data-vis
  echo -n "Do you want to build the image for data-vis? (y/N) > "
  read -r DASH_OPTION

  if [ "$DASH_OPTION" == "y" ]
  then
    docker build -f data-vis/Dockerfile -t data-vis:latest ./data-vis
  fi

  # Cleaning up dangling images after build
  echo "Cleaning up dangling images after build...";

  docker image prune

  echo "=> Build DONE. ✅";
}

# Clean process
clean() {
  echo "Cleaning Docker 🗑️";

  docker container prune  # remove stopped containers, done with the docker-compose down 

  docker volume prune  # remove all dangling volumes (delete all data from your Kafka and Cassandra) 

  docker image prune -a  # remove all images (help with rebuild images) 

  docker builder prune  # remove all build cache (you have to pull data again in the next build) 

  docker system prune -a  # basically remove everything 

  echo "=> Clean DONE ✅";
}

execute() {
  local task=${1}
  case "${task}" in
    build)
      build
      ;;
    start)
      start
      ;;
    setup)
      setup
      ;;
    stop)
      stop
      ;;
    bash)
      # shellcheck disable=SC1091
      source ./container-bash.sh
      ;;
    clean)
      clean
      ;;
    *)
      err "invalid task: ${task}"
      usage
      exit 1
      ;;
  esac
}

err() {
    echo "$*" >&2
}

usage() {
    err "$(basename "$0"): [build|setup|start|stop|bash|clean]"
}

main() {
  if [ $# -ne 1 ]
  then
    usage; 
    exit 1; 
  fi
  local task=${1}
  execute "${task}"
}

main "$@"