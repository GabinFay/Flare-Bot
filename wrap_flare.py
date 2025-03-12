#!/usr/bin/env python3
"""
Script to wrap native FLR to WFLR (Wrapped Flare) on Flare network
"""

# Load wallet details from .env file
from dotenv import load_dotenv
import os
import json
import traceback
from eth_account import Account

load_dotenv()

from web3 import Web3
from web3.middleware import geth_poa_middleware

def wrap_flare(amount_flr):
    """
    Wrap native FLR to WFLR (Wrapped Flare) on Flare network
    
    Args:
        amount_flr (float): Amount of FLR to wrap
        
    Returns:
        dict: Transaction receipt if successful, None otherwise
    """
    # Get environment variables
    FLARE_RPC_URL = os.getenv("FLARE_RPC_URL")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    
    # Derive wallet address from private key
    if not PRIVATE_KEY:
        print("ERROR: Private key is missing or empty!")
        return None
    
    try:
        account = Account.from_key(PRIVATE_KEY)
        WALLET_ADDRESS = account.address
        print(f"Using wallet address derived from private key: {WALLET_ADDRESS}")
    except Exception as e:
        print(f"ERROR: Failed to derive wallet address from private key: {e}")
        print(traceback.format_exc())
        return None

    print(f"Using RPC URL: {FLARE_RPC_URL}")
    
    # Debug: Check if private key is available
    if not PRIVATE_KEY:
        print("ERROR: Private key is missing or empty!")
        return None
    else:
        print("Private key is available (not showing for security)")
    
    # Debug: Check if amount_flr is valid
    print(f"Amount to wrap (raw input): {amount_flr}, type: {type(amount_flr)}")
    
    # Validate amount_flr
    if amount_flr is None:
        print("ERROR: amount_flr is None")
        return None
    
    try:
        # Convert amount_flr to float if it's a string
        if isinstance(amount_flr, str):
            amount_flr = float(amount_flr)
        
        # Ensure amount_flr is a number
        if not isinstance(amount_flr, (int, float)):
            print(f"ERROR: amount_flr must be a number, got {type(amount_flr)}")
            return None
        
        print(f"Amount to wrap (converted): {amount_flr} FLR")
    except Exception as e:
        print(f"ERROR: Failed to convert amount_flr: {e}")
        print(traceback.format_exc())
        return None

    # Connect to the Flare network
    web3 = Web3(Web3.HTTPProvider(FLARE_RPC_URL))

    # Add middleware for POA networks
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Check if connected to the network
    if not web3.is_connected():
        print("ERROR: Failed to connect to the Flare network")
        return None

    print(f"Connected to Flare network: {web3.is_connected()}")
    print(f"Current block number: {web3.eth.block_number}")

    # Check account balance
    account_balance = web3.eth.get_balance(WALLET_ADDRESS)
    print(f"Account balance: {web3.from_wei(account_balance, 'ether')} FLR")
    
    # Check if account has enough balance
    amount_to_wrap = web3.to_wei(amount_flr, 'ether')
    if account_balance < amount_to_wrap:
        print(f"ERROR: Insufficient balance. Have {web3.from_wei(account_balance, 'ether')} FLR, need {amount_flr} FLR")
        return None

    # WNat (WFLR) contract address on Flare
    wnat_contract_address = '0x1D80c49BbBCd1C0911346656B529DF9E5c2F783d'  # WFLR address

    # Standard WETH9-like ABI (which WFLR likely follows)
    wnat_abi = '''
    [
        {
            "constant": true,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "guy", "type": "address"}, {"name": "wad", "type": "uint256"}],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "src", "type": "address"}, {"name": "dst", "type": "address"}, {"name": "wad", "type": "uint256"}],
            "name": "transferFrom",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "wad", "type": "uint256"}],
            "name": "withdraw",
            "outputs": [],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [{"name": "", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "dst", "type": "address"}, {"name": "wad", "type": "uint256"}],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "deposit",
            "outputs": [],
            "payable": true,
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "payable": true,
            "stateMutability": "payable",
            "type": "fallback"
        },
        {
            "anonymous": false,
            "inputs": [{"indexed": true, "name": "src", "type": "address"}, {"indexed": true, "name": "guy", "type": "address"}, {"indexed": false, "name": "wad", "type": "uint256"}],
            "name": "Approval",
            "type": "event"
        },
        {
            "anonymous": false,
            "inputs": [{"indexed": true, "name": "src", "type": "address"}, {"indexed": true, "name": "dst", "type": "address"}, {"indexed": false, "name": "wad", "type": "uint256"}],
            "name": "Transfer",
            "type": "event"
        },
        {
            "anonymous": false,
            "inputs": [{"indexed": true, "name": "dst", "type": "address"}, {"indexed": false, "name": "wad", "type": "uint256"}],
            "name": "Deposit",
            "type": "event"
        },
        {
            "anonymous": false,
            "inputs": [{"indexed": true, "name": "src", "type": "address"}, {"indexed": false, "name": "wad", "type": "uint256"}],
            "name": "Withdrawal",
            "type": "event"
        }
    ]
    '''

    # Create contract instance
    wnat_contract = web3.eth.contract(address=wnat_contract_address, abi=wnat_abi)

    # Amount of FLR to wrap (in wei, 1 FLR = 10^18 wei)
    amount_to_wrap = web3.to_wei(amount_flr, 'ether')
    
    print(f"Preparing to wrap {amount_flr} FLR to WFLR...")

    try:
        # Try to get contract name and symbol
        try:
            contract_name = wnat_contract.functions.name().call()
            contract_symbol = wnat_contract.functions.symbol().call()
            print(f"Contract name: {contract_name}")
            print(f"Contract symbol: {contract_symbol}")
        except Exception as e:
            print(f"Could not get contract name/symbol: {e}")
        
        # Check initial WFLR balance
        try:
            initial_balance = wnat_contract.functions.balanceOf(WALLET_ADDRESS).call()
            print(f"Initial WFLR balance: {web3.from_wei(initial_balance, 'ether')} WFLR")
        except Exception as e:
            print(f"Could not get initial balance: {e}")
            initial_balance = 0

        # Get current gas price
        gas_price = web3.eth.gas_price
        print(f"Current gas price: {web3.from_wei(gas_price, 'gwei')} gwei")
        
        # Use a slightly higher gas price to ensure transaction goes through
        suggested_gas_price = int(gas_price * 1.1)
        print(f"Suggested gas price: {web3.from_wei(suggested_gas_price, 'gwei')} gwei")
        
        # Build transaction
        transaction = wnat_contract.functions.deposit().build_transaction({
            'from': WALLET_ADDRESS,
            'value': amount_to_wrap,
            'gas': 200000,  # Increased gas limit
            'gasPrice': suggested_gas_price,
            'nonce': web3.eth.get_transaction_count(WALLET_ADDRESS),
        })
        
        print(f"Transaction details: {json.dumps(dict(transaction), indent=2, default=str)}")

        # Sign transaction
        try:
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
            print("Transaction signed successfully")
        except Exception as e:
            print(f"ERROR: Failed to sign transaction: {e}")
            print(traceback.format_exc())
            return None

        # Send transaction
        try:
            print(f"Sending transaction to wrap {amount_flr} FLR to WFLR...")
            txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"Transaction sent with hash: {txn_hash.hex()}")
        except Exception as e:
            print(f"ERROR: Failed to send transaction: {e}")
            print(traceback.format_exc())
            return None

        # Wait for transaction receipt
        try:
            print("Waiting for transaction confirmation...")
            txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
            print(f"Transaction receipt received")
        except Exception as e:
            print(f"ERROR: Failed to get transaction receipt: {e}")
            print(traceback.format_exc())
            return None
        
        print(f"Transaction receipt: {json.dumps(dict(txn_receipt), indent=2, default=str)}")
        
        if txn_receipt.status == 1:
            print(f"Transaction successful!")
            print(f"Transaction hash: {txn_receipt.transactionHash.hex()}")
            print(f"Gas used: {txn_receipt.gasUsed}")
            
            # Check new WFLR balance
            try:
                new_balance = wnat_contract.functions.balanceOf(WALLET_ADDRESS).call()
                print(f"New WFLR balance: {web3.from_wei(new_balance, 'ether')} WFLR")
                print(f"Change: {web3.from_wei(new_balance - initial_balance, 'ether')} WFLR")
            except Exception as e:
                print(f"Could not get new balance: {e}")
                
            return txn_receipt
        else:
            print("Transaction failed!")
            
            # Try to get transaction details
            try:
                tx = web3.eth.get_transaction(txn_hash)
                print(f"Transaction details: {json.dumps(dict(tx), indent=2, default=str)}")
            except Exception as e:
                print(f"Error getting transaction details: {e}")
            
            return None

    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Wrap 50 FLR
    wrap_flare(50) 