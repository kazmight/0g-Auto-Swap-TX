import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
from eth_abi import abi

# Initialize colorama
init(autoreset=True)

# Border Width
BORDER_WIDTH = 80

# ASCII Art Intro
ASCII_INTRO = """
░█████╗░░██████╗░  ░█████╗░██╗░░░██╗████████╗░█████╗░  ░██████╗░██╗░░░░░░░██╗░█████╗░██████╗░
██╔══██╗██╔════╝░  ██╔══██╗██║░░░██║╚══██╔══╝██╔══██╗  ██╔════╝░██║░░██╗░░██║██╔══██╗██╔══██╗
██║░░██║██║░░██╗░  ███████║██║░░░██║░░░██║░░░██║░░██║  ╚█████╗░░╚██╗████╗██╔╝███████║██████╔╝
██║░░██║██║░░╚██╗  ██╔══██║██║░░░██║░░░██║░░░██║░░██║  ░╚═══██╗░░████╔═████║░██╔══██║██╔═══╝░
╚█████╔╝╚██████╔╝  ██║░░██║╚██████╔╝░░░██║░░░╚█████╔╝  ██████╔╝░░╚██╔╝░╚██╔╝░██║░░██║██║░░░░░
░╚════╝░░╚═════╝░  ╚═╝░░╚═╝░╚═════╝░░░░╚═╝░░░░╚════╝░  ╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░░░░
by Kazmight
"""

# Constants
NETWORK_URL = "https://evmrpc-testnet.0g.ai"
CHAIN_ID = 16601
EXPLORER_URL = "https://chainscan-galileo.0g.ai/tx/0x"
ROUTER_ADDRESS = "0xb95B5953FF8ee5D5d9818CdbEfE363ff2191318c" # Check if this address is still valid on 0G.ai

# Token Configuration
TOKENS = {
    "USDT": {"address": "0x3ec8a8705be1d5ca90066b37ba62c4183b024ebf", "decimals": 18},
    "BTC": {"address": "0x36f6414ff1df609214ddaba71c84f18bcf00f67d", "decimals": 18},
    "ETH": {"address": "0x0fe9b43625fa7edd663adcec0728dd635e4abf7c", "decimals": 18},
}

# Router ABI for swap
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

# ERC20 ABI for approve and balance
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

# Language Dictionary
LANG = {
    'id': {
        'title': '✨ SWAP TOKEN - OG LABS TESTNET ✨',
        'info': 'Informasi',
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

# Function to print a nice border
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
    print(f"{color}║{padded_text}║{Style.RESET_ALL}")
    print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

# Function to get swap percentage
def get_swap_percentage(language: str = 'id') -> float:
    print_border(LANG[language]['enter_percentage'], Fore.YELLOW)
    while True:
        try:
            percent_input = input(f"{Fore.YELLOW}    > {LANG[language]['percentage_prompt']}{Style.RESET_ALL}")
            percent = float(percent_input) if percent_input.strip() else 50.0
            if percent <= 0 or percent > 100:
                print(f"{Fore.RED}    ✖ {LANG[language]['error']}: {LANG[language]['percentage_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}    ✔ {LANG[language]['selected_percent'].format(percent=percent)}{Style.RESET_ALL}")
                return percent
        except ValueError:
            print(f"{Fore.RED}    ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Function to print separator
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Function to check for valid private key
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Function to load private keys from pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'id') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}    ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
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
                        print(f"{Fore.YELLOW}    ⚠ {LANG[language]['error']}: Line {i} - {key} {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}    ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}    ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Function for Web3 connection
def connect_web3(language: str = 'id'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if w3.is_connected():
            print(f"{Fore.GREEN}    ✔ {LANG[language]['connect_success']} | Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
            return w3
        else:
            print(f"{Fore.RED}    ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}    ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Helper function to get gas price with retries
async def get_gas_price_with_retries(w3: Web3, language: str = 'id', max_retries=5):
    for i in range(max_retries):
        try:
            gas_price = w3.eth.gas_price
            if gas_price > 0:
                return gas_price
            else:
                print(f"{Fore.YELLOW}    ⚠ Harga gas 0 Gwei terdeteksi (dari RPC). Menggunakan 1 Gwei sebagai minimal.{Style.RESET_ALL}")
                return w3.to_wei(1, 'gwei')
        except Exception as e:
            error_str = str(e)
            if "rate exceeded" in error_str.lower() or "too many requests" in error_str.lower():
                wait_time = 10 # Fixed delay for rate limit during gas price fetch
                print(f"{Fore.YELLOW}    ⚠ Gagal mendapatkan harga gas (Rate limit). Menunggu {wait_time:.2f} detik ({i+1}/{max_retries})...{Style.RESET_ALL}")
                await asyncio.sleep(wait_time)
            else:
                print(f"{Fore.YELLOW}    ⚠ Gagal mendapatkan harga gas: {str(e)}. Mencoba lagi dalam 5 detik ({i+1}/{max_retries})...{Style.RESET_ALL}")
                await asyncio.sleep(5)
    print(f"{Fore.RED}    ✖ Gagal mendapatkan harga gas yang valid setelah {max_retries} percobaan. Menggunakan harga gas minimal 1 Gwei.{Style.RESET_ALL}")
    return w3.to_wei(1, 'gwei') # Fallback to 1 Gwei if all retries fail

# Function to swap tokens
async def swap_tokens(w3: Web3, private_key: str, token_in: str, token_out: str, amount_in: int, token_in_symbol: str, token_out_symbol: str, language: str = 'id'):
    account = Account.from_key(private_key)
    router_contract = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_ADDRESS), abi=ROUTER_ABI)

    try:
        # Approve token before swap
        if not await approve_token(w3, private_key, token_in, ROUTER_ADDRESS, amount_in, language):
            return False

        # Prepare swap parameters
        swap_params = {
            "tokenIn": Web3.to_checksum_address(token_in),
            "tokenOut": Web3.to_checksum_address(token_out),
            "fee": 3000,  # 0.3%
            "recipient": account.address,
            "deadline": int(time.time()) + 1800,  # 30 minutes
            "amountIn": amount_in,
            "amountOutMinimum": 0,
            "sqrtPriceLimitX96": 0,
        }

        # Get transaction parameters
        nonce = w3.eth.get_transaction_count(account.address)
        
        # --- PRIMARY CHANGE: DYNAMIC GAS PRICE WITH RETRY ---
        gas_price = await get_gas_price_with_retries(w3, language)
        print(f"{Fore.YELLOW}    - Harga Gas yang digunakan: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei{Style.RESET_ALL}")
        # --- END OF CHANGE ---
        
        gas_limit = 500000 # Reasonable default for swap if estimation fails
        
        # Try estimating gas with retries for rate limits
        for i in range(3): # Max 3 retries for gas estimation
            try:
                estimated_gas = router_contract.functions.exactInputSingle(swap_params).estimate_gas({
                    'from': account.address,
                    'value': 0
                })
                gas_limit = int(estimated_gas * 1.20) # Increased buffer to 20%
                print(f"{Fore.YELLOW}    - Estimasi Gas: {estimated_gas} | Batas Gas yang digunakan: {gas_limit}{Style.RESET_ALL}")
                break # Exit loop if estimation successful
            except Exception as e:
                error_str = str(e)
                if "rate exceeded" in error_str.lower() or "too many requests" in error_str.lower():
                    wait_time = 10 # Fixed delay for rate limit during gas estimation
                    print(f"{Fore.YELLOW}    ⚠ Rate limit saat estimasi gas. Menunggu {wait_time:.2f} detik ({i+1}/3)...{Style.RESET_ALL}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"{Fore.YELLOW}    - Tidak dapat mengestimasi gas: {str(e)}. Menggunakan gas default: {gas_limit} (disesuaikan){Style.RESET_ALL}")
                    break # Exit if it's not a rate limit error or after retries

        # Check if user has enough A0GI for gas
        balance_a0gi = w3.from_wei(w3.eth.get_balance(account.address), 'ether')
        required_balance_a0gi = w3.from_wei(gas_limit * gas_price, 'ether')
        if balance_a0gi < required_balance_a0gi:
            print(f"{Fore.RED}    ✖ {LANG[language]['no_balance']} (Perlu: {required_balance_a0gi:.6f} A0GI, Punya: {balance_a0gi:.6f} A0GI){Style.RESET_ALL}")
            return False

        # Function to execute transaction with nonce and rate limit handling
        async def execute_transaction_with_nonce_handling(nonce=None):
            max_retries = 5 # Increased retry attempts
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # If nonce is not provided, get from network
                    if nonce is None:
                        nonce = w3.eth.get_transaction_count(account.address)
                    
                    # Build transaction
                    tx = router_contract.functions.exactInputSingle(swap_params).build_transaction({
                        'from': account.address,
                        'nonce': nonce,
                        'gas': gas_limit,
                        'gasPrice': gas_price,
                        'chainId': CHAIN_ID,
                    })
                    
                    print(f"{Fore.CYAN}    > {LANG[language]['swapping']} (Nonce: {nonce}){Style.RESET_ALL}")
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                    receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                    
                    return True, receipt, tx_hash, tx_link
                
                except Exception as e:
                    error_str = str(e)
                    # Nonce handling
                    if "invalid nonce" in error_str.lower() or "nonce too low" in error_str.lower():
                        try:
                            import re
                            match = re.search(r'expected (0x[0-9a-fA-F]+)|expected ([\d]+)', error_str)
                            if match:
                                if match.group(1): # Hex value
                                    expected_nonce = int(match.group(1), 16)
                                else: # Decimal value
                                    expected_nonce = int(match.group(2))
                                print(f"{Fore.YELLOW}    ⚠ Nonce tidak valid. Mencoba lagi dengan nonce: {expected_nonce}{Style.RESET_ALL}")
                                nonce = expected_nonce
                                retry_count += 1
                                await asyncio.sleep(2) # Add small delay for nonce error
                            else:
                                print(f"{Fore.YELLOW}    ⚠ Nonce tidak valid. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                                await asyncio.sleep(2)
                                nonce = w3.eth.get_transaction_count(account.address)
                                retry_count += 1
                        except Exception as parse_e:
                            print(f"{Fore.YELLOW}    ⚠ Gagal mengurai nonce dari error: {parse_e}. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                            await asyncio.sleep(2)
                            nonce = w3.eth.get_transaction_count(account.address)
                            retry_count += 1
                    # Rate limit handling - MORE AGGRESSIVE BACKOFF
                    elif "rate exceeded" in error_str.lower() or "too many requests" in error_str.lower():
                        wait_time = 10 # Fixed delay for rate limit during tx execution
                        print(f"{Fore.YELLOW}    ⚠ Rate limit exceeded. Menunggu {wait_time:.2f} detik sebelum mencoba lagi...{Style.RESET_ALL}")
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        nonce = w3.eth.get_transaction_count(account.address) # Get fresh nonce after waiting
                    else:
                        print(f"{Fore.RED}    ✖ Swap gagal: {str(e)}{Style.RESET_ALL}")
                        return False, None, None, None
            
            print(f"{Fore.RED}    ✖ Swap gagal setelah {max_retries} kali percobaan{Style.RESET_ALL}")
            return False, None, None, None

        # Execute transaction with nonce and rate limit handling
        success, receipt, tx_hash, tx_link = await execute_transaction_with_nonce_handling()
        
        if success and receipt.status == 1:
            try:
                amount_out = 0 # Default if not found
                # Logic to decode Transfer log (optional, as this can be complex)
                if receipt.logs:
                    token_out_contract = w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI)
                    # Topic for Transfer(address from, address to, uint256 value)
                    transfer_event_topic = Web3.keccak(text="Transfer(address,address,uint256)")

                    for log in receipt.logs:
                        if log.address == Web3.to_checksum_address(token_out) and \
                           log.topics and log.topics[0] == transfer_event_topic:
                            try:
                                # Topics: [0] = signature, [1] = from (indexed), [2] = to (indexed)
                                # Data: value
                                # Check if 'to' address in log topics matches current account
                                # log.topics[2] is the 'to' address as an indexed topic (bytes32)
                                if len(log.topics) >= 3 and Web3.to_checksum_address('0x' + log.topics[2].hex()[-40:]) == account.address:
                                    decoded_data = abi.decode(['uint256'], log.data)
                                    if decoded_data:
                                        amount_out = decoded_data[0]
                                        break
                            except Exception as decode_e:
                                print(f"{Fore.YELLOW}    ⚠ Gagal mendecode log Transfer: {decode_e}{Style.RESET_ALL}")
                                amount_out = 0

                if amount_out == 0:
                    print(f"{Fore.YELLOW}    ⚠ Tidak dapat mengambil jumlah token keluar secara pasti dari log. Mungkin log tidak standar atau tidak ditemukan.{Style.RESET_ALL}")

                # Ensure token_in and token_out symbols exist in TOKENS before accessing
                token_in_balance = w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=ERC20_ABI).functions.balanceOf(account.address).call() / 10**TOKENS.get(token_in_symbol, {"decimals": 18})["decimals"]
                token_out_balance = w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI).functions.balanceOf(account.address).call() / 10**TOKENS.get(token_out_symbol, {"decimals": 18})["decimals"]
                
                print(f"{Fore.GREEN}    ✔ {LANG[language]['success']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - {LANG[language]['address']}: {account.address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - Jumlah masuk: {amount_in / (10**TOKENS.get(token_in_symbol, {'decimals': 18})['decimals']):.6f} {token_in_symbol}{Style.RESET_ALL}")
                if amount_out > 0:
                    print(f"{Fore.YELLOW}      - Jumlah keluar: {amount_out / (10**TOKENS.get(token_out_symbol, {'decimals': 18})['decimals']):.6f} {token_out_symbol}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - {LANG[language]['balance']} {token_in_symbol}: {token_in_balance:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - {LANG[language]['balance']} {token_out_symbol}: {token_out_balance:.6f}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            except Exception as e:
                print(f"{Fore.GREEN}    ✔ {LANG[language]['success']} (Tidak dapat mengambil detail lengkap: {str(e)}){Style.RESET_ALL}")
                print(f"{Fore.YELLOW}      - Tx: {tx_link}{Style.RESET_ALL}")
                return True
        else:
            if tx_link:
                print(f"{Fore.RED}    ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}    ✖ {LANG[language]['failure']}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}    ✖ Swap gagal: {str(e)}{Style.RESET_ALL}")
        return False

# Function to approve token
async def approve_token(w3: Web3, private_key: str, token_address: str, spender: str, amount: int, language: str = 'id'):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    
    try:
        allowance = token_contract.functions.allowance(account.address, spender).call()
        if allowance >= amount: # Check if allowance is sufficient
            print(f"{Fore.GREEN}    ✔ Sudah ada allowance yang cukup untuk {spender}{Style.RESET_ALL}")
            return True

        # Set approval for the specific amount to be swapped (not unlimited)
        approval_amount = amount # Set approval only for the amount to be swapped
        print(f"{Fore.YELLOW}    > Mengatur persetujuan untuk jumlah spesifik ({amount / (10**TOKENS.get(next(iter(TOKENS)), {'decimals': 18})['decimals']):.6f} token){Style.RESET_ALL}")
        
        nonce = w3.eth.get_transaction_count(account.address)
        
        gas_price = await get_gas_price_with_retries(w3, language) # Get gas price with retries
        print(f"{Fore.YELLOW}    - Harga Gas yang digunakan: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei{Style.RESET_ALL}")
        
        gas_limit = 60000 # Reasonable default for approve
        
        # Try estimating gas with retries for rate limits
        for i in range(3): # Max 3 retries for gas estimation
            try:
                estimated_gas = token_contract.functions.approve(spender, approval_amount).estimate_gas({
                    'from': account.address
                })
                gas_limit = int(estimated_gas * 1.20) # Increased buffer to 20%
                break # Exit loop if estimation successful
            except Exception as e:
                error_str = str(e)
                if "rate exceeded" in error_str.lower() or "too many requests" in error_str.lower():
                    wait_time = 10 # Fixed delay for rate limit during gas estimation
                    print(f"{Fore.YELLOW}    ⚠ Rate limit saat estimasi gas approve. Menunggu {wait_time:.2f} detik ({i+1}/3)...{Style.RESET_ALL}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"{Fore.YELLOW}    - Tidak dapat mengestimasi gas untuk approve: {str(e)}. Menggunakan gas default: {gas_limit} (disesuaikan){Style.RESET_ALL}")
                    break # Exit if it's not a rate limit error or after retries

        # Function to execute approve with nonce and rate limit handling
        async def execute_approve_with_nonce_handling(nonce=None):
            max_retries = 5 # Increased retry attempts
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # If nonce is not provided, get from network
                    if nonce is None:
                        nonce = w3.eth.get_transaction_count(account.address)
                    
                    # Build transaction with maximum approval
                    tx = token_contract.functions.approve(spender, approval_amount).build_transaction({
                        'from': account.address,
                        'nonce': nonce,
                        'gas': gas_limit,
                        'gasPrice': gas_price,
                        'chainId': CHAIN_ID,
                    })
                    
                    print(f"{Fore.CYAN}    > {LANG[language]['approving']} (Nonce: {nonce}){Style.RESET_ALL}")
                    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                    
                    return True, receipt, tx_hash
                
                except Exception as e:
                    error_str = str(e)
                    # Nonce handling
                    if "invalid nonce" in error_str.lower() or "nonce too low" in error_str.lower():
                        try:
                            import re
                            match = re.search(r'expected (0x[0-9a-fA-F]+)|expected ([\d]+)', error_str)
                            if match:
                                if match.group(1):
                                    expected_nonce = int(match.group(1), 16)
                                else:
                                    expected_nonce = int(match.group(2))
                                print(f"{Fore.YELLOW}    ⚠ Nonce tidak valid. Mencoba lagi dengan nonce: {expected_nonce}{Style.RESET_ALL}")
                                nonce = expected_nonce
                                retry_count += 1
                                await asyncio.sleep(2)
                            else:
                                print(f"{Fore.YELLOW}    ⚠ Nonce tidak valid. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                                await asyncio.sleep(2)
                                nonce = w3.eth.get_transaction_count(account.address)
                                retry_count += 1
                        except Exception as parse_e:
                            print(f"{Fore.YELLOW}    ⚠ Gagal mengurai nonce dari error: {parse_e}. Mendapatkan nonce baru dari jaringan...{Style.RESET_ALL}")
                            await asyncio.sleep(2)
                            nonce = w3.eth.get_transaction_count(account.address)
                            retry_count += 1
                    # Rate limit handling - MORE AGGRESSIVE BACKOFF
                    elif "rate exceeded" in error_str.lower() or "too many requests" in error_str.lower():
                        wait_time = 10 # Fixed delay for rate limit during tx execution
                        print(f"{Fore.YELLOW}    ⚠ Rate limit exceeded. Menunggu {wait_time:.2f} detik sebelum mencoba lagi...{Style.RESET_ALL}")
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        nonce = w3.eth.get_transaction_count(account.address) # Get fresh nonce after waiting
                    else:
                        print(f"{Fore.RED}    ✖ Approve gagal: {str(e)}{Style.RESET_ALL}")
                        return False, None, None
            
            print(f"{Fore.RED}    ✖ Approve gagal setelah {max_retries} kali percobaan{Style.RESET_ALL}")
            return False, None, None

        # Execute transaction with nonce and rate limit handling
        success, receipt, tx_hash = await execute_approve_with_nonce_handling()
        
        if success and receipt.status == 1:
            print(f"{Fore.GREEN}    ✔ Approve berhasil | Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            return True
        else:
            if tx_hash:
                print(f"{Fore.RED}    ✖ Approve gagal | Tx: {EXPLORER_URL}{tx_hash.hex()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}    ✖ Approve gagal{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}    ✖ Approve gagal: {str(e)}{Style.RESET_ALL}")
        return False

# Function to get swap count
def get_swap_count(language: str = 'id') -> int:
    print_border(LANG[language]['enter_swap_count'], Fore.YELLOW)
    while True:
        try:
            swap_count_input = input(f"{Fore.YELLOW}    > {LANG[language]['swap_count_prompt']}{Style.RESET_ALL}")
            swap_count = int(swap_count_input) if swap_count_input.strip() else 1
            if swap_count <= 0:
                print(f"{Fore.RED}    ✖ {LANG[language]['error']}: {LANG[language]['swap_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}    ✔ {LANG[language]['selected']}: {swap_count} swaps{Style.RESET_ALL}")
                return swap_count
        except ValueError:
            print(f"{Fore.RED}    ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Function to display balances
def display_balances(w3: Web3, account_address: str, language: str = 'id'):
    for symbol, token_info in TOKENS.items():
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(token_info['address']), abi=ERC20_ABI)
            balance_wei = contract.functions.balanceOf(account_address).call()
            balance = balance_wei / (10**token_info['decimals'])
            print(f"{Fore.YELLOW}    - {LANG[language]['balance']} {symbol}: {balance:.6f}{Style.RESET_ALL}")
        except Exception as e:
            # Silently skip if fetching token balance fails (e.g., no balance or RPC issue)
            pass

    try:
        a0gi_balance = w3.from_wei(w3.eth.get_balance(account_address), 'ether')
        print(f"{Fore.YELLOW}    - {LANG[language]['balance']} A0GI: {a0gi_balance:.6f}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}    ✖ Error fetching A0GI balance: {str(e)}{Style.RESET_ALL}")


# Random Swap
async def random_swap(w3: Web3, private_key: str, swap_count: int, percent: float, wallet_index: int, language: str = 'id'):
    account = Account.from_key(private_key)
    successful_swaps = 0
    
    for swap_num in range(swap_count):
        print(f"{Fore.CYAN}    > {LANG[language]['swap']} {swap_num + 1}/{swap_count}{Style.RESET_ALL}")
        
        # Display balances for the current account
        display_balances(w3, account.address, language)
        
        # Get list of tokens with a positive balance
        token_balances = {}
        for symbol, token_data in TOKENS.items():
            try:
                contract = w3.eth.contract(address=Web3.to_checksum_address(token_data['address']), abi=ERC20_ABI)
                balance = contract.functions.balanceOf(account.address).call()
                token_balances[symbol] = balance
            except Exception as e:
                print(f"{Fore.YELLOW}    ⚠ Gagal mengambil saldo {symbol}: {str(e)}. Melewatkan token ini untuk swap acak.{Style.RESET_ALL}")
                token_balances[symbol] = 0
        
        tokens_with_balance = [symbol for symbol, balance in token_balances.items() if balance > 0]
        if not tokens_with_balance:
            print(f"{Fore.RED}    ✖ {LANG[language]['no_balance']}{Style.RESET_ALL}")
            break

        token_in_symbol = None
        for _ in range(len(TOKENS)): # Try all available tokens once
            candidate_symbol = random.choice(list(TOKENS.keys()))
            if token_balances.get(candidate_symbol, 0) > 0:
                token_in_symbol = candidate_symbol
                break
        
        if token_in_symbol is None:
            print(f"{Fore.RED}    ✖ Tidak ada token dengan saldo yang cukup untuk di-swap.{Style.RESET_ALL}")
            break

        token_in_address = TOKENS[token_in_symbol]["address"]
        balance_wei = token_balances[token_in_symbol]
        balance = balance_wei / 10**TOKENS[token_in_symbol]["decimals"]
        
        # Calculate amount based on percentage of balance
        amount = balance * (percent / 100)
        amount_in = int(amount * (10**TOKENS[token_in_symbol]["decimals"]))
        
        if amount_in <= 0:
            print(f"{Fore.RED}    ✖ {LANG[language]['no_balance']} (Saldo {token_in_symbol} terlalu kecil untuk di-swap {percent}%: {balance:.6f}){Style.RESET_ALL}")
            remaining_tokens = [s for s in tokens_with_balance if s != token_in_symbol]
            if remaining_tokens:
                print(f"{Fore.YELLOW}    ℹ Mencoba token lain dari daftar saldo yang tersedia.{Style.RESET_ALL}")
                continue
            else:
                print(f"{Fore.RED}    ✖ Tidak ada token lain dengan saldo yang cukup untuk di-swap.{Style.RESET_ALL}")
                break
            
        # Display calculation details
        print(f"{Fore.YELLOW}    > {LANG[language]['calculating_amount'].format(percent=percent, balance=balance, amount=amount, symbol=token_in_symbol)}{Style.RESET_ALL}")

        # Choose token_out_symbol ensuring it's different from token_in_symbol
        available_token_out_symbols = [s for s in TOKENS.keys() if s != token_in_symbol]
        if not available_token_out_symbols:
            print(f"{Fore.RED}    ✖ Tidak ada token keluar yang tersedia untuk swap dari {token_in_symbol}{Style.RESET_ALL}")
            break
        token_out_symbol = random.choice(available_token_out_symbols)
        token_out_address = TOKENS[token_out_symbol]["address"]

        if await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language):
            successful_swaps += 1
        
        if swap_num < swap_count - 1:
            delay = 10 # All internal swap delays changed to 10s
            print(f"{Fore.YELLOW}    ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    return successful_swaps

# Modified manual swap function
async def manual_swap(w3: Web3, private_key: str, wallet_index: int, language: str = 'id', pair_choice=None, percent=None):
    account = Account.from_key(private_key)
    
    # 1. First display balances for this wallet
    print_separator()
    print(f"{Fore.CYAN}    > Saldo token yang tersedia untuk dompet ini:{Style.RESET_ALL}")
    display_balances(w3, account.address, language)
    print_separator()
    
    # 2. Use provided pair choice or ask from user
    if pair_choice is None:
        print_border(LANG[language]['select_manual_swap'], Fore.YELLOW)
        for i in range(1, 7):
            print(f"{Fore.GREEN}      ├─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}" if i < 6 else 
                f"{Fore.GREEN}      └─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}")
        
        while True:
            try:
                pair_choice = int(input(f"{Fore.YELLOW}    > {LANG[language]['manual_swap_prompt']}{Style.RESET_ALL}"))
                if pair_choice in range(1, 7):
                    break
            except ValueError:
                print(f"{Fore.RED}    ✖ {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            print(f"{Fore.RED}    ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")

    pairs = {
        1: ("USDT", "ETH"), 2: ("ETH", "USDT"), 3: ("USDT", "BTC"),
        4: ("BTC", "USDT"), 5: ("BTC", "ETH"), 6: ("ETH", "BTC")
    }
    
    token_in_symbol, token_out_symbol = pairs[pair_choice]
    token_in_address = TOKENS[token_in_symbol]["address"]
    token_out_address = TOKENS[token_out_symbol]["address"]
    
    print(f"{Fore.GREEN}    ✔ Menggunakan pasangan: {token_in_symbol} -> {token_out_symbol}{Style.RESET_ALL}")
    
    # 3. Get current balance of selected token
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_in_address), abi=ERC20_ABI)
    balance_wei = token_contract.functions.balanceOf(account.address).call()
    balance = balance_wei / 10**TOKENS[token_in_symbol]["decimals"]
    
    if balance <= 0:
        print(f"{Fore.RED}    ✖ {LANG[language]['no_balance']} (Tidak ada {token_in_symbol} untuk di-swap){Style.RESET_ALL}")
        return 0
    
    # 4. Use provided percentage or ask from user
    if percent is None:
        percent = get_swap_percentage(language)
    else:
        print(f"{Fore.GREEN}    ✔ {LANG[language]['selected_percent'].format(percent=percent)}{Style.RESET_ALL}")
    
    # 5. Calculate actual amount based on percentage
    amount = balance * (percent / 100)
    amount_in = int(amount * (10**TOKENS[token_in_symbol]["decimals"])) # Ensure correct decimal conversion
    
    if amount_in <= 0:
        print(f"{Fore.RED}    ✖ {LANG[language]['no_balance']} (Saldo {token_in_symbol} terlalu kecil untuk di-swap {percent}%: {balance:.6f}){Style.RESET_ALL}")
        return 0

    # 6. Display calculation details
    print(f"{Fore.YELLOW}    > {LANG[language]['calculating_amount'].format(percent=percent, balance=balance, amount=amount, symbol=token_in_symbol)}{Style.RESET_ALL}")
    
    # 7. Execute swap with calculated amount
    success = await swap_tokens(w3, private_key, token_in_address, token_out_address, amount_in, token_in_symbol, token_out_symbol, language)
    return 1 if success else 0

async def run_swaptoken(language: str = 'id'):
    print(Fore.MAGENTA + ASCII_INTRO + Style.RESET_ALL) # Print ASCII art
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}    {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print_separator()

    while True:
        print_border(LANG[language]['select_swap_type'], Fore.YELLOW)
        print(f"{Fore.GREEN}      ├─ {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}      └─ {LANG[language]['manual_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}    > {LANG[language]['choice_prompt']}{Style.RESET_ALL}").strip()

        if choice in ['1', '2']:
            break
        print(f"{Fore.RED}    ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        print()

    if choice == '1':
        swap_count = get_swap_count(language)
        percent = get_swap_percentage(language)
    else:
        if private_keys:
            first_account = Account.from_key(private_keys[0][1])
            print(f"{Fore.CYAN}    > Saldo contoh dari dompet pertama:{Style.RESET_ALL}")
            display_balances(w3, first_account.address, language)
            print_separator()
        
        print_border(LANG[language]['select_manual_swap'], Fore.YELLOW)
        for i in range(1, 7):
            print(f"{Fore.GREEN}      ├─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}" if i < 6 else 
                f"{Fore.GREEN}      └─ {LANG[language]['manual_swap_options'][i]}{Style.RESET_ALL}")
        
        while True:
            try:
                pair_choice = int(input(f"{Fore.YELLOW}    > {LANG[language]['manual_swap_prompt']}{Style.RESET_ALL}"))
                if pair_choice in range(1, 7):
                    break
            except ValueError:
                print(f"{Fore.RED}    ✖ {LANG[language]['invalid_number']}{Style.RESET_ALL}")
            print(f"{Fore.RED}    ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        
        percent = get_swap_percentage(language)
        swap_count = 1 # For manual swap, it's one swap per wallet

    print_separator()

    total_swaps = swap_count * len(private_keys) if choice == '1' else len(private_keys)
    successful_swaps = 0

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()
        
        if choice == '1':
            print_border(LANG[language]['start_random'].format(swap_count=swap_count), Fore.CYAN)
            successful_swaps += await random_swap(w3, private_key, swap_count, percent, i, language)
        else:
            print_border(LANG[language]['start_manual'], Fore.CYAN)
            successful_swaps += await manual_swap(w3, private_key, i, language, pair_choice, percent)
        
        # Delay between wallets to prevent rate limits if there are many wallets
        if i < len(private_keys):
            inter_wallet_delay = 10 # Fixed 10 seconds as requested
            print(f"{Fore.YELLOW}    ℹ Menjeda {inter_wallet_delay:.2f} detik sebelum memproses dompet berikutnya...{Style.RESET_ALL}")
            await asyncio.sleep(inter_wallet_delay)
        print() # Newline for separation

    print_border(LANG[language]['completed'].format(successful=successful_swaps, total=total_swaps), Fore.GREEN)
    print()


if __name__ == "__main__":
    asyncio.run(run_swaptoken('id'))
