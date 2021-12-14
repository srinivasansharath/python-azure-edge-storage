import time
import os
import sys
import asyncio
import threading
import io
from six.moves import input
from azure.iot.device.aio import IoTHubModuleClient
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobClient

# ------ Logging ------
def init_logging():
    import logging
    logger = logging.getLogger('azure.storage.blob')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    print(f"Logger enabled for ERROR={logger.isEnabledFor(logging.ERROR)}, " \
        f"WARNING={logger.isEnabledFor(logging.WARNING)}, " \
        f"INFO={logger.isEnabledFor(logging.INFO)}, " \
        f"DEBUG={logger.isEnabledFor(logging.DEBUG)}")
# ------------

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The code requires python 3.5.3+. Current version of Python: %s" % sys.version )

        # Initilize Environment Variables
        blob_conn_str = os.getenv('LOCAL_STORAGE_CONN_STR')
        if not blob_conn_str:
            raise Exception("Env Varible LOCAL_STORAGE_CONN_STR is not set, exiting.. ")

        container_name = os.getenv('LOCAL_STORAGE_CONTAINER_NAME')
        if not container_name:
            print("Env Varible LOCAL_STORAGE_CONTAINER_NAME is not set.. using default")
            container_name = "iothubdata"

        blob_name_prefix = os.getenv('LOCAL_STORAGE_BLOB_NAME_PREFIX')
        if not blob_name_prefix:
            print("Env Varible LOCAL_STORAGE_BLOB_NAME_PREFIX is not set.. using default")
            blob_name_prefix = "data_"

        enable_logs = os.getenv('ENABLE_LOGS')
        if enable_logs.lower() == "false":
            print("Logs disabled..")
            enable_logs = False
        else:
            # By default logs are enabled
            print("Logs enabled..")
            enable_logs = True
            init_logging()

        print("blob_conn_str:",blob_conn_str) #TODO: comment this line for security reason
        print("container_name:", container_name)
        print("blob_name_prefix:", blob_name_prefix)

        # Create the Azure Storage Container
        try:
            container_client  =  ContainerClient.from_connection_string(conn_str=blob_conn_str, container_name=container_name, logging_enable=enable_logs)
            if container_client.exists():
                print("Container %s already exists, lets continue.." % container_name)
            else:
                print("Container %s does not exist, creating a new one" % container_name)
                container_client.create_container()
        except Exception as e:
            print ( "Container create Exception: %s" % e )

        # Initilize IotHub listener
        module_client = IoTHubModuleClient.create_from_edge_environment()
        await module_client.connect()

        # ---- iothub listener loop ----
        async def iothub_listener(module_client):
            while True:
                print("Awaiting iothub message..")
                input_message = await module_client.receive_message_on_input("input1")
                data = io.BytesIO(input_message.data)
                # validate
                print (data.read())
                data.seek(0)

                # Upload to storage
                blob_name=blob_name_prefix + str(round(time.time() * 1000))
                blob = BlobClient.from_connection_string(conn_str=blob_conn_str, \
                        container_name=container_name, \
                        blob_name=blob_name, \
                        logging_enable=enable_logs)
                blob.upload_blob(data)
                print("Uploaded to blob: %s" % blob_name)
                print("Processed iothub message..\n\n")
        # ---- -----

        # ---- Secondary loop for user interrupt ---- 
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(100)
        # ---- ----

        # Schedule the iothub listener task
        listeners = asyncio.gather(iothub_listener(module_client))

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)
        await user_finished # program will loop here until user interruption

        # Cancel listening
        listeners.cancel()

        # Disconnect from iothub
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())

