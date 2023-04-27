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
_SOCKET_OFFSET = 50050
CASE = int(os.getenv('testCase', 0))
print("## CASE TO BE HANDLED IS: ", CASE, " ##")
time.sleep(2)


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


class CoordinatorSocketServicer(site_socket_pb2_grpc.CoordinatorSocketServicer):
    """Provides methods that implement functionality of site server."""

    def __init__(self):
        '''
        Initializes the important data structures needed for the coordinator to function.
        Also, creates a new log file if one does not already exist.        
        '''

        self.site_stubs = dict()
        self.site_channels = dict()
        self.txn_payload_dict = dict()
        self.txn_payload_send = dict()

        self.txn_global_verdict_cache = dict()

        self.has_recovered = False

        self.log_file_path = "coord_logs.json"

        # time.sleep(10)

    def init_recover(self):
        if not os.path.exists(self.log_file_path):
            self.setLog({})
            self.has_recovered = True
        else:
            self.coordinator_recover()
            self.has_recovered = True
        # print("Initial logs are: ",self.getLog())

    def coordinator_recover(self):

        df = self.getLog()
        for curr_txn_id, curr_txn_logs in df.items():
            print(bcolors.BOLD, "Coordinator trying to recover from txn: ",
                  curr_txn_id, bcolors.ENDC)
            # decide on which state did the exit happen
            if not curr_txn_logs['already_done']:
                curr_txn_logs['already_done'] = True
                if curr_txn_logs["global_decision_status"] is None:
                    curr_txn_logs["global_decision_status"] = False
                    print(bcolors.BOLD, "Deducing global verdict to be : ",
                          curr_txn_logs["global_decision_status"], bcolors.ENDC)
                self.txn_global_verdict_cache[curr_txn_id] = curr_txn_logs['global_decision_status']

                # loop through valid sites and test for clean ending on all sites
                for _site_id in curr_txn_logs['txn_payload']['txn_details']:
                    self.ensure_clean_exit_on_site(curr_txn_id, _site_id)
            else:
                self.txn_global_verdict_cache[curr_txn_id] = curr_txn_logs['global_decision_status']
            print("Coordinator seems satisfied with the clean up for txn: ",
                  curr_txn_id, "\n####################\n")

        self.setLog(df)

    def getLog(self) -> dict:
        """
        WARN: Should only be called `with wLock:`
        1) going_to_send_prep: (sets True and then moves to send <prep T> to all sites)
        2) global_decision_taken (sets status after a decision has been taken, then moves on to communicate global decisions)
        3) has_recv acked from all
        """

        with open(self.log_file_path, 'r') as fd:
            return json.load(fd)

    def logInit(self, txn_id):
        df = self.getLog()
        assert (txn_id not in df)
        df[txn_id] = dict()
        df[txn_id]['going_to_send_prep'] = False
        df[txn_id]['local_coordinator_decision'] = None
        df[txn_id]['global_decision_status'] = None
        df[txn_id]['txn_payload'] = self.txn_payload_dict[txn_id]
        df[txn_id]['already_done'] = False
        self.setLog(df, from_log_init=True)

    def setLog(self, wal: dict, from_log_init=False):
        """
        WARN: Should only be called `with wLock:`
        """
        with open(self.log_file_path, 'w') as fd:
            json.dump(wal, fd, indent=4)
            assert (os.path.exists(self.log_file_path))

    def ping_coordinator(self, req, _context):
        print(f"Inside ping() for COORDINATOR", flush=True)
        bool_msg = site_socket_pb2.BoolMessage(
            val=1 if self.has_recovered else 0)
        return bool_msg

    def perform_transaction(self, req, _context):

        _tmp = req.txn_json

        _json_obj = json.loads(_tmp)
        txn_id = _json_obj['txn_name']
        print(bcolors.BOLD,
              f"Coordinator has received a request from the client for {txn_id}", bcolors.ENDC)

        assert (self.has_recovered)
        df = self.getLog()
        if txn_id in df:
            _txn_status = df[txn_id]['already_done']
            _txn_verdict = df[txn_id]['global_decision_status']
            assert (_txn_status)
            return site_socket_pb2.BoolMessage(val=_txn_verdict)

        self.txn_payload_dict[txn_id] = _json_obj
        # print("Payload obj is: ", self.txn_payload_dict)

        txn_status = 1

        sites_involved = [
            int(x) for x in self.txn_payload_dict[txn_id]['txn_details'].keys()]
        self.txn_payload_dict[txn_id]['txn_details'] = dict(sorted(
            [(int(x), y) for (x, y) in self.txn_payload_dict[txn_id]['txn_details'].items()]))

        # connect to all the involved sets
        self.connect_to_sites(sites_involved)

        self.prep_local_payload(self.txn_payload_dict[txn_id])

        txn_status = 1 if self.execute_transaction(txn_id) else 0

        return site_socket_pb2.BoolMessage(val=txn_status)

    def connect_to_sites(self, sites_list):
        got_success = True
        for _curr_site_id in sites_list:
            site_socket = _SOCKET_OFFSET+_curr_site_id
            # print("Attempting to connect to: ", site_socket)
            channel = grpc.insecure_channel(
                f'localhost:{site_socket}', options=(('grpc.enable_http_proxy', 0),))
            site_stub = site_socket_pb2_grpc.SiteSocketStub(channel)
            try:
                recovery_status = site_stub.ping_site(EMPTY_MSG)
                self.site_stubs[_curr_site_id] = site_stub
                self.site_channels[_curr_site_id] = channel
                # print("recovery status and type is: ", type(
                #     recovery_status), recovery_status)
                # print("After pinging, recovery status val is: ",
                #       recovery_status.val)
                if recovery_status.val == 0:
                    got_success = False
            except Exception as E:
                # print("Exception is: ")
                print(bcolors.FAIL,
                      f"|Site: {_curr_site_id} UNABLE TO PING.", bcolors.ENDC, flush=True)
                self.site_stubs[_curr_site_id] = None
                self.site_channels[_curr_site_id] = None
                got_success = False

        return got_success

    @staticmethod
    def fetch_items_gen(items_arr):
        for x in items_arr:
            yield x

    @staticmethod
    def fetch_people_orders(people_dict):
        for curr_person in people_dict:
            person_obj = site_socket_pb2.PersonOrders(
                PersonName=curr_person,
                items_ordered=CoordinatorSocketServicer.fetch_items_gen(people_dict[curr_person]))
            yield person_obj

    def prep_local_payload(self, curr_txn):
        '''
        Prepares the payload which is to be sent to various sites during BeginTxn
        '''
        txn_obj = dict()
        txn_obj['txn_id'] = curr_txn['txn_name']
        txn_obj['txn_sites'] = dict()
        for curr_site in curr_txn['txn_details']:
            txn_obj['txn_sites'][curr_site] = site_socket_pb2.TxnLocalDetails(
                txn_id=txn_obj['txn_id'],
                num_people_involved=len(
                    curr_txn['txn_details'][curr_site]),
                people_order_details=CoordinatorSocketServicer.fetch_people_orders(
                    curr_txn['txn_details'][curr_site]),
                other_sites_involved=(int(x)
                                      for x in curr_txn['txn_details'].keys())
            )
            # break

        self.txn_payload_send[txn_obj['txn_id']] = txn_obj

    def calculate_local_verdict(self, txn_id: str):
        '''Coordinator calculates local verdict.'''
        curr_payload = self.txn_payload_dict[txn_id]
        _MAX_ITEM_LIMIT = 10
        with open("txn_for_local_verdict.json", 'w') as fd:
            json.dump(curr_payload, fd, indent=2)
        my_verdict = True
        for curr_site, site_payload in curr_payload['txn_details'].items():
            for curr_cust in site_payload:
                if len(site_payload[curr_cust]) > _MAX_ITEM_LIMIT:
                    my_verdict = False
                    break

        return my_verdict

    def execute_transaction(self, txn_id):

        self.logInit(txn_id)

        # NOTE: Enter stage 1
        ERRONEOUS_SITES = set()
        curr_payload = self.txn_payload_send[txn_id]
        # go through each transaction, prepare `TxnLocalDetails` for each site
        print("Inside ExecuteTransaction() for Txn ", txn_id)
        # print("Payload is: ", curr_payload)
        local_coord_verdict = self.calculate_local_verdict(txn_id)
        # os._exit(1)
        voting_verdicts = dict()

        # -1 stands for the coordinator
        voting_verdicts[-1] = local_coord_verdict
        # print("Current payload is: ", curr_payload)
        _txn_id_message = site_socket_pb2.TxnIDMessage(
            txn_id=txn_id)
        # TC: 1_2 here

        # Add coordinator's local decision here
        log_df = self.getLog()
        log_df[txn_id]['local_coordinator_decision'] = local_coord_verdict
        self.setLog(log_df)
        del log_df
        # #NOTE: Enter Stage 2

        print("Locally, coordinator has taken decision: ", local_coord_verdict)
        # TC: 2_3 here

        # ----------------------------------------------------------------------------------
        ############# BEGIN TXN ##########################

        # print("Keys in stub is: ", self.site_stubs.keys())
        for curr_site, _curr_site_payload in curr_payload['txn_sites'].items():
            if curr_site in ERRONEOUS_SITES:
                continue
            try:
                # print("Sending begnTxn for: ", curr_site)
                self.site_stubs[curr_site].BeginTxn(_curr_site_payload)
                # #NOTE: Enter Stage 3
                # TC: 3_4 here
            except Exception as E:
                ERRONEOUS_SITES.add(curr_site)
                print(
                    bcolors.FAIL, f"Site: {curr_site} failed during BeginTxn | Error: {E}", bcolors.ENDC)

        # #NOTE: Enter Stage 4
        print("Have tried to send BeginTxn() to all sites.")
        # TC: 4_5 here
        # ----------------------------------------------------------------------------------
        ############# PREPARE TXN ##########################
        global_commit = local_coord_verdict
        # Indicate in logs going to send Prep
        # Add prepare log
        log_df = self.getLog()
        log_df[txn_id]['going_to_send_prep'] = True
        self.setLog(log_df)
        del log_df
        # #NOTE: Enter Stage 5
        print("Have written PREP to logs. Now, going to send PrepTxn() to sites.")

        for curr_site, _curr_site_payload in curr_payload['txn_sites'].items():
            if curr_site in ERRONEOUS_SITES:
                voting_verdicts[curr_site] = False
                global_commit = False
                continue
            try:
                local_verdict = self.site_stubs[curr_site].PrepareTxn(
                    _txn_id_message)
                voting_verdicts[curr_site] = local_verdict
                # #NOTE: Enter Stage 6
                if not local_verdict.val:
                    global_commit = False
                if CASE == 11 and txn_id == 'T51' and int(curr_site) == 1:
                    print(bcolors.FAIL, "Artifically crashing TXN COORDINATOR",
                          " CASE: ", CASE)
                    time.sleep(1)
                    os._exit(1)
            except Exception as E:
                ERRONEOUS_SITES.add(curr_site)
                print(
                    bcolors.FAIL, f"Site: {curr_site} failed during PrepTxn |", bcolors.ENDC)
                voting_verdicts[curr_site] = False
                global_commit = False

        print("Have send PrepareTxn() to all sites.")
        if CASE == 9 and txn_id == 'T51':
            print(bcolors.FAIL, "Artifically crashing TXN COORDINATOR",
                  " CASE: ", CASE)
            time.sleep(1)
            os._exit(1)

        # #NOTE: Enter Stage 7

        # Indicate in logs going to send Prep
        log_df = self.getLog()
        log_df[txn_id]['global_decision_status'] = global_commit
        self.setLog(log_df)
        del log_df
        print(bcolors.BOLD,
              f"Written global decision in logs for f{txn_id} | Decision: ", global_commit, bcolors.ENDC)
        # #NOTE: Enter Stage 8

        if CASE == 12 and txn_id == 'T51':
            print(bcolors.FAIL, "Artifically crashing TXN COORDINATOR",
                  " CASE: ", CASE)
            time.sleep(1)
            os._exit(1)

        if CASE == 13 and txn_id == 'T61':
            print(bcolors.FAIL, "Artifically crashing TXN COORDINATOR",
                  " CASE: ", CASE)
            time.sleep(1)
            os._exit(1)
        # -----------------------------------------------------------------------------------
        # Send global verdict to each site
        ############# Send GLOBAL VERDICT TXN ##########################
        _global_verdict_message = site_socket_pb2.GlobalVerdictMessage(
            txn_id=txn_id, global_verdict=site_socket_pb2.GlobalVerdictMessage.GLOBAL_ABORT if not global_commit else site_socket_pb2.GlobalVerdictMessage.GLOBAL_COMMIT)
        # send BeginTxn, send PrepTxn and send GlobalVerdict
        for curr_site in curr_payload['txn_sites']:
            if curr_site in ERRONEOUS_SITES:
                continue
            try:
                self.site_stubs[curr_site].SendGlobalVerdict(
                    _global_verdict_message)
                # #NOTE: Enter Stage 9
                if CASE == 10 and txn_id == 'T51' and int(curr_site) == 1:
                    print(bcolors.FAIL, "Artifically crashing TXN COORDINATOR",
                          " CASE: ", CASE)
                    time.sleep(1)
                    os._exit(1)
            except Exception as E:
                ERRONEOUS_SITES.add(curr_site)
                print(
                    bcolors.FAIL, f"Site: {curr_site} failed during GlobalVerdict |", bcolors.ENDC)

        # #NOTE: Enter Stage 10

        # print("##########################################")
        # break
        for _site_id, curr_channel in self.site_channels.items():
            # Handle this in case the channel has closed
            if curr_channel:
                curr_channel.close()

        #  Cache global commit
        # TODO: Think about consequences if this were done after dealing with erroneous sites
        self.txn_global_verdict_cache[txn_id] = global_commit

        print(bcolors.WARNING,
              f"Sites found crashed are: {ERRONEOUS_SITES}", bcolors.ENDC)
        for curr_error_site in ERRONEOUS_SITES:
            curr_stat = False
            while not curr_stat:
                curr_stat = self.connect_to_sites([curr_error_site])
                time.sleep(5)

        self.site_channels.clear()
        self.site_stubs.clear()

        ####################################
        log_df = self.getLog()
        log_df[txn_id]['already_done'] = True
        self.setLog(log_df)
        del log_df
        print(bcolors.BOLD,
              f"Finally setting `already_done` for txn id: {txn_id}", bcolors.ENDC)

        # return global commit
        return global_commit

    @staticmethod
    def persistent_connect_to_site(site_socket):
        SOCKET_ID = site_socket
        while True:
            try:
                time.sleep(3)
                print("Coordinator trying to connect to site at socket: ", SOCKET_ID)
                channel = grpc.insecure_channel(
                    f'localhost:{SOCKET_ID}', options=(('grpc.enable_http_proxy', 0),))
                site_stub = site_socket_pb2_grpc.SiteSocketStub(channel)
                recovery_status = site_stub.ping_site(EMPTY_MSG)
                if recovery_status.val == 0:
                    continue
                return site_stub, channel
            except Exception as E:
                print(bcolors.WARNING, f"Unable to connect to SITE.", bcolors.ENDC)

    def ensure_clean_exit_on_site(self, txn_id, site_id):
        print(
            f"Trying to ensure clean exit for txn: {txn_id} | site:{site_id} ")
        site_id = int(site_id)
        site_stub, _channel = self.persistent_connect_to_site(
            _SOCKET_OFFSET+site_id)
        curr_exit_stat = False
        while not curr_exit_stat:
            curr_exit_stat_msg = site_stub.fetch_txn_exit_stat(
                site_socket_pb2.TxnIDMessage(txn_id=txn_id))
            curr_exit_stat = bool(curr_exit_stat_msg.val)
            print(
                f"Exit status for site: {site_id} for txn {txn_id}: ", curr_exit_stat)
            time.sleep(2)
        _channel.close()
        return curr_exit_stat

    # rpc respond_to_recovering_client(TxnIDMessage) returns (BoolMessage){}

    def respond_to_recovering_client(self, req, _context):
        print("Responding to a recovering client.")
        txn_id = req.txn_id
        while txn_id not in self.txn_global_verdict_cache:
            pass
        stat = self.txn_global_verdict_cache[txn_id]
        print(
            f"Replying with cached global verdict {stat} to recovering request from some site for txn: ", req.txn_id)
        return site_socket_pb2.BoolMessage(val=1 if stat else 0)


def run():
    '''
    Site servers started listening from PORT 50049 onwards
    '''

    make_new_logs = True
    if len(sys.argv) > 1:
        if int(sys.argv[1]) == 0:
            make_new_logs = False
    if make_new_logs:
        if os.path.exists("coord_logs.json"):
            print("Removing previous logs")
            os.system(f"rm -rf coord_logs.json")

    SOCKET_TO_CONNECT = 50049
    cmd_to_exec = f"kill $(lsof -t -i:{SOCKET_TO_CONNECT})"
    os.system(cmd_to_exec)
    #####################################
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    server_obj = CoordinatorSocketServicer()
    # sys.exit(0)
    site_socket_pb2_grpc.add_CoordinatorSocketServicer_to_server(
        server_obj, server)
    ret_port = server.add_insecure_port(f'[::]:{SOCKET_TO_CONNECT}')
    print(f"Coordinator has started to listen at {SOCKET_TO_CONNECT}")

    server.start()
    server_obj.init_recover()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    run()
