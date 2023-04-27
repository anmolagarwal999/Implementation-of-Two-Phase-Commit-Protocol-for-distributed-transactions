from __future__ import print_function

from concurrent import futures
import logging
import os
import sys
import time
import grpc
from copy import deepcopy
from typing import Dict, Tuple, List
import json

#######################
# import protocol buffers
import site_socket_pb2 as site_socket_pb2
import site_socket_pb2_grpc as site_socket_pb2_grpc
EMPTY_MSG = site_socket_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
#########################


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    colors = [OKBLUE, OKCYAN, OKGREEN]


def read_testcase_file(tc_num: int) -> List[Dict]:

    txn_base_dir = "../testcases/txns"
    tc_input_file_path = os.path.join(txn_base_dir, f"tc_{tc_num}.txt")

    with open(tc_input_file_path, 'r') as fd:
        all_lines = [x.strip() for x in fd.readlines()]
    curr_line_id = 0
    txn_df = []
    while curr_line_id < len(all_lines):
        txn_obj = {'txn_name': "", "txn_details": dict()}
        # print("FIRST LINE is")
        # print(all_lines[curr_line_id].split(
        #     " "))
        txn_obj['txn_name'], num_people_involved = all_lines[curr_line_id].split(
            " ")
        curr_line_id += 1
        num_people_involved = int(num_people_involved)

        for _i in range(num_people_involved):
            all_tokens = all_lines[curr_line_id+_i].split(" ")
            assert (len(all_tokens) > 1)
            person_name = all_tokens[0]
            items_ordered = sorted(all_tokens[1:])
            assert (sorted(list(set(items_ordered))) == items_ordered)

            site_id, customer_name = person_name.split("_")
            site_id = int(site_id)
            if site_id not in txn_obj['txn_details']:
                txn_obj['txn_details'][site_id] = dict()
            txn_obj['txn_details'][site_id][customer_name] = [
                int(x) for x in items_ordered]
            # assert (person_name not in txn_obj['txn_details'])
            # txn_obj['txn_details'][person_name] = items_ordered
        txn_df.append(deepcopy(txn_obj))
        curr_line_id = curr_line_id + num_people_involved + 1
        # print("#############")
    return txn_df


def connect_to_coordinator():
    COORDINATOR_SOCKET_ID = 50049
    while True:
        try:
            time.sleep(3)
            print("Trying to connect to coordinator at socket: ",
                  COORDINATOR_SOCKET_ID)
            channel = grpc.insecure_channel(
                f'localhost:{COORDINATOR_SOCKET_ID}', options=(('grpc.enable_http_proxy', 0),))
            coord_stub = site_socket_pb2_grpc.CoordinatorSocketStub(channel)
            recovery_status = coord_stub.ping_coordinator(EMPTY_MSG)
            if recovery_status.val == 0:
                continue
            return coord_stub, channel
        except Exception as E:
            print(bcolors.WARNING,
                  f"Unable to connect to coordinator. Error.", bcolors.ENDC)


def run():
    '''
    Client process
    '''
    tc_num = int(sys.argv[1])
    # establish connection with coordinator
    coord_stub, channel = connect_to_coordinator()

    # load the client process with a test case
    tc_df = read_testcase_file(tc_num)
    print("TC DF IS: ", tc_df)
    with open("curr_tc.json", 'w') as fd:
        json.dump(tc_df, fd, indent=2)
    print("Client has read the test case")

    # keep sending Transactions to coordinator one by one
    while len(tc_df) > 0:
        curr_tc = tc_df[0]
        print(
            f"Client planning to send TXN : {curr_tc['txn_name']} to coordinator")

        txn_json = json.dumps(curr_tc)
        try:
            ret_status = coord_stub.perform_transaction(
                site_socket_pb2.TxnGlobalMessage(txn_json=txn_json))

            if ret_status.val == 1:
                print(bcolors.OKGREEN,
                      f"txn {curr_tc['txn_name']} SUCCESS", bcolors.ENDC)
            else:
                print(bcolors.WARNING,
                      f"txn {curr_tc['txn_name']} FAILED", bcolors.ENDC)
            tc_df.pop(0)
            # break

        except:
            print(
                "Some error occurred while sending message to coordinator. Retrying connect.")
            coord_stub, channel = connect_to_coordinator()

        # TODO: REMOVE
        # break

        print("---------------------------")

    channel.close()


if __name__ == '__main__':
    logging.basicConfig()
    run()
