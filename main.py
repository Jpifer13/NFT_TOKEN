import os
import asyncio
import subprocess
from src.Token import Token

if __name__ == '__main__':
    test_token = Token()
    test_token.set_config('https://api.testnet.solana.com')
    test_token.generate_keypair_file(f'{os.getcwd()}/key_pairs/my-keypair.json')
    test_token.set_keypair_file(f'{os.getcwd()}/key_pairs/my-keypair.json')
    print(f"Airdropping sol: {subprocess.run(['solana', 'airdrop', '1'], capture_output=True, text=True, timeout=30)}")
    test_token.get_sol_balance()
    print(f'SOL available: {test_token.sol}')
    test_token.create_nft()
    test_token.create_account()
    test_token.get_token_balance()
    print(f'Account balance available: {test_token.sol}')
    test_token.mint(number_of_tokens=100)
    test_token.get_accounts()