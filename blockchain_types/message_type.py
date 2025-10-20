"""Message types for P2P communication."""


class MessageType:
    """
    Message type constants for network communication.
    
    Defines protocols for client-server and peer-to-peer messages.
    """
    
    # Client to Server commands
    GET_BALANCE = "getBalance"
    # RECV: getBalance, b64(address)
    # RESP: b64(balance)
    
    DO_TRANSACT = "doTransact"
    # RECV: doTransact, b64(transaction.toBase64)
    # RESP: b64(Ok), b64(Error)
    
    GET_CLONE_CHAIN_FROM = "getCloneChainFrom"
    # RECV: getCloneChainFrom, b64(networkNode.toBase64)
    # RESP: b64(Ok), b64(Error)
    
    JOIN_NETWORK = "joinNetwork"
    # RECV: joinNetwork, b64(networknode.toBase64)
    # RESP: b64(Ok), b64(Dup)
    
    MINE_START = "startMining"
    # RECV: startMining (Note: Local command)
    # RESP: b64(Ok)
    
    MINE_STOP = "stopMining"
    # RECV: stopMining (Note: Local command)
    # RESP: b64(Ok)
    
    # Peer-to-Peer broadcast messages
    BCAST_BLOCK = "broadcastedBlock"
    # RECV: broadcastedBlock, b64(block.toBase64)
    # RESP: b64(Ok), b64(Dup)
    
    BCAST_TRANSACT = "broadcastedTransaction"
    # RECV: broadcastedTransaction, b64(transaction.toBase64)
    # RESP: b64(Ok), b64(Dup)
    
    BCAST_NEWNODE = "broadcastedNewNode"
    # RECV: broadcastedNewNode, b64(networkNode.toBase64)
    # RESP: b64(Ok), b64(Dup)
    
    CLONE_CHAIN = "cloneBlockchain"
    # RECV: cloneBlockchain
    # RESP: b64(blockchain.toBase64())