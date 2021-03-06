#!/usr/bin/env python
# encoding: utf-8
"""
@author: zhuangxu
@email: zhuangxu0@gmail.com
@time: 2019/1/4 19:50
@desc:
"""

import ast
import sys
import time
import getopt
import json

from scmsimagelib import connection
from scmsimagelib import receiver
from scmsimagelib import sender


global chain
global service
service = "score"


def main(args):
    print("@@@@  Start service score  @@@@@")
    message_server = ""

    global chain
    global service
    chain = None

    try:
        opts, args = getopt.getopt(args, "hs:c:", ["help", "server=", "chain="])
    except getopt.GetoptError:
        print("Error: score.py -s <server ip> -c <chain name>")
        print("Or score.py --server=<server ip> --chain=<chain name>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("score.py -s <server ip> -c <chain name>")
            print("Or score.py --server=<server ip> --chain=<chain name>")
            sys.exit()
        elif opt in ("-s", "--server"):
            message_server = arg
            # print("server : %s" % message_server)
        elif opt in ("-c", "--chain"):
            chain = arg
            # print("chain : %s" % chain)

    # check the args
    if not message_server or not chain:
        print("Error: server ip and chain name can't be none")
        sys.exit(2)

    # init pika connection and start receiving message
    connection.SERVER = message_server
    connection.get_client(message_server)
    receiver.receive_message(chain, service, score)


def score(ch, method, properties, body):
    global chain
    global service
    t_in = time.time()
    # print("[In] chain: %s; service: %s \n" % (chain, service))

    # mock real time-consuming
    time.sleep(0.1)

    body_dict = ast.literal_eval(body)
    method_name = body_dict.get('method')
    parameter = body_dict.get('parameter')
    content = body_dict.get('content')

    # send message to next service
    if 'query_score' == method_name:
        query_score(body_dict)

    ch.basic_ack(delivery_tag=method.delivery_tag)

    # print("[Out] chain: %s; service: %s \n" % (chain, service))
    t_out = time.time()
    print("Score time:", str(t_out - t_in))


def query_score(body_dict):
    # record time msec
    t_start = int(time.time() * 1000)
    message = {"uuid": body_dict.get("uuid"), "chain": chain, "gw_time": body_dict.get("gw_time"),
               "books_time": body_dict.get("books_time"), "review_time": body_dict.get("review_time"),
               "score_time": t_start}
    next_service = "gw"
    sender.send_message(str(message), chain, next_service)
    print("return message to gw \n")


if __name__ == "__main__":
    main(sys.argv[1:])
