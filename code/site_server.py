from __future__ import print_function

from concurrent import futures
import logging
import os
import sys
import time
import grpc
from typing import Dict, Tuple, List
import json
import shutil
import threading
import sqlite3
# import numpy as np
#######################
# import protocol buffers
import site_socket_pb2 as site_socket_pb2
import site_socket_pb2_grpc as site_socket_pb2_grpc
# import numpy as np
#########################
global server_id, SITE_DB_DIR, CASE
CASE = int(os.getenv('testCase', 0))
print("## CASE TO BE HANDLED IS: ", CASE, " ##")
# time.sleep(2)

_SOCKET_OFFSET = 50050
EMPTY_MSG = site_socket_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

#################################


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

    colors = [OKBLUE, OKCYAN, OKGREEN, BOLD]


class SiteSocketServicer(site_socket_pb2_grpc.SiteSocketServicer):
    """Provides methods that implement functionality of site server."""

    def __init__(self,
                 site_socket_id: int,
                 site_db_dir: str):
        self.site_socket_id = site_socket_id
        self.site_id = self.site_socket_id - _SOCKET_OFFSET
        print(f"__init__ Class for site at socket: {self.site_socket_id}")
        self.site_db_dir = site_db_dir

        # TODO: Populate
        self.local_feasibility = dict()

        # TODO: Populate
        self.txn_payload_recv = dict()
        self.has_recovered = False
        self.log_file_path = os.path.join(
            self.site_db_dir, f"log_file_{self.site_id}.json")
        if not os.path.exists(self.log_file_path):
            # print("FILE DOES NOT EXIST, creating logs at: ", self.log_file_path)
            self.setLog({})
            self.has_recovered = True
        else:
            # TODO: parse txn payload recv
            # TODO: Add recovery here
            self.recover()
            with open("recovered_logs.json", 'w') as fd:
                json.dump(self.txn_payload_recv, fd)
            self.has_recovered = True

        print(bcolors.colors[self.site_id])

    def _timeout(self, txn_id: str):
        # Wait for TIMEOUT_OUT seconds before concluding that the coordinator has crashed
        TIMEOUT_DUR = 10
        time.sleep(TIMEOUT_DUR)

        # TODO: NOTE: Make sure that site supposed to be new leader reaches this for case_3_4

        # check if the transaction has reached a meaningful conclusion
        # TODO: involve locks here
        # for now, see if the transaction has reached a meaningful conclusion here

        print(bcolors.BOLD, f"Site {self.site_id} has not received global decision for txn {txn_id} so far and hence, is pausing for new leader",
              bcolors.ENDC, bcolors.colors[self.site_id])

        # TODO: the local decision needs to be calculated before the minimum site contacts

        # now, inspect the sites involved in the transaction
        sites_in_txn = self.txn_payload_recv[txn_id]['other_sites_involved']
        _new_leader_id = min(sites_in_txn)

        if _new_leader_id != self.site_id:
            # if you are NOT the minimum site involved in the transaction, then wait for the minimum site to contact you
            return
        else:
            print(bcolors.BOLD, f"{self.site_id} is taking over as new leader for txn: {txn_id}",
                  bcolors.ENDC, bcolors.colors[self.site_id])
            # open a connection to all sister sites and find their local verdicts
            self.coordinate_as_new_leader(txn_id, sites_in_txn)
            pass

    @staticmethod
    def fetch_channel_stub(socket_id: int):
        channel = grpc.insecure_channel(
            f'localhost:{socket_id}', options=(('grpc.enable_http_proxy', 0),))
        stub = site_socket_pb2_grpc.SiteSocketStub(channel)
        stub.ping_site(EMPTY_MSG)
        return stub, channel

    def coordinate_as_new_leader(self, txn_id, other_sites: List[int]):
        print(
            f"Site {self.site_id} | new leader for txn {txn_id} among {other_sites}")
        local_decisions_df = dict()
        global_decisions_recv_df = dict()
        have_all_sent_df = dict()
        # TODO:: Be careful not to send a message to own self
        for curr_site_id in other_sites:
            if curr_site_id == self.site_id:
                _local_decision = self.local_feasibility[txn_id]
                # print("Reading logs for leader")
                # fetch logs
                df = self.getLog()
                have_sent = df[txn_id]['has_sent_local_verdict']
                glob_dec_recv = df[txn_id]['global_verdict']
                # print(glob_dec_recv)
                local_decisions_df[curr_site_id] = _local_decision
                global_decisions_recv_df[curr_site_id] = glob_dec_recv
                del df
            else:
                # get a proper socket and channel

                _stub, _channel = self.fetch_channel_stub(
                    _SOCKET_OFFSET+curr_site_id)
                # TODO: NOTE: The decision returned here may be NONE as well (since we may be calling sites which have NOT yet received BeginTxn)
                local_decision = _stub.fetch_local_decision(
                    site_socket_pb2.TxnIDMessage(txn_id=txn_id))
                _channel.close()
                _local_decision = local_decision.local_verdict
                have_sent = local_decision.have_sent_local_verdict
                glob_dec_recv = local_decision.global_verdict_recv

                local_decisions_df[curr_site_id] = None if _local_decision == 2 else bool(
                    _local_decision)
                global_decisions_recv_df[curr_site_id] = None if glob_dec_recv == 2 else bool(
                    glob_dec_recv)
            have_all_sent_df[curr_site_id] = have_sent
        print("local_decisions_df gathered is:", local_decisions_df)
        print("global_decisions_recv_df gathered is:", global_decisions_recv_df)
        print("have_all_sent_df gathered is:", have_all_sent_df)

        all_decs = list(local_decisions_df.values())
        inferred_should_commit = None

        # print(have_all_sent_df.values())
        # if not np.all(have_all_sent_df.values()):
        if False in have_all_sent_df.values():
            print(bcolors.BOLD, "Atleast one site is yet to send LOCAL VERDICT, so aborting",
                  self.reset_color())
            inferred_should_commit = False
        else:
            print(bcolors.BOLD, "All sites have sent local verdict.",
                  self.reset_color())
            global_values_recv_set = set(global_decisions_recv_df.values())
            # check if there is any not None value in received global decisions
            if len(global_values_recv_set) > 2:
                print("ERROR: GLOBAL VALUES OF MORE THAN 2 types received. This is clearly not possible. Debug: ",
                      global_decisions_recv_df)
                os._exit(1)
            else:
                if True in global_values_recv_set:
                    assert (False not in global_values_recv_set)
                    inferred_should_commit = True
                    print(
                        "Atleast one site has received the GLOBAL COMMIT verdict.", self.reset_color())
                elif False in global_values_recv_set:
                    assert (True not in global_values_recv_set)
                    inferred_should_commit = False
                    print(
                        bcolors.BOLD, "Atleast one site has received the GLOBAL ABORT verdict.", self.reset_color())
                else:
                    assert (None in global_values_recv_set)
                    assert (len(global_values_recv_set) == 1)
                    print(
                        bcolors.BOLD, "NO ONE HAS RECEIVED ANY GLOBAL VERDICT.", self.reset_color())

                    # since all sites have sent local_decisions, `all_decs` cannot contain NULL
                    assert (None not in all_decs)
                    # if np.all(all_decs):
                    if not (False in all_decs):
                        # consult coordinator for it's local verdict
                        # TODO: Add consultation code
                        print(
                            bcolors.BOLD, "All sites have LOCAL_COMMIT. So, need to consult coordinator.", self.reset_color())
                        coordinator_verdict = self.query_global_verdict_from_coordinator(
                            txn_id)
                        print(bcolors.BOLD, "Fetched coordinator verdict and found it to be:",
                              coordinator_verdict, self.reset_color())
                        if coordinator_verdict:
                            inferred_should_commit = True
                        else:
                            inferred_should_commit = False
                        pass
                    else:
                        print(
                            bcolors.BOLD, "No need to consult coordinator as a LOCAL_ABORT was found among one of the sites itself.", self.reset_color())
                        # no need to consult coordinator
                        inferred_should_commit = False

        assert (inferred_should_commit is not None)

        global_msg = site_socket_pb2.GlobalVerdictMessage(
            txn_id=txn_id, global_verdict=int(inferred_should_commit))
        for curr_site_id in other_sites:
            if curr_site_id == self.site_id:
                self.communicate_leader_decision(global_msg, None)
            else:
                # get a proper socket and channel

                _stub, _channel = self.fetch_channel_stub(
                    _SOCKET_OFFSET+curr_site_id)
                _stub.communicate_leader_decision(global_msg)
                _channel.close()

        # local decisions have been gathered, now depending on the decisions, we need to decide the global verdict to be sent to all

    def fetch_local_decision(self, res, _context):
        '''
        When the coordinator fails, this function is called by the new leader site to gather the local vedicts of all the participant sites
        '''
        df = self.getLog()
        txn_id = res.txn_id  # NOTE: Correct this
        _local_verdict = None
        have_sent_local_verdict = False
        global_verdict_recv = None
        if txn_id in df:
            if df[txn_id]['local_verdict'] is None:
                _local_verdict = 2  # LOCAL_UNDECIDED
            elif df[txn_id]['local_verdict'] == True:
                _local_verdict = 1  # LOCAL_COMMIT
            else:
                _local_verdict = 0  # LOCAL_ABORT

            if df[txn_id]['global_verdict'] is None:
                global_verdict_recv = 2  # LOCAL_UNDECIDED
            elif df[txn_id]['global_verdict'] == True:
                global_verdict_recv = 1  # LOCAL_COMMIT
            else:
                global_verdict_recv = 0  # LOCAL_ABORT
            have_sent_local_verdict = df[txn_id]['has_sent_local_verdict']
        else:
            _local_verdict = 2
            global_verdict_recv = 2

        print(f"Local verdict at site: {txn_id} is: ", _local_verdict)
        assert (_local_verdict is not None)
        return site_socket_pb2.VerdictMessage(local_verdict=_local_verdict, have_sent_local_verdict=have_sent_local_verdict, global_verdict_recv=global_verdict_recv)

    def communicate_leader_decision(self, req, context):
        '''
        When the coordinator fails, the new leader communicates the decision to sister sites using this function
        '''
        # TODO: NOTE: This decision is being communicated by new leader. However, it is possible that `self.site_id` HAS NOT EVEN RECEIVED the BeginTxn and hence, no entry for this is present in it's logs.
        recv_global_verdict = True if req.global_verdict == 1 else False
        txn_id = req.txn_id

        # fetch logs and decide appropriately
        df = self.getLog()
        if txn_id not in df:
            # print("Was not aware of txn yet but have been made aware by new leader.")
            # print("This is NOT A CASE 2 PC CAN HANDLE. WEAKNESS !")
            os._exit(1)
        if df[txn_id]['acted_on_global']:
            print(f"Have already acted on global for txn: {txn_id}.")
            assert (df[txn_id]['global_verdict'] == recv_global_verdict)
            return EMPTY_MSG

        print(bcolors.BOLD,
              f"Global verdict communicated by new leader for txn {txn_id} is: {recv_global_verdict}", bcolors.ENDC)
        self.SendGlobalVerdict(req, context)
        return EMPTY_MSG

    def query_global_verdict_from_coordinator(self, txn_id) -> bool:
        coord_stub, channel = self.connect_to_coordinator()
        status_here = coord_stub.respond_to_recovering_client(
            site_socket_pb2.TxnIDMessage(txn_id=txn_id))
        status_here = True if status_here.val == 1 else False
        channel.close()
        print(bcolors.BOLD,
              f"For txn: {txn_id}, Global verdict queried from coordinator: ", status_here, self.reset_color())
        return status_here

    def recover(self):
        '''
        Let's recover
        '''

        log_df = self.getLog()

        # AIM: To populate `self.local_feasibility` and `self.txn_payload_recv`
        for curr_txn_id, curr_txn_logs in log_df.items():
            self.txn_payload_recv[curr_txn_id] = curr_txn_logs['payload_recv']
            if curr_txn_logs['local_verdict'] is not None:
                self.local_feasibility[curr_txn_id] = curr_txn_logs['local_verdict']

        for curr_txn_id, curr_txn_logs in log_df.items():
            if (curr_txn_logs['acted_on_global']):
                continue
            if not curr_txn_logs['has_sent_local_verdict']:
                # THIS IS DEFINITELY ABORT
                # NOTHING
                curr_txn_logs['acted_on_global'] = True
                curr_txn_logs['global_verdict'] = False
            else:
                # Have already sent local verdict to the coordinator

                if curr_txn_logs['global_verdict'] is not None:
                    if curr_txn_logs['global_verdict'] == True:
                        # Case 1: Global verdict is GLOBAL COMMIT and NOT YET ACTED
                        if curr_txn_logs['local_verdict'] == True:
                            #   Subcase a) Local verdict is LOCAL COMMIT

                            # act on global commit
                            self.PerformCommit(curr_txn_id)

                            # set 'acted on global commit to true'
                            curr_txn_logs['acted_on_global'] = True
                        else:
                            #   Subcase b: Local verdict is LOCAL ABORT
                            #       NOT POSSIBLE (assert False)
                            print(bcolors.WARNING,
                                  "This should NOT BE HAPPENING ", bcolors.ENDC)
                            assert (False)
                    else:
                        assert (curr_txn_logs['global_verdict'] == False)
                        # Case 2: Global verdict is GLOBAL ABORT and NOT YET ACTED
                        #   Subcase a) Local verdict is LOCAL COMMIT
                        # this is definitely abort, do nothing
                        #   Subcase b: Local verdict is LOCAL ABORT
                        # this is definitely abort, do nothing
                        curr_txn_logs['acted_on_global'] = True
                else:
                    # Case 3: Global verdict NOT received ie None
                    if curr_txn_logs['local_verdict'] == True:
                        #   Subcase a) Local verdict is LOCAL COMMIT
                        # TODO: Think of consequences of deadlock DUE to num_workers in
                        # global verdict needs to be queried
                        curr_txn_logs['global_verdict'] = self.query_global_verdict_from_coordinator(
                            curr_txn_id)
                        if curr_txn_logs['global_verdict'] == True:
                            #       Consult coordinator to find global verdict and act on the global verdict (since coordinator already sent the global verdict to everyone and assumes that everyone would abide by global verdict)
                            self.PerformCommit(curr_txn_id)
                            curr_txn_logs['acted_on_global'] = True
                        else:
                            curr_txn_logs['acted_on_global'] = True

                    else:
                        #   Subcase b: Local verdict is LOCAL ABORT
                        #       This is definitely abort, do nothing
                        assert (not curr_txn_logs['local_verdict'])
                        curr_txn_logs['acted_on_global'] = True

                    pass

        # TODO: DUMP LOGS
        self.setLog(log_df)

    def getLog(self):
        with open(self.log_file_path, 'r') as fd:
            wal = json.load(fd)
            # if self.site_id == 0:
            #         print(bcolors.OKCYAN, "LOADING : ", wal, bcolors.colors[self.site_id])
            return wal

    def setLog(self, wal):
        with open(self.log_file_path, 'w') as fd:
            # print("Dumped at: ", self.log_file_path)
            json.dump(wal, fd, indent=4)
            assert (os.path.exists(self.log_file_path))
            # if self.site_id == 0:
            #     print(bcolors.OKGREEN, "DUmping : ", wal, bcolors.colors[self.site_id])

    def parse_people(self, people_order_details):
        arr = [{"PersonName": x.PersonName, "items_ordered": [
            int(y) for y in x.items_ordered]} for x in people_order_details]
        return arr

    def logInit(self, txn_id, payload_received):
        # with wLock:
        df = self.getLog()
        assert (txn_id not in df)
        df[txn_id] = dict()
        df[txn_id]['begin_txn'] = True
        # print(type(payload_received.people_order_details))
        df[txn_id]['payload_recv'] = {"txn_id": payload_received.txn_id,
                                      "num_people_involved": payload_received.num_people_involved,
                                      "people_order_details": self.parse_people(payload_received.people_order_details),
                                      "other_sites_involved": [int(x) for x in payload_received.other_sites_involved]}
        self.txn_payload_recv[txn_id] = df[txn_id]['payload_recv']
        # df[txn_id]['prep_txn'] = False
        df[txn_id]['local_verdict'] = None
        df[txn_id]['has_sent_local_verdict'] = False
        df[txn_id]['global_verdict'] = None
        df[txn_id]['acted_on_global'] = False
        self.setLog(df)

    def reset_color(self):
        print(bcolors.ENDC, bcolors.colors[self.site_id])
        return ""

    def ping_site(self, req, _context):
        print(f"Inside ping() for {self.site_id}", flush=True)
        bool_msg = site_socket_pb2.BoolMessage(
            val=1 if self.has_recovered else 0)
        # print("bool msg val: is : ", bool_msg.val)
        return bool_msg

    def fetch_customer_file(self, cust_name):
        file_path = os.path.join(self.site_db_dir, f"{cust_name}.json")
        items_have = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as fd:
                items_have = json.load(fd)
        conn = sqlite3.connect(
            f'../dummy_databases/site_databases/db_{self.site_id}.db')
        cursor = conn.execute(
            f"SELECT ITEMS from ORDERS WHERE NAME='{cust_name}';")
        for row in cursor:
            items_have = list(map(int, row[0].split(",")))
        conn.close()
        return items_have

    def write_customer_file(self, cust_name, new_items):
        file_path = os.path.join(self.site_db_dir, f"{cust_name}.json")
        with open(file_path, 'w') as fd:
            json.dump(new_items, fd)
        new_items = list(map(str, new_items))
        conn = sqlite3.connect(
            f'../dummy_databases/site_databases/db_{self.site_id}.db')
        try:
            conn.execute(
                f"INSERT INTO ORDERS (NAME,ITEMS) VALUES ('{cust_name}', '{','.join(new_items)}');")
        except:
            conn.execute(
                f"UPDATE ORDERS set ITEMS = '{','.join(new_items)}' where NAME = '{cust_name}'")
        conn.commit()
        conn.close()

    def evaluate_local_verdict(self, txn_id):
        assert (txn_id in self.txn_payload_recv)
        req = self.txn_payload_recv[txn_id]
        should_commit = True
        for curr_cust_obj in req['people_order_details']:
            cust_name = curr_cust_obj['PersonName']

            items_have = self.fetch_customer_file(cust_name)
            items_buying = [int(x) for x in curr_cust_obj['items_ordered']]
            common_items = set(items_buying).intersection(items_have)
            if len(common_items) > 0:
                print(
                    f"Txn ID: {req['txn_id']} NOT FEASIBLE for : {cust_name} since item limit constraint has been violated.")
                should_commit = False
        return should_commit

    def BeginTxn(self, req, _context):
        print(f"Inside BeginTxn for {self.site_id}")
        # print("Payload received is:", req)
        self.logInit(req.txn_id, req)
        if CASE == 7 and self.site_id == 0 and req.txn_id == 'T1':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)

        # start a timeout thread for this transaction
        if CASE > 8 or CASE == -1:
            threading.Thread(target=self._timeout, args=(req.txn_id, )).start()

        # check feasibility of txn

        # save LOCAL VERDICT
        self.local_feasibility[req.txn_id] = self.evaluate_local_verdict(
            req.txn_id)
        log_file = self.getLog()
        log_file[req.txn_id]['local_verdict'] = self.local_feasibility[req.txn_id]
        self.setLog(log_file)
        print(bcolors.BOLD, f"Local vedict decided for txn_id: {req.txn_id} is: ",
              self.local_feasibility[req.txn_id], bcolors.ENDC, bcolors.colors[self.site_id])

        return EMPTY_MSG

    def PrepareTxn(self, req, _context):
        txn_id = req.txn_id
        print(f"Inside PrepareTxn for {self.site_id} for txn: {txn_id}")
        if CASE == 1 and self.site_id == 0 and txn_id == 'T1':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)
        if CASE == 5 and self.site_id == 0 and txn_id == 'T2':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)
        assert (txn_id in self.local_feasibility)

        log_file = self.getLog()
        log_file[req.txn_id]['has_sent_local_verdict'] = True
        self.setLog(log_file)

        # send saved local verdict
        return site_socket_pb2.BoolMessage(val=self.local_feasibility[txn_id])

    def PerformCommit(self, txn_id):
        # print("KEYS ARE: ", self.txn_payload_recv[txn_id].keys())
        for curr_cust_obj in self.txn_payload_recv[txn_id]["people_order_details"]:
            cust_name = curr_cust_obj["PersonName"]
            items_have = self.fetch_customer_file(cust_name)
            items_buying = [int(x) for x in curr_cust_obj["items_ordered"]]
            common_items = set(items_buying).intersection(items_have)
            assert (len(common_items) == 0)
            items_have.extend(items_buying)
            items_have = sorted(items_have)
            self.write_customer_file(cust_name, items_have)
        print("Commit has been performed and written to database.")
        # print("#################################")

    def SendGlobalVerdict(self, req, _context):
        if CASE == 2 and self.site_id == 0 and req.txn_id == 'T1':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)

        if CASE == 4 and self.site_id == 0 and req.txn_id == 'T2':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)

        print(
            f"Inside SendGlobalVerdict for site: {self.site_id}, txn_id: {req.txn_id}")
        global_verdict = True if req.global_verdict == 1 else False
        print(bcolors.BOLD, "GLOBAL verdict received is: ",
              global_verdict, bcolors.ENDC, bcolors.colors[self.site_id])

        #############
        log_file = self.getLog()
        log_file[req.txn_id]['global_verdict'] = global_verdict
        self.setLog(log_file)
        #############
        print("Global verdict written in log file.")

        if CASE == 3 and self.site_id == 0 and req.txn_id == 'T1':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)

        if CASE == 8 and self.site_id == 0 and req.txn_id == 'T2':
            print(bcolors.FAIL, "Artifically crashing ", self.site_id,
                  " CASE: ", CASE, bcolors.colors[self.site_id])
            time.sleep(1)
            os._exit(1)

        txn_id = req.txn_id

        if global_verdict:
            self.PerformCommit(txn_id=txn_id)
        else:
            # TODO: Shrey is saying tco write some if-else GLOBAL ABORT - GLOBAL COMMIT CODE
            pass

        #############
        log_file = self.getLog()
        log_file[req.txn_id]['acted_on_global'] = True
        self.setLog(log_file)
        #############
        print(
            f"Logged for site: {self.site_id}, txn_id: {req.txn_id} ie `acted_on_global` = True")

        # take action depending on global verdict
        return EMPTY_MSG

    def fetch_txn_exit_stat(self, req, _context):
        txn_id = req.txn_id
        df = self.getLog()
        is_over = False
        if txn_id in df:
            if df[txn_id]['acted_on_global'] == True:
                is_over = True
        print(
            f"Inside fetch_txn_exit_stat | txn: {txn_id} | is_over: {is_over}")
        return site_socket_pb2.BoolMessage(val=int(is_over))

    @staticmethod
    def connect_to_coordinator():
        COORDINATOR_SOCKET_ID = 50049
        while True:
            try:
                time.sleep(3)
                print("LEADER trying to connect to coordinator at socket: ",
                      COORDINATOR_SOCKET_ID)
                channel = grpc.insecure_channel(
                    f'localhost:{COORDINATOR_SOCKET_ID}', options=(('grpc.enable_http_proxy', 0),))
                coord_stub = site_socket_pb2_grpc.CoordinatorSocketStub(
                    channel)

                # TODO: FIXME
                recovery_status = coord_stub.ping_coordinator(EMPTY_MSG)
                # print("Recovery status is: ",recovery_status)
                # if recovery_status.val == 0:
                #     continue
                return coord_stub, channel
            except Exception as E:
                print(
                    bcolors.WARNING, f"Unable to connect to coordinator. Error. Retry.", bcolors.ENDC)


def serve():
    global server_id, SITE_DB_DIR
    server_id = int(sys.argv[1])
    _DELETE_SITE_DB = True
    if len(sys.argv) == 3:
        if int(sys.argv[2]) == 0:
            _DELETE_SITE_DB = False

    SOCKET_TO_CONNECT = _SOCKET_OFFSET + server_id
    cmd_to_exec = f"kill $(lsof -t -i:{SOCKET_TO_CONNECT})"
    os.system(cmd_to_exec)

    SITE_DB_DIR = os.path.join(
        "../dummy_databases/site_databases", f"db_{server_id}")

    #######################
    if not os.path.exists(SITE_DB_DIR):
        os.makedirs(SITE_DB_DIR)

    if _DELETE_SITE_DB:
        shutil.rmtree(SITE_DB_DIR, ignore_errors=True)
        os.system(
            f'rm -rf ../dummy_databases/site_databases/db_{server_id}.db')
        # os.system(f"rm -rf coord_logs.json")
        os.makedirs(SITE_DB_DIR)

    if not os.path.exists(f'../dummy_databases/site_databases/db_{server_id}.db'):
        conn = sqlite3.connect(
            f'../dummy_databases/site_databases/db_{server_id}.db')
        conn.execute('''CREATE TABLE ORDERS
            (NAME           TEXT PRIMARY KEY   NOT NULL,
            ITEMS        TEXT);''')
        conn.close()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # sys.exit(0)
    site_socket_pb2_grpc.add_SiteSocketServicer_to_server(
        SiteSocketServicer(site_socket_id=SOCKET_TO_CONNECT, site_db_dir=SITE_DB_DIR), server)
    ret_port = server.add_insecure_port(f'[::]:{SOCKET_TO_CONNECT}')
    print(f"Starting to listen at {SOCKET_TO_CONNECT}")

    #######################

    server.start()
    # print("RET VAL IS: ", ret_port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
