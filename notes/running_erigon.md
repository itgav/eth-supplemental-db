### RUN RPC DAEMON

- Can access the Erigon local DB in multiple ways, I'll be using the RPC pathway
  - !!! most of the code needs access to a node via RPC to run. Otherwise, will get an error similar to that of below:
    - "ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it"
- To access via RPC pathway, need to have the RPC Daemon running in a separate terminal instance while you query
  - I'm using Windows PowerShell and running as admin

- Run RPC Daemon:
  - open a separate terminal instance
    - Windows PowerShell run as Administrator
  - cd to "erigon" folder
    - terminal: cd c:/erigon_versions/erigon_23.06.27_stable/erigon
      - *** adjust the above based on your file path
  - run RPC Daemon
    - syntax: ./build/bin/rpcdaemon --datadir={location of your erigon DB} --http.api=eth,erigon,web3,net,debug,trace,txpool --rpc.batch.concurrency={number}
    - terminal: ./build/bin/rpcdaemon --datadir=A:/erigon_db --http.api=eth,erigon,web3,net,debug,trace,txpool --rpc.batch.concurrency=100
      - *** adjust both of the above based on your file path

### RUN NODE

- cd to "erigon" folder then run Erigon
  - terminal: cd C:/erigon_versions/erigon_23.06.27_stable/erigon
  - terminal: ./build/bin/erigon --datadir=A:/erigon_db --internalcl
    - *** adjust both of the above based on your file path
