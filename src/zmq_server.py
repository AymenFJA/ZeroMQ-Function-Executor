#!/bin/python
from multiprocessing import Pool
import multiprocessing as mp
import multiprocessing
import socket
import sys
import os
import argparse
import json
import pickle
import ast
import importlib
import contextlib

def execute(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        
        while True:
            data = connection.recv(1024)
            if data == "":
                break
            logger.debug("Data Received  %r", data)
            rec_data=json.loads(data)
            mod=rec_data[0]
            exec "import {}".format(mod)
            cmd = (rec_data[1])
            std = eval(compile(cmd, '<string>', 'eval'))
            serial = json.dumps(std)
            connection.send(serial)
            logger.debug("Sending the result back ...")

    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

    #return queue()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        output = mp.Queue()
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        
        
        conn, address = self.socket.accept()
        self.logger.debug("Got connection")
        NumTask=10
        process = [mp.Process(target=execute, args=(conn,address)) for x in range(NumTask)]
        self.logger.debug("Submitting Tasks %r", process)
        for p in process:
            p.start()
        
        results = [output.get() for p in process]
        print('results are ', results)
        #process = [multiprocessing.Process(target=execute, args=(conn, address)) for x in range(NumTask)]
        #process.daemon = True
        #process.start()
        #results = [output.get() for p in process]
            

    

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server("0.0.0.0", 9000)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")

