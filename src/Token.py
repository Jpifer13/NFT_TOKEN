import os
import subprocess
import atexit


class Token:
    def __init__(self):
        self.config = {}
        self.signature = []
        self.sol = None

        # run self destruct to delete all data on exit of runtime
        atexit.register(self.self_destruct)
    
    def get_config(self):
        output = subprocess.run(['solana', 'config', 'get'], capture_output=True, text=True)
        self.config = self._parse_output(output.stdout, output.stderr)
    
    def get_accounts(self):
        output = subprocess.run(['spl-token', 'accounts'], capture_output=True, text=True)
        self.config = self._parse_output(output.stdout, output.stderr)

    def get_sol_balance(self):
        output = subprocess.run(['solana', 'balance', self.pubkey, '--url', self.rpc_url], capture_output=True, text=True)
        if not output.stdout:
            print(f'Unable to retrieve balance on account: {self.pubkey}')
            print(output.stderr)
            return 0
        self.sol = output.stdout.split(' SOL')[0]
    
    def get_token_balance(self):
        output = subprocess.run(['spl-token', 'supply', self.token_addr], capture_output=True, text=True)
        if not output.stdout:
            print(f'Unable to retrieve balance on token: {self.token_addr}')
            print(output.stderr)
            return 0
        self.token_balance = output.stdout.split('\n')[0]
    
    def get_account_balance(self):
        output = subprocess.run(['spl-token', 'balance', self.account_addr], capture_output=True, text=True)
        if not output.stdout:
            print(f'Unable to retrieve balance on token: {self.account_addr}')
            print(output.stderr)
            return 0
        self.account_balance = output.stdout.split(' SOL')[0]
    
    def set_config(self, url:str):
        output = subprocess.run(['solana', 'config', 'set', '--url', url], capture_output=True, text=True)
        self.config = self._parse_output(output.stdout, output.stderr)

    def set_keypair_file(self, keypair_path: str):
        output = subprocess.run(['solana', 'config', 'set', '--keypair', keypair_path], capture_output=True, text=True)
        _ = self._parse_output(output.stdout, output.stderr)
    
    def set_keypair_hardware(self, drive: str):
        output = subprocess.run(['solana', 'config', 'set', '--keypair', drive], capture_output=True, text=True)
        _ = self._parse_output(output.stdout, output.stderr)
    
    def generate_keypair_file(self, keypair_path: str):
        output = subprocess.run(['solana-keygen', 'new', '--outfile', keypair_path, '--force', '--no-bip39-passphrase'], capture_output=True, text=True, timeout=5)
        _ = self._parse_output(output.stdout, output.stderr)
        if not self._verify_keypair_file():
            print('Keypair not verified...')
        print('Keypair verified...')
    
    def _verify_keypair_file(self):
        if not self.keypair_path:
            print('No keypair file found.')
            return None

        output = subprocess.run(['solana-keygen', 'verify', self.pubkey, self.keypair_path], capture_output=True, text=True, timeout=5)
        return True if 'Success' in output.stdout else False
    
    def create_nft(self):
        output = subprocess.run(['spl-token', 'create-token'], capture_output=True, text=True, timeout=30)
        _ = self._parse_output(output.stdout, output.stderr)
    
    def create_account(self):
        output = subprocess.run(['spl-token', 'create-account', self.token_addr], capture_output=True, text=True)
        _ = self._parse_output(output.stdout, output.stderr)
    
    def mint(self, number_of_tokens: int=1):
        output = subprocess.run(['spl-token', 'mint', self.token_addr, str(number_of_tokens)], capture_output=True, text=True, timeout=10)
        _ = self._parse_output(output.stdout, output.stderr)
    
    def self_destruct(self):
        # Delete key_pair from file
        print('Removing sensitive keypair file...')
        try:
            os.remove(self.keypair_path)
        except Exception as err:
            print(err)

    def _parse_output(self, stdout: str, stderr: str) -> dict:
        response = {}
        if stderr:
            print(f"Exception caught when retrieving config: {stderr}")
            raise Exception
        elif stdout:
            out_list = stdout.split('\n')
            phase = False
            for line in out_list:
                if line:
                    try:
                        if phase:
                            response['seed_phase'] = line
                            phase = False
                            continue

                        pair_list = line.split(': ')
                        response[pair_list[0].lower().strip().replace(' ', '_')] = pair_list[1].strip()
                    except Exception as _:
                        if 'save this seed' in line.lower():
                            phase = True
                        elif 'creating token' in line.lower():
                            response['token_addr'] = line.split('token ')[1]
                        elif 'creating account' in line.lower():
                            response['account_addr'] = line.split('account ')[1]
                        continue

        for key in response:
            if key == 'signature':
                self.signature.append(response[key])
                continue
            setattr(self, key, response[key])
        
        return response

