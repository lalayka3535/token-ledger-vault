"""
Chain Tracker — отслеживание цепочки движения средств от заданной транзакции.
"""

import requests
import argparse
import time

def fetch_transaction(txid):
    url = f"https://api.blockchair.com/bitcoin/raw/transaction/{txid}"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"❌ Ошибка загрузки транзакции {txid}")
    return r.json()["data"][txid]["decoded_raw_transaction"]

def extract_outputs(tx):
    return [o["script_pub_key"].get("address") for o in tx.get("vout", []) if "script_pub_key" in o and "address" in o["script_pub_key"]]

def track_chain(txid, depth=2, visited=None):
    if visited is None:
        visited = set()

    if depth == 0 or txid in visited:
        return
    visited.add(txid)

    print(f"\n🔗 Транзакция: {txid}")
    try:
        tx = fetch_transaction(txid)
    except Exception as e:
        print(str(e))
        return

    outputs = extract_outputs(tx)
    print(f"📤 Адреса-выходы ({len(outputs)}):")
    for addr in outputs:
        if addr:
            print(f"  • {addr}")
            try:
                time.sleep(1)
                url = f"https://api.blockchair.com/bitcoin/dashboards/address/{addr}"
                r = requests.get(url)
                if r.status_code == 200:
                    txs = r.json()["data"][addr]["transactions"]
                    next_txid = txs[0] if txs and txs[0] != txid else None
                    if next_txid:
                        track_chain(next_txid, depth-1, visited)
            except:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chain Tracker — отслеживание цепочки транзакций.")
    parser.add_argument("txid", help="Начальный хеш транзакции")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Глубина рекурсии (по умолчанию 2)")
    args = parser.parse_args()

    track_chain(args.txid, args.depth)
