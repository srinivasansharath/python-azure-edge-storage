This module is designed to run as an iothub module. Once it is initilized and running on the edge, it recevies any data sent to it on "input1" and stores it to the Azure blob storage (either local or to the cloud)

Steps to get it working:
1. Ideally no changes are required in the code, most of the customizations are available thru environment variables.
2. To build the docker image, open the build.sh file and update the Docker URL and image name
3. The build.sh file will also push the directory to the desired registery
4. In IotHub, and this image as a new iot module. Give it a module name and url for the docker registry along with the password
5. Configure the following parameters as environment variables:

LOCAL_STORAGE_CONN_STR - the connection string to the Azure blob storage on the edge. This variable is mandatory, if not provided, the code will exit. It is typically in the format - DefaultEndpointsProtocol=http;AccountName=<account name>;AccountKey=<key in base64>;BlobEndpoint=http://AzureBlobStorageonIoTEdge:11002/<account name>;

LOCAL_STORAGE_CONTAINER_NAME - A container name that will be created to store the blobs; this variable is optional, if not provided it will default to 'iothubdata'.

LOCAL_STORAGE_BLOB_NAME_PREFIX - A prefix for the blob name, the code will add a milisecond timestamp to this prefix. This variable is optional, if not provided it will default to 'data_'.

ENABLE_LOGS - specfies if extended logs are to be enabled, optional parameter, if not provided it will default to 'True'. If you want to disable the logs, please provide 'False'

6. Configure a route, so that iot data can reach this module, following is an example to direct data from the azure Simulated Temp sensor module to this module (sendrecv): 
FROM /messages/modules/SimulatedTemperatureSensor/outputs/temperatureOutput INTO BrokeredEndpoint("/modules/sendrecv/inputs/input1")
