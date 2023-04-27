# Distributed Systems Project (Distributed Database with atomic transactions via a 2 PC commit protocol implementation)

**Topic Name**: Distributed Two-Phase Commit Protocol for atomic transactions
**Team Number**: 37
**Team members**: Anmol Agarwal, Shrey Gupta, Ashwin Mittal

### What problem are we trying to solve and why is it important to solve it ?
Let’s consider the consistency problem that arises when executing a distributed transaction, i.e. a transaction that reads or writes data on multiple nodes. The data on those nodes may be:
1) Replicas of the same dataset
2) Different parts of a larger dataset; a distributed transaction applies in both cases.

**Maintaining atomicity in distributed transactions:** A key property of a transaction is atomicity. When a transaction spans multiple nodes, we still want atomicity for the transaction as a whole: that is, either all nodes must commit the transaction and make its updates durable, or all nodes must abort the transaction and discard or roll back its updates. Thus, we need agreement among the nodes on whether the transaction should abort or commit.

##### Properties of Atomic commitment: 
* A transaction either commits or aborts
* If it commits, its updates are durable
* If it aborts, it has no visible side-effects
* If the transaction updates data on multiple nodes, this implies:
    * Either all nodes must commit, or all must abort
    * If any node crashes, all must abort


### Brief details on setup and directory structure
For communication among the various processes, we use the gRPC framework.



* `code/txn_coord.py`: Transaction coordinator which receives transaction details from the client and monitors the transaction across all the distributed databases. It listens on PORT `50049`
* `code/site_server.py`: These are the transaction managers present on the different sites. Depending on the site number, they listen from port `50050` onwards
* `code/client.py`: This code is meant to simulate the client which is generating the transactions to be performed on the database.
* `code/protos_dir/site_socket.proto`: the protocol buffer file which contains the 'message types' and 'interfaces' used for communication between the various processes. 



### How to Run
#### Client
```bash=
python client.py <TESTCASE to be tested on>
```

#### Coordinator
```bash=
python txn_coord.py
```


#### Site servers
```bash=
python site_server.py <SERVER_ID>
```

#### Building communication interface using Protocol Buffers
Run the below command from the `code` directory.
```bash=
python -m grpc_tools.protoc -I./protos_dir --python_out=. --pyi_out=. --grpc_python_out=. ./protos_dir/site_socket.proto
```

#### Testcases
The testcases can be found in: `testcases` directory.
##### Sample testcase.
```
T1 3
0_shrey 4 5
0_pratyush 1 7
1_anmol 4 5 9
##################
T2 4
0_shrey 0 1
0_pratyush 1 6
1_anmol 1 2
1_gurkirat 3
#################
T3 2
1_anmol 1 2
0_pratyush 2 6
```
`T{i}` represents the transaction number. Each transcation has n participants whose details have been given on the following n lines. Each line `j` contains name of the server to run on (can be automatically calulated), the name of the person and the list of items purchased.

#### References
* Lecture Notes by Dr Lini
* Distributed Systems Notes by Prof Martin Klepmann (University of Cambridge)
* Section 21.13 of Database Management Systems by Johannes Gehrke and Raghu Ramakrishnan
* Section 20.5 of DATABASE SYSTEMS by Hector Garcia-Molina, Jeffrey D. Ullman, Jennifer Widom
* Distributed Systems by Tanenbaum
