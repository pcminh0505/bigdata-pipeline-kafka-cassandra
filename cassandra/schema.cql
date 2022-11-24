CREATE TABLE weatherreport (
  forecastdate TIMESTAMP,
  location TEXT,
  description TEXT,
  temp FLOAT,
  feels_like FLOAT,
  temp_min FLOAT,
  temp_max FLOAT,
  pressure FLOAT,
  humidity FLOAT,
  wind FLOAT,
  sunrise BIGINT,
  sunset BIGINT,
  PRIMARY KEY (location, forecastdate)
);

CREATE TABLE fakerdata (
  username TEXT,
  name TEXT,
  email TEXT,
  phone_number TEXT,
  address TEXT,
  company TEXT,
  job TEXT,
  license_plate TEXT,
  year INT,
  safe_color_name TEXT,
  PRIMARY KEY (username, phone_number)
);

CREATE TABLE binancedata (
  datetime TIMESTAMP,
  pair TEXT,
  open_price DOUBLE,
  close_price DOUBLE,
  high_price DOUBLE,
  low_price DOUBLE,
  volume DOUBLE,
  trades DOUBLE,
  PRIMARY KEY (datetime, pair)
);