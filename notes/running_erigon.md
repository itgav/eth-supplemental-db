# GOAL

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
    - terminal: cd {file_path to erigon folder}
      - *** adjust the above based on your file path
  - run RPC Daemon
    - terminal: ./build/bin/rpcdaemon --datadir={location of your erigon DB} --http.api=eth,erigon,web3,net,debug,trace,txpool --rpc.batch.concurrency={number}
      - *** adjust both of the above based on your file path

### RUN NODE

- cd to "erigon" folder then run Erigon
  - terminal: cd {file_path to erigon folder}
  - terminal: ./build/bin/erigon --datadir={location of your erigon DB}
    - *** adjust both of the above based on your file path
    - *** I also use the '--internalcl' flag but you can also use a normal CL client
