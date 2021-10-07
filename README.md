# mpunks Miner Bundle Windows x64

THIS IS EXPERIMENTAL SOFTWARE. USE AT YOUR OWN RISK.

Read LICENSE and NOTICE.

VirusTotal scan of `mpunks-miner-controller.exe`: https://www.virustotal.com/gui/file/a284579c528b5326226475ba1e359d65a2b478b30bcc7752d845930c1a8a4d14?nocache=1

**If you would like to run the `mpunks-miner-controller` from source instead of using the executable, feel free to clone the repository:** https://github.com/mineablepunks/mpunks-miner-controller

## How to Mine

Skipping any of these steps will result in issues. Please take the time to read all of this.

### Step 1: Download or clone this repository!

### Step 2: Configure the `mpunks-miner-controller`

Create a `.env.local` file from the `.env` template.

Read LICENSE and NOTICE. Then fill in environment variables within `.env.local`.

Special notes:

`PRIVATE_KEY`

- THE PRIVATE KEY MUST BE PREFIXED WITH `0x`
- For this miner to automatically submit valid nonces, you will need to populate the PRIVATE_KEY variable with your wallet private key. For security reasons, we recommend making a new wallet and depositing a smaller amount of ETH to pay for transaction fees. A minimum of 0.1 ETH is required for this.

- **Again, without PRIVATE_KEY, the miner won't be able to submit valid nonces for you. You will have to watch the mining output and manually submit the nonces.**

`WEB3_HOST`

- This must point to a valid Ethereum node URL. The default of `https://cloudflare-eth.com` should work, but we have noticed instability with this node. We recommend making a free `infura` or `alchemy` account instead of using `cloudflare-eth`.

`MAX_GAS_PRICE_GWEI`

- **THE DEFAULT IS 150 GWEI. This could result in a worst-case mint transaction cost of 0.21 ETH!**

### Step 3: Set up the `mpunks-miner-supervisor`

- Install Python 3
  - You can do this by downloading/installing Python 3 for Windows from the official Python website.
  - **Be sure to add the `python` executable (and `pip`) to your PATH**
- Open up a terminal (`cmd.exe` or `powershell.exe` will do)
- `cd` into this directory
- Run `pip install -r requirements.txt`

### Step 4: Run the `mpunks-miner-controller.exe` file

Double-click the executable, or from within your favorite terminal run `./mpunks-miner-controller.exe`

### Step 5: Run the `mpunks-miner-supervisor`

- If you don't have one open already, open up a terminal (`cmd.exe` or `powershell.exe` will do)
- `cd` into this directory
- Run `python mpunks-miner-supervisor.py`

# THE `mpunks-miner-controller` MUST BE RUNNING in order for the `mpunks-miner-supervisor` to work!

## Notes

- The `mpunks-miner-supervisor` should print `>>> STATS` lines that show your hash rate, as well as how many nonces have been tried so far.
