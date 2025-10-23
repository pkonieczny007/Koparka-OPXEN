import argparse
import time
from datetime import datetime

import os
from web3 import Web3
from db import create_table, insert_mint

#"AGENT31"
RPC_URL = "https://mainnet.optimism.io"
PRIVATE_KEY = "0x6554e33c2a71c429eaa...a2176d68"
FROM_ADDRESS = Web3.to_checksum_address("0xCa466850b9cE18b38ed620bc6755325f215e659e")
CHAIN_ID = 10
DEFAULT_MAX_FEE_GWEI = 0.000001 #0.000005 to jest ok 0.000001 super
DEFAULT_MAX_PRIO_GWEI = 0.000001 #0.000005 to jest ok 0.000001 super

XENTORRENT_ADDRESS = Web3.to_checksum_address("0xAF18644083151cf57F914CCCc23c42A1892C218e")

# Minimalne ABI
ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "count", "type": "uint256"},
            {"internalType": "uint256", "name": "term", "type": "uint256"}
        ],
        "name": "bulkClaimRank",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": True, "internalType": "uint256", "name": "tokenId", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

def get_suggested_gas(web3):
    try:
        gas_price = web3.eth.gas_price
        # Dla EIP-1559, pobierz z suggest_fee
        block = web3.eth.get_block("latest")
        base_fee = block.get("baseFeePerGas", gas_price)
        max_fee = int(base_fee * 1.5)
        max_priority = int(Web3.to_wei(0.02, "gwei"))  # Domyślna prio
        return max_fee, max_priority
    except Exception:
        # Twarde domyślne backup
        return int(Web3.to_wei(0.2, "gwei")), int(Web3.to_wei(0.02, "gwei"))

def parse_transfer_event(receipt, from_addr, contract_addr, web3):
    transfer_event_topic = web3.keccak(text="Transfer(address,address,uint256)").hex()  # ERC721 Transfer
    token_id = None
    for log in receipt["logs"]:
        if (log["address"].lower() == contract_addr.lower() and
            log["topics"][0] == transfer_event_topic and
            log["topics"][-40:].lower() == from_addr[2:].lower() and
            log["topics"][-40:].lower() == FROM_ADDRESS[2:].lower()):
            # topics = tokenId (as hex -> int)
            token_id = int(log["topics"], 16)
            return token_id
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=120, help="VMU per NFT")
    parser.add_argument("--term", type=int, default=507, help="liczba dni")
    parser.add_argument("--repeat", type=int, default=1, help="ile NFT wykonać pod rząd")
    parser.add_argument("--delay", type=int, default=3, help="opóźnienie między transakcjami (w sekundach)")
    parser.add_argument("--maxFee", type=float, help="maxFeePerGas w gwei")
    parser.add_argument("--maxPrio", type=float, help="maxPriorityFeePerGas w gwei")
    parser.add_argument("--gasLimit", type=int, help="manualny gasLimit")
    parser.add_argument("--rpc", type=str, help="RPC_URL override")

    args = parser.parse_args()
    count = args.count
    term = args.term
    repeat = args.repeat
    delay = args.delay
    max_fee = args.maxFee if args.maxFee is not None else DEFAULT_MAX_FEE_GWEI
    max_prio = args.maxPrio if args.maxPrio is not None else DEFAULT_MAX_PRIO_GWEI
    gas_limit = args.gasLimit
    rpc = args.rpc if args.rpc else RPC_URL

    assert count > 0, "Parametr --count musi być > 0"
    assert term > 0, "Parametr --term musi być > 0"

    create_table()
    web3 = Web3(Web3.HTTPProvider(rpc))
    contract = web3.eth.contract(address=XENTORRENT_ADDRESS, abi=ABI)

    for i in range(repeat):
        print(f"\nMint #{i+1}...")
        try:
            nonce = web3.eth.get_transaction_count(FROM_ADDRESS, "pending")
            maxFeePerGas = int(Web3.to_wei(max_fee, "gwei")) if max_fee else None
            maxPriorityFeePerGas = int(Web3.to_wei(max_prio, "gwei")) if max_prio else None
            if not (maxFeePerGas and maxPriorityFeePerGas):
                sugg_fee, sugg_prio = get_suggested_gas(web3)
                maxFeePerGas = maxFeePerGas or sugg_fee
                maxPriorityFeePerGas = maxPriorityFeePerGas or sugg_prio

            tx = contract.functions.bulkClaimRank(count, term).build_transaction({
                "from": FROM_ADDRESS,
                "nonce": nonce,
                "maxFeePerGas": maxFeePerGas,
                "maxPriorityFeePerGas": maxPriorityFeePerGas,
                "chainId": CHAIN_ID,
            })
            if gas_limit:
                tx["gas"] = gas_limit
            else:
                tx["gas"] = web3.eth.estimate_gas(tx)

            signed = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"Tx hash: {tx_hash.hex()} — wysłano, czekam na potwierdzenie...")

            try:
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)
                print(f"Tx confirmed: {receipt.status} (block: {receipt.blockNumber})")
                token_id = parse_transfer_event(receipt, "0x0000000000000000000000000000000000000000", XENTORRENT_ADDRESS, web3)
                if token_id:
                    print(f"Mint OK! tokenId={token_id}")
                else:
                    print("Uwaga: nie udało się odnaleźć tokenId w Transfer event!")
                insert_mint(
                    tx_hash.hex(),
                    token_id,
                    FROM_ADDRESS,
                    count,
                    term,
                    datetime.utcnow().isoformat()
                )
            except Exception as e:
                print(f"[Błąd] Timeout lub błąd potwierdzenia: {str(e)}")
        except ValueError as e:
            # Błąd web3: np. “replacement transaction underpriced”
            reason = str(e)
            print(f"[Web3Error] {reason}")
        except Exception as e:
            print(f"[Unknown error] {str(e)}")
        if i < repeat - 1:
            time.sleep(delay)

if __name__ == "__main__":
    main()
