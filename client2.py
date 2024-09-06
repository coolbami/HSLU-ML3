import influxdb_client
from pathlib import Path  
import pandas as pd
from influxdb_client.client.write_api import SYNCHRONOUS
filepath = Path('/home/nganou/Documents/CASML/data/data/MlData.csv')
bucket = "test"
org = "test"
token = "qbaUYyf3qvRCChGFsRvCXAq291u3c_t8SHfzTsJUyHMouFUakqtV_YwQgCTMRytO_-H-pxsgQUcazESAp-0rJw=="
# Store the URL of your InfluxDB instance
url="https://us-west-2-1.aws.cloud2.influxdata.com"

client = influxdb_client.InfluxDBClient(
    url="http://192.168.1.107:8086",
    token=token,
    org=org
)

# Query script
query_api = client.query_api()
query = 'from(bucket:"test")\
|> range(start: -30d)\
|> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")\
|> filter(fn: (r) => r["_field"] == "temperature")\
|> filter(fn: (r) => r["host"] == "crc-lz7xw-master-0")\
|> filter(fn: (r) => r["topic"] == "zurich/NO")\
|> yield(name: "mean")'
result = client.query_api().query_data_frame(query=query, org=org, data_frame_index=['_time']) 
print(result['_value'].head())
result.info()
result.to_csv(filepath)
print(result)
