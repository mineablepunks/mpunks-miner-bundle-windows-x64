# mpunks Miner Bundle Windows x64

THIS IS EXPERIMENTAL SOFTWARE. USE AT YOUR OWN RISK.

Read LICENSE and NOTICE.

VirusTotal scan of `mpunks-miner-controller.exe`: https://www.virustotal.com/gui/file/a284579c528b5326226475ba1e359d65a2b478b30bcc7752d845930c1a8a4d14?nocache=1

**If you would like to run the `mpunks-miner-controller` from source instead of using the executable, feel free to clone the repository:** https://github.com/mineablepunks/mpunks-miner-controller

## The components and how they work together

#### `mpunks-miner-controller`

See the git repo for an explanation: https://github.com/mineablepunks/mpunks-miner-controller

#### `mpunks-miner-worker`

This is the compiled CUDA GPU miner. This is also open sourced here: https://github.com/mineablepunks/mpunks-miner-worker.

#### `mpunks-miner-supervisor`

This process manages the inputs, outputs, and lifecycle of the `mpunks-miner-worker`.

The `mpunks-miner-controller` provides mining inputs for the `mpunks-miner-worker`. The `mpunks-miner-supervisor` takes those inputs and creates the worker process, and restarts the worker when those inputs change.

The `mpunks-miner-worker` writes valid nonces out as files to a `validNonces` directory that the `mpunks-miner-supervisor` watches in order to submit the nonces to the `mpunks-miner-controller`.

## Requirements

- #### Windows
- #### An NVIDIA GPU
- #### Updated GPU drivers
- #### Python 3.9 or above (<= 3.8 WILL NOT WORK)
- #### A WEB3 RPC endpoint
  - #### Make an Infura or Alchemy account for this. You'll need to make a project and then get the web3 url for your project.

## How to Mine

Skipping any of these steps will result in issues. Please take the time to read all of this.

### Step 1: Download or clone this repository!

### Step 2: Configure the `mpunks-miner-controller`

Create a `.env.local` file from the `.env` template.

Read LICENSE and NOTICE.

Then, fill in environment variables within `.env.local`. If you agree with the LICENSE and NOTICE, and if you agree with the value of `MAX_GAS_PRICE_GWEI`, set those fields to `true`.

Special notes:

`PRIVATE_KEY`

- THE PRIVATE KEY MUST BE PREFIXED WITH `0x`
- To export from metamask: https://metamask.zendesk.com/hc/en-us/articles/360015289632-How-to-Export-an-Account-Private-Key
  - Make sure you add `0x` in front of your private key since metamask doesn't add it for you!
- For this miner to automatically submit valid nonces, you will need to populate the PRIVATE_KEY variable with your wallet private key. For security reasons, we recommend making a new wallet and depositing a smaller amount of ETH to pay for transaction fees.

  - The "smaller amount of ETH to pay for transaction fees" should be around 0.1 ETH on the safe side (varies based on gas price)

- **Again, without PRIVATE_KEY, the miner won't be able to submit valid nonces for you. You will have to watch the mining output and manually submit the nonces.**

`WEB3_HOST`

- This must point to a valid Ethereum node URL. We have found that `https://cloudflare-eth.com` is very unstable and we do not recommend using this endpoint. We recommend making a free `infura` or `alchemy` account.

`MAX_GAS_PRICE_GWEI`

- **THE DEFAULT IS 150 GWEI. This could result in a worst-case mint transaction cost of 0.21 ETH! Make sure you are okay with this.**

### Step 3: Set up the `mpunks-miner-supervisor`

- Install Python 3.9 or above (<= 3.8 WILL NOT WORK) or upgrade existing Python to 3.9
  - You can do this by downloading/installing Python 3.9 for Windows from the official Python website.
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
