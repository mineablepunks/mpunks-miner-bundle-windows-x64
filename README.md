# mpunks Miner Bundle Windows x64

THIS IS EXPERIMENTAL SOFTWARE. USE AT YOUR OWN RISK.

Read LICENSE and NOTICE.

VirusTotal scan of `mpunks-miner-controller.exe`: https://www.virustotal.com/gui/file/ea3ff1ce72a9cee5b12e93568ad3c5129bca3c260e9908ad0706cec0c75c7f61/detection

**If you would like to run the `mpunks-miner-controller` from source instead of using the executable, feel free to clone the repository:** https://github.com/mineablepunks/mpunks-miner-controller

## How to Mine

Skipping any of these steps will result in issues. Please take the time to read all of this.

### Step 1: Configure the `mpunks-miner-controller`
Create a `.env.local` file from the `.env` template like this:
```
cp .env .env.local
```
Read LICENSE and NOTICE. Then fill in environment variables within `.env.local`.

Special notes:

`PRIVATE_KEY`

- For this miner to automatically submit valid nonces, you will need to populate the PRIVATE_KEY variable with your wallet private key. For security reasons, we recommend making a new wallet and depositing a smaller amount of ETH to pay for transaction fees. A minimum of 0.1 ETH is required for this.

- **Again, without PRIVATE_KEY, the miner won't be able to submit valid nonces for you. You will have to watch the mining output and manually submit the nonces.**

`WEB3_HOST`

- This must point to a valid Ethereum node URL. The default of `https://cloudflare-eth.com` should work, but we have noticed instability with this node. We recommend making a free `infura` or `alchemy` account instead of using `cloudflare-eth`.

`MAX_GAS_PRICE_GWEI`

- **THE DEFAULT IS 150 GWEI. This could result in a worst-case mint transaction cost of 0.21 ETH!**

### Step 2: Set up the `mpunks-miner-supervisor`
- Install Python 3.9
- Open up a terminal (`cmd.exe` or `powershell.exe` will do)
- `cd` into this directory
- Run `pip install -r requirements.txt`

### Step 3: Run the `mpunks-miner-controller.exe` file
Double-click the executable, or from within your favorite terminal run `./mpunks-miner-controller.exe`

### Step 4: Run the `mpunks-miner-supervisor`
- If you don't have one open already, open up a terminal (`cmd.exe` or `powershell.exe` will do)
- `cd` into this directory
- Run `python mpunks-miner-supervisor.py`

## Notes
- The `mpunks-miner-supervisor` should print `>>> STATS` lines that show your hash rate, as well as how many nonces have been tried so far.
