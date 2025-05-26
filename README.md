# 0G Labs Testnet Automation Swap Scripts

This repository contains a collection of Python scripts designed to automate various tasks on the 0G Labs Testnet token swapping,  These scripts are integrated with a central `autoswap.py` file for streamlined execution, supporting multiple private keys and a user-friendly CLI interface.

## Features Overview

### General Features

- **Multi-Account Support**: Reads private keys from `pvkey.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both Vietnamese and English output based on user selection.

#### 2. `swaptoken.py` - Swap Tokens
- **Description**: Swaps tokens (USDT, ETH, BTC) randomly or manually on the 0G Labs Testnet swap router.
- **Features**:
  - Supports random or manual swap pairs (e.g., USDT -> ETH).
  - User inputs for swap count and amount (default: 0.1 token).
  - Random delays (10-30 seconds) between swaps.
- **Usage**: Select from `python autoswap.py` menu, choose swap type and parameters.

## Installation

1. **Clone this repository:**
```sh
git clone https://github.com/kazmight/0g-Auto-Swap-TX.git
```
```sh
cd 0g-Auto-Swap-TX
```

2. **Set Environment:**
run the command:
```sh
python -m venv venv
```
- activate venv
```sh
source venv/bin/activate
```

3. **Install Dependencies:**
run the command:
```sh
pip install -r requirements.txt
```

4. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt
```

5. **Run:**
run the command:
```sh
python Autoswap.py
or 
python3 Autoswap.py
