import os
import sys
import asyncio
import random
import time
from web3 import Web3
from web3connect import connect # Asumsi web3connect.py ada dan berfungsi
from eth_account import Account
from colorama import init, Fore, Style
from eth_abi import abi

# Inisialisasi colorama
init(autoreset=True)

# Lebar Garis
BORDER_WIDTH = 80

# Konstanta
NETWORK_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 16601
EXPLORER_URL = "https://chainscan-galileo.0g.ai/"
ROUTER_ADDRESS = "0xb95B5953FF8ee5D5d9818CdbEfE363ff2191318c"

# Konfigurasi Token
TOKENS = {
    "USDT": {"address": "0x3ec8a8705be1d5ca90066b37ba62c4183b024ebf", "decimals": 18},
    "BTC": {"address": "0x36f6414ff1df609214ddaba71c84f18bcf00f67d", "decimals": 18},
    "ETH": {"address": "0x0fe9b43625fa7edd663adcec0728dd635e4abf7c", "decimals": 18},
}

# Router ABI untuk swap
ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    }
]

# ERC20 ABI untuk approve dan balance
ERC20_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Kamus bahasa
LANG = {
    'id': {
        'title': '✨ SWAP TOKEN - OG LABS TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Ditemukan',
        'wallets': 'dompet',
        'select_swap_type': '✦ PILIH TIPE SWAP',
        'random_option': '1. Swap token acak',
        'manual_option': '2. Swap token manual',
        'choice_prompt': 'Masukkan pilihan (1 atau 2): ',
        'enter_swap_count': '✦ MASUKKAN JUMLAH SWAP',
        'swap_count_prompt': 'Jumlah swap (default 1): ',
        'enter_amount': '✦ MASUKKAN JUMLAH TOKEN UNTUK SWAP',
        'amount_prompt': 'Jumlah token (default 0.1): ',
        'select_manual_swap': '✦ PILIH PASANGAN SWAP MANUAL',
        'start_random': '✨ MEMULAI {swap_count} SWAP ACAK',
        'start_manual': '✨ MEMULAI SWAP MANUAL',
        'processing_wallet': '⚙ MEMPROSES DOMPET',
        'swap': 'Swap',
        'approving': 'Menyetujui token...',
        'swapping': 'Melakukan swap...',
        'success': '✅ Swap berhasil!',
        'failure': '❌ Swap gagal',
        'address': 'Alamat dompet',
        'gas': 'Gas',
        'block': 'Blok',
        'balance': 'Saldo',
        'pausing': 'Menjeda',
        'seconds': 'detik',
        'completed': '🏁 SELESAI: {successful}/{total} SWAP BERHASIL',
        'error': 'Error',
        'invalid_number': 'Mohon masukkan angka yang valid',
        'swap_count_error': 'Jumlah swap harus lebih besar dari 0',
        'amount_error': 'Jumlah token harus lebih besar dari 0',
        'invalid_choice': 'Pilihan tidak valid',
        'connect_success': '✅ Berhasil: Terhubung ke OG Labs Testnet',
        'connect_error': '❌ Tidak dapat terhubung ke RPC',
        'web3_error': '❌ Koneksi Web3 gagal',
        'pvkey_not_found': '❌ File pvkey.txt tidak ditemukan',
        'pvkey_empty': '❌ Tidak ada private key yang valid ditemukan',
        'pvkey_error': '❌ Gagal membaca pvkey.txt',
        'no_balance': '❌ Saldo token atau A0GI tidak mencukupi untuk swap',
        'selected': 'Terpilih',
        'manual_swap_options': {
            1: '1. Swap USDT -> ETH',
            2: '2. Swap ETH -> USDT',
            3: '3. Swap USDT -> BTC',
            4: '4. Swap BTC -> USDT',
            5: '5. Swap BTC -> ETH',
            6: '6. Swap ETH -> BTC',
        },
        'manual_swap_prompt': 'Pilih pasangan swap (1-6): ',
        'enter_percentage': '✦ MASUKKAN PERSENTASE YANG AKAN DI-SWAP',
        'percentage_prompt': 'Persentase token yang akan di-swap (default 50%): ',
        'percentage_error': 'Persentase harus antara 1 sampai 100',
        'selected_percent': 'Terpilih: {percent}% token',
        'calculating_amount': 'Menghitung jumlah ({percent}% dari {balance}): {amount} {symbol}',
    }
}

# Fungsi untuk menampilkan garis batas yang bagus
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
    print(f"{color}║{padded_text}║{Style.RESET_ALL}")
    print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

# Fungsi untuk mendapatkan persentase swap
def get_swap_percentage(language: str = 'id') -> float:
    print_border(LANG[language]['enter_percentage'], Fore.YELLOW)
    while True:
        try:
            percent_input = input(f"{Fore.YELLOW}   > {LANG[language]['percentage_prompt']}{Style.RESET_ALL}")
            percent = float(percent_input) if percent_input.strip() else 50.0
            if percent <= 0 or percent > 100:
                print(f"{Fore.RED}   ✖ {LANG[language]['error']}: {LANG[language]['percentage_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}   ✔ {LANG[language]['selected_percent'].format(percent=percent)}{Style.RESET_ALL}")
                return percent
        except ValueError:
            print(f"{Fore.RED}   ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Fungsi untuk menampilkan pemisah
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Fungsi untuk memeriksa kunci privat yang valid
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Fungsi untuk membaca kunci privat dari file pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'id') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}   ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Tambahkan private key di sini, setiap key di baris baru\n# Contoh: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}   ⚠ {LANG[language]['error']}: Baris {i} - {key} {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}   ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}   ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Fungsi untuk koneksi Web3
def connect_web3(language: str = 'id'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if w3.is_connected():
            print(f"{Fore.GREEN}   ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}   ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}   ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Fungsi untuk swap token
async def swap_tokens(w3: Web3, private_key: str, token_in: str, token_out: str, amount_in: int, token_in_symbol: str, token_out_symbol: str, language: str = 'id'):
    account = Account.from_key(private_key)
    router_contract = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_ADDRESS), abi=ROUTER_ABI)

    try:
        # Approve token sebelum swap
        if not await approve_token(w3, private_key, token_in, ROUTER_ADDRESS, amount_in, language):
            return False

        # Siapkan parameter swap
        swap_params = {
            "tokenIn": Web3.to_checksum_address(token_in),
            "tokenOut": Web3.to_checksum_address(token_out),
            "fee": 3000,  # 0.3%
            "recipient": account.address,
            "deadline": int(time.time()) + 1800,  # 30 menit
            "amountIn": amount_in,
            "amountOutMinimum": 0,
            "sqrtPriceLimitX96": 0,
        }

        # Dapatkan parameter transaksi
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.to_wei('70', 'gwei')  # Harga gas tetap
        
        try:
            estimated_gas = router_contract.functions.exactInputSingle(swap_params).estimate_gas({
                'from': account.address,
                'value': 0
            })
            gas_limit = int(estimated_gas * 1.2)
            print(f"{Fore.YELLOW}   - Estimasi Gas: {estimated_gas} | Batas Gas yang digunakan: {gas_limit}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}   - Tidak dapat mengestimasi gas: {str(e)}. Menggunakan gas default: 500000{Style.RESET_ALL}")
            gas_limit = 500000  # Batas gas default yang lebih tinggi

        # Periksa apakah pengguna memiliki cukup A0GI untuk gas
        balance = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
        required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
        if balance < required_balance:
            print(f"{Fore.RED}   ✖ {LANG[language]['no_balance']} (Perlu: {required_balance:.6f} A0GI, Punya: {balance:.6f} A0GI){Style.RESET_ALL}")
            return False

        # Fungsi untuk mengeksekusi transaksi dengan penanganan nonce
        async def execute_transaction_with_nonce_handling(nonce=None):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Jika nonce tidak diberikan, dapatkan dari jaringan
                    if nonce is None:
                        nonce = w3.eth.get_transaction_count(account.address)
                    
                    # Bangun transaksi
                    tx = router_contract.functions.exactInputSingle(swap_params).build_transaction({
                        'from': account.address,
                        'nonce': nonce,
                        'gas': gas_limit,
                        'gasPrice': gas_price,
                        'chainId': CHAIN_ID,
                    })
                    
                    print(f"{Fore.CYAN}   > {LANG[language]['swapping']} (Nonce: {nonce}){Style.RESET_ALL}")
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                    receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                    
                    return True, receipt, tx_hash, tx_link
                
                except Exception as e:
                    error_str = str(e)
                    if "invalid nonce" in error_str.lower():
                        # Ekstrak nonce yang diharapkan dari pesan error
                        try:
                            # Parse pesan error untuk mendapatkan nonce yang diharapkan
                            # Format: 'invalid nonce; got X, expected Y, ...'
                            expected_nonce_str = error_str.split('expected ')[1].split(',')[0]
                            expected_nonce = int(expected_nonce_str)
                            print(f"{Fore.YELLOW}   ⚠ Nonce tidak valid. Mencoba lagi dengan nonce: {expected_nonce}{Style.RESET_ALL}")
                            nonce = expected_nonce
                            retry_count += 1
                        except:
                            # Jika tidak dapat mem-parse nonce yang diharapkan, dapatkan yang baru dari jaringan
                            print(f"{Fore.YELLOW}   ⚠ Nonce tidak valid. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                            await asyncio.sleep(2)  # Tunggu sebentar sebelum mendapatkan nonce baru
                            nonce = w3.eth.get_transaction_count(account.address)
                            retry_count += 1
                    else:
                        # Error lain yang tidak terkait dengan nonce
                        print(f"{Fore.RED}   ✖ Swap gagal: {str(e)}{Style.RESET_ALL}")
                        return False, None, None, None
            
            # Jika sudah mencoba beberapa kali dan gagal
            print(f"{Fore.RED}   ✖ Swap gagal setelah {max_retries} kali percobaan{Style.RESET_ALL}")
            return False, None, None, None

        # Eksekusi transaksi dengan penanganan nonce
        success, receipt, tx_hash, tx_link = await execute_transaction_with_nonce_handling()
        
        if success and receipt.status == 1:
            # Dapatkan saldo token setelah swap untuk menghitung jumlah yang diterima
            try:
                # Coba ekstrak amountOut dari log, tapi tangani log yang hilang dengan baik
                amount_out = 0
                if receipt.logs and len(receipt.logs) > 0:
                    try:
                        amount_out_data = receipt.logs[0].data[-32:]  # Ambil amountOut dari log
                        amount_out = int.from_bytes(amount_out_data, 'big')
                    except (IndexError, Exception) as e:
                        print(f"{Fore.YELLOW}   ⚠ Tidak dapat mengambil jumlah token keluar dari log: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}   ⚠ Transaksi berhasil tetapi tidak ada log untuk mengambil jumlah token keluar{Style.RESET_ALL}")
                
                # Dapatkan saldo setelah swap
                token_in_balance = w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=ERC20_ABI).functions.balanceOf(account.address).call() / 10**18
                token_out_balance = w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI).functions.balanceOf(account.address).call() / 10**18
                
                print(f"{Fore.GREEN}   ✔ {LANG[language]['success']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - Jumlah masuk: {amount_in / 10**18:.6f} {token_in_symbol}{Style.RESET_ALL}")
                if amount_out > 0:
                    print(f"{Fore.YELLOW}     - Jumlah keluar: {amount_out / 10**18:.6f} {token_out_symbol}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - {LANG[language]['balance']} {token_in_symbol}: {token_in_balance:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - {LANG[language]['balance']} {token_out_symbol}: {token_out_balance:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            except Exception as e:
                # Jika tidak bisa mendapatkan jumlah output, tetap laporkan berhasil tapi sebutkan errornya
                print(f"{Fore.GREEN}   ✔ {LANG[language]['success']} (Tidak dapat mengambil detail: {str(e)}){Style.RESET_ALL}")
                print(f"{Fore.YELLOW}     - Tx: {tx_link}{Style.RESET_ALL}")
                return True
        else:
            if tx_link:
                print(f"{Fore.RED}   ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}   ✖ {LANG[language]['failure']}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}   ✖ Swap gagal: {str(e)}{Style.RESET_ALL}")
        return False

# Fungsi approve token
async def approve_token(w3: Web3, private_key: str, token_address: str, spender: str, amount: int, language: str = 'id'):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    
    try:
        allowance = token_contract.functions.allowance(account.address, spender).call()
        if allowance >= amount:
            print(f"{Fore.GREEN}   ✔ Sudah ada allowance yang cukup untuk {spender}{Style.RESET_ALL}")
            return True

        # Atur jumlah persetujuan maksimum (2^256 - 1)
        max_approval = 2**256 - 1
        print(f"{Fore.YELLOW}   > Mengatur persetujuan tak terbatas (max uint256){Style.RESET_ALL}")
        
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.to_wei('70', 'gwei')  # Harga gas tetap
        
        try:
            estimated_gas = token_contract.functions.approve(spender, max_approval).estimate_gas({
                'from': account.address
            })
            gas_limit = int(estimated_gas * 1.2)
        except Exception as e:
            print(f"{Fore.YELLOW}   - Tidak dapat mengestimasi gas untuk approve: {str(e)}. Menggunakan gas default: 100000{Style.RESET_ALL}")
            gas_limit = 100000

        # Fungsi untuk mengeksekusi approve dengan penanganan nonce
        async def execute_approve_with_nonce_handling(nonce=None):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Jika nonce tidak diberikan, dapatkan dari jaringan
                    if nonce is None:
                        nonce = w3.eth.get_transaction_count(account.address)
                    
                    # Bangun transaksi dengan persetujuan maksimum
                    tx = token_contract.functions.approve(spender, max_approval).build_transaction({
                        'from': account.address,
                        'nonce': nonce,
                        'gas': gas_limit,
                        'gasPrice': gas_price,
                        'chainId': CHAIN_ID,
                    })
                    
                    print(f"{Fore.CYAN}   > {LANG[language]['approving']} (Nonce: {nonce}){Style.RESET_ALL}")
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                    
                    return True, receipt, tx_hash
                
                except Exception as e:
                    error_str = str(e)
                    if "invalid nonce" in error_str.lower():
                        # Ekstrak nonce yang diharapkan dari pesan error
                        try:
                            expected_nonce_str = error_str.split('expected ')[1].split(',')[0]
                            expected_nonce = int(expected_nonce_str)
                            print(f"{Fore.YELLOW}   ⚠ Nonce tidak valid. Mencoba lagi dengan nonce: {expected_nonce}{Style.RESET_ALL}")
                            nonce = expected_nonce
                            retry_count += 1
                        except:
                            print(f"{Fore.YELLOW}   ⚠ Nonce tidak valid. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                            await asyncio.sleep(2)
                            nonce = w3.eth.get_transaction_count(account.address)
                            retry_count += 1
                    else:
                        print(f"{Fore.RED}   ✖ Approve gagal: {str(e)}{Style.RESET_ALL}")
                        return False, None, None
            
            print(f"{Fore.RED}   ✖ Approve gagal setelah {max_retries} kali percobaan{Style.RESET_ALL}")
            return False, None, None

        # Eksekusi transaksi dengan penanganan nonce
        success, receipt, tx_hash = await execute_approve_with_nonce_handling()
        
        if success and receipt.status == 1:
            print(f"{Fore.GREEN}   ✔ Approve berhasil | Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            return True
        else:
            if tx_hash:
                print(f"{Fore.RED}   ✖ Approve gagal | Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}   ✖ Approve gagal{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}   ✖ Approve gagal: {str(e)}{Style.RESET_ALL}")
        return False

# Fungsi untuk mendapatkan jumlah swap
def get_swap_count(language: str = 'id') -> int:
    print_border(LANG[language]['enter_swap_count'], Fore.YELLOW)
    while True:
        try:
            swap_count_input = input(f"{Fore.YELLOW}   > {LANG[language]['swap_count_prompt']}{Style.RESET_ALL}")
            swap_count = int(swap_count_input) if swap_count_input.strip() else 1
            if swap_count <= 0:
                print(f"{Fore.RED}   ✖ {LANG[language]['error']}: {LANG[language]['swap_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}   ✔ {LANG[language]['selected']}: {swap_count} swaps{Style.RESET_ALL}")
                return swap_count
        except ValueError:
            print(f"{Fore.RED}   ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Fungsi untuk menampilkan saldo
def display_balances(w3: Web3, account_address: str, language: str = 'id'):
    print(f"{Fore.YELLOW}   - {LANG[language]['balance']} USDT: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['USDT']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   - {LANG[language]['balance']} ETH: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['ETH']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   - {LANG[language]['balance']} BTC: {(w3.eth.contract(address=Web3.to_checksum_address(TOKENS['BTC']['address']), abi=ERC20_ABI).functions.balanceOf(account_address).call() / 10**18):.6f}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   - {LANG[language]['balance']} A0GI: {(w3.from_wei(w3.eth.get_balance(account_address), 'ether')):.6f}{Style.RESET_ALL}")

# Swap acak
async def random_swap(w3: Web3, private_key: str, swap_count: int, percent: float, wallet_index: int, language: str = 'id'):
    account = Account.from_key(private_key)
    successful_swaps = 0
    
    for swap_num in range(swap_count):
        print(f"{Fore.CYAN}   > {LANG[language]['swap']} {swap_num + 1}/{swap_count}{Style.RESET_ALL}")
        
        # Tampilkan saldo
        display_balances(w3, account.address, language)
        
        # Dapatkan daftar token yang memiliki saldo
        token_balances = {}
        for symbol, token_data in TOKENS.items():
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_data['address']), abi=ERC20_ABI)
            balance = contract.functions.balanceOf(account.address).call()
            token_balances[symbol] = balance
        
        tokens_with_balance = [symbol for symbol, balance in token_balances.items() if balance > 0]
        if not tokens_with_balance:
            print(f"{Fore.RED}   ✖ {LANG[language]['no_balance']}{Style.RESET_ALL}")
            break

        token_in_symbol = random.choice(tokens_with_balance)
        token_in_address = TOKENS[token_in_symbol]["address"]
        balance_wei = token_balances[token_in_symbol]
        balance = balance_wei / 10**TOKENS[token_in_symbol]["decimals"]
        
        # Hitung jumlah berdasarkan persentase saldo
        amount = balance * (percent / 100)
        amount_in = int(amount * 10**TOKENS[token_in_symbol]["decimals"])
        
        if amount_in <= 0:
            print(f"{Fore.RED}   ✖ {LANG[language]['no_balance']} (Saldo terlalu kecil: {balance} {token_in_symbol}){Style.RESET_ALL}")
            break
            
        # Tampilkan detail perhitungan
        print(f"{Fore.YELLOW}   > {LANG[language]['calculating_amount'].format(percent=percent, balance=balance, amount=amount, symbol=token_in_symbol)}{Style.RESET_ALL}")

        if token_in_symbol == "USDT":
            token_out_symbol = random.choice(["ETH", "BTC"])
        else:
            token_out_symbol = "USDT"
        token_out_address = TOKENS[token_out_symbol]["address"]

        if await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language):
            successful_swaps += 1
        
        if swap_num < swap_count - 1:
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}   ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    return successful_swaps

# Fungsi swap manual yang dimodifikasi dengan alur baru
async def manual_swap(w3: Web3, private_key: str, wallet_index: int, language: str = 'id', pair_choice=None, percent=None):
    account = Account.from_key(private_key)
    
    # 1. Pertama tampilkan saldo untuk dompet ini
    print_separator()
    print(f"{Fore.CYAN}   > Saldo token yang tersedia untuk dompet ini:{Style.RESET_ALL}")
    display_balances(w3, account.address, language)
    print_separator()
    
    # 2. Gunakan pilihan pasangan yang disediakan atau minta dari pengguna
    if pair_choice is None:
        print_border(LANG[language]['select_manual_swap'], Fore.YELLOW)
        for i in range(1, 7):
            print(f"{Fore.GREEN}     ├─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}" if i < 6 else 
                f"{Fore.GREEN}     └─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}")
        
        while True:
            try:
                pair_choice = int(input(f"{Fore.YELLOW}   > {LANG[language]['manual_swap_prompt']}{Style.RESET_ALL}"))
                if pair_choice in range(1, 7):
                    break
                print(f"{Fore.RED}   ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}   ✖ {LANG[language]['invalid_number']}{Style.RESET_ALL}")

    pairs = {
        1: ("USDT", "ETH"), 2: ("ETH", "USDT"), 3: ("USDT", "BTC"),
        4: ("BTC", "USDT"), 5: ("BTC", "ETH"), 6: ("ETH", "BTC")
    }
    
    token_in_symbol, token_out_symbol = pairs[pair_choice]
    token_in_address = TOKENS[token_in_symbol]["address"]
    token_out_address = TOKENS[token_out_symbol]["address"]
    
    print(f"{Fore.GREEN}   ✔ Menggunakan pasangan: {token_in_symbol} -> {token_out_symbol}{Style.RESET_ALL}")
    
    # 3. Dapatkan saldo saat ini dari token yang dipilih
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_in_address), abi=ERC20_ABI)
    balance_wei = token_contract.functions.balanceOf(account.address).call()
    balance = balance_wei / 10**TOKENS[token_in_symbol]["decimals"]
    
    if balance <= 0:
        print(f"{Fore.RED}   ✖ {LANG[language]['no_balance']} (Tidak ada {token_in_symbol} untuk di-swap){Style.RESET_ALL}")
        return 0
    
    # 4. Gunakan persentase yang disediakan atau minta dari pengguna
    if percent is None:
        percent = get_swap_percentage(language)
    else:
        print(f"{Fore.GREEN}   ✔ {LANG[language]['selected_percent'].format(percent=percent)}{Style.RESET_ALL}")
    
    # 5. Hitung jumlah aktual berdasarkan persentase
    amount = balance * (percent / 100)
    amount_in = int(amount * 10**TOKENS[token_in_symbol]["decimals"])
    
    # 6. Tampilkan detail perhitungan
    print(f"{Fore.YELLOW}   > {LANG[language]['calculating_amount'].format(percent=percent, balance=balance, amount=amount, symbol=token_in_symbol)}{Style.RESET_ALL}")
    
    # 7. Eksekusi swap dengan jumlah yang dihitung (menggunakan pengaturan gas asli)
    success = await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language)
    return 1 if success else 0

async def run_swaptoken(language: str = 'id'):
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}   {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print_separator()

    while True:
        print_border(LANG[language]['select_swap_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}     ├─ {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}     └─ {LANG[language]['manual_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}   > {LANG[language]['choice_prompt']}{Style.RESET_ALL}").strip()

        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}   ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        print()

    if choice == '1':
        # Untuk swap acak, minta jumlah swap dan persentase, bukan jumlah absolut
        swap_count = get_swap_count(language)
        percent = get_swap_percentage(language)  # Sekarang menggunakan persentase untuk swap acak juga
    else:
        # Untuk swap manual, kita akan meminta pasangan dan persentase sekali untuk semua dompet
        # Tampilkan saldo contoh dari dompet pertama untuk membantu pengambilan keputusan
        if private_keys:
            first_account = Account.from_key(private_keys[0][1])
            print(f"{Fore.CYAN}   > Saldo contoh dari dompet pertama:{Style.RESET_ALL}")
            display_balances(w3, first_account.address, language)
            print_separator()
        
        # Minta pasangan swap sekali
        print_border(LANG[language]['select_manual_swap'], Fore.YELLOW)
        for i in range(1, 7):
            print(f"{Fore.GREEN}     ├─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}" if i < 6 else 
                f"{Fore.GREEN}     └─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}")
        
        while True:
            try:
                pair_choice = int(input(f"{Fore.YELLOW}   > {LANG[language]['manual_swap_prompt']}{Style.RESET_ALL}"))
                if pair_choice in range(1, 7):
                    break
                print(f"{Fore.RED}   ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}   ✖ {LANG[language]['invalid_number']}{Style.RESET_ALL}")
        
        # Dapatkan persentase sekali
        percent = get_swap_percentage(language)
        swap_count = 1

    print_separator()

    total_swaps = swap_count * len(private_keys) if choice == '1' else len(private_keys)
    successful_swaps = 0

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        conn = connect(private_key) # Asumsi fungsi connect() ada dan tidak memerlukan w3 sebagai argumen
        print()
        
        if choice == '1':
            print_border(LANG[language]['start_random'].format(swap_count=swap_count), Fore.CYAN)
            successful_swaps += await random_swap(w3, private_key, swap_count, percent, i, language)  # Teruskan persentase
        else:
            print_border(LANG[language]['start_manual'], Fore.CYAN)
            # Teruskan pasangan yang dipilih dan persentase ke fungsi
            successful_swaps += await manual_swap(w3, private_key, i, language, pair_choice, percent)
        print()

    print_border(LANG[language]['completed'].format(successful=successful_swaps, total=total_swaps), Fore.GREEN)
    print()


if __name__ == "__main__":
    asyncio.run(run_swaptoken('id'))  # Bahasa default adalah Bahasa Indonesia
