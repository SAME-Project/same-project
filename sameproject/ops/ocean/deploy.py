from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
"""Boilerplate Ocean publishing and running c2d"""

import os
import _init_paths
from ocean_lib.data_provider.data_service_provider import DataServiceProvider
from ocean_lib.common.agreements.service_types import ServiceTypes
from ocean_lib.web3_internal.constants import ZERO_ADDRESS
from ocean_lib.web3_internal.currency import to_wei
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.assets import trusted_algorithms
from ocean_lib.services.service import Service
from ocean_lib.models.btoken import BToken #BToken is ERC20
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.config import Config


def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module
        print(f"Root module is {root_module.root}")
        
    config = Config('config.ini') # Ocean requires a config file with network, metadata, block, and provider info
    ocean = Ocean(config)
    OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
    provider_url = DataServiceProvider.get_url(ocean.config)


    """
    Algorithm publishing

    Requirements:

    - Model script on GitHub
    - wallet private key as environment variable
    - dataset we want to train on specified
    - model metadata (name, date, compute, etc.)
    """

    wallet = Wallet(ocean.web3, os.getenv('TEST_PRIVATE_KEY1'), transaction_timeout=20, block_confirmations=config.block_confirmations)
    print(f"wallet.address = '{wallet.address}'")
    assert wallet.web3.eth.get_balance(wallet.address) > 0, "need ETH"


    # Publish ALG datatoken
    ALG_datatoken = ocean.create_data_token('ALG1', 'ALG1', wallet, blob=ocean.config.metadata_cache_uri)
    ALG_datatoken.mint(wallet.address, to_wei(100), wallet)
    print(f"ALG_datatoken.address = '{ALG_datatoken.address}'")

    # Specify metadata and service attributes, for "GPR" algorithm script.
    # In same location as Branin test dataset. GPR = Gaussian Process Regression.
    ALG_metadata =  {
        "main": {
            "type": "algorithm",
            "algorithm": {
                "language": "python",
                "format": "docker-image",
                "version": "0.1", # project-specific
                "container": {
                "entrypoint": "python $ALGO",
                "image": "oceanprotocol/algo_dockers",
                "tag": "python-branin" # project-specific
                }
            },
            "files": [
        {
            "url": "https://raw.githubusercontent.com/trentmc/branin/main/gpr.py", # project-specific
            "index": 0,
            "contentType": "text/text",
        }
        ],
        "name": "gpr", "author": "Trent", "license": "CC0", # project-specific
        "dateCreated": "2020-01-28T10:55:11Z" # project-specific
        }
    }
    ALG_service_attributes = {
            "main": {
                "name": "ALG_dataAssetAccessServiceAgreement",
                "creator": wallet.address,
                "timeout": 3600 * 24,
                "datePublished": "2020-01-28T10:55:11Z",
                "cost": 1.0, # <don't change, this is obsolete>
            }
        }

    # Calc ALG service access descriptor. We use the same service provider as DATA
    ALG_access_service = Service(
        service_endpoint=provider_url,
        service_type=ServiceTypes.CLOUD_COMPUTE,
        attributes=ALG_service_attributes
    )

    # Publish metadata and service info on-chain
    ALG_ddo = ocean.assets.create(
    metadata=ALG_metadata, # {"main" : {"type" : "algorithm", ..}, ..}
    publisher_wallet=wallet,
    services=[ALG_access_service],
    data_token_address=ALG_datatoken.address)

    trusted_algorithms.add_publisher_trusted_algorithm('DATA_ddo', ALG_ddo.did, config.metadata_cache_uri) # project-specific
    ocean.assets.update('DATA_ddo', publisher_wallet=wallet) # project-specific

    """
    Datatoken buying

    Requirements:
    - wallet from previous step
    - datatoken DID and pool address
    """

    did = 'SPECIFY'
    pool_address = 'SPECIFY'

    wallet = Wallet(ocean.web3, private_key=private_key, transaction_timeout=20, block_confirmations=0)
    assert wallet is not None, "Wallet error, initialize app again"
    # Get asset, datatoken_address
    asset = ocean.assets.resolve(did)
    data_token_address = f'0x{did[7:]}'

    print('Executing Transaction')
    #my wallet
    print(f"Environment Wallet Address = '{wallet.address}'")
    print(f"Wallet OCEAN = {pretty_ether_and_wei(OCEAN_token.balanceOf(wallet.address))}")
    print(f"Wallet ETH = {pretty_ether_and_wei(ocean.web3.eth.get_balance(wallet.address))}")
    #Verify that Bob has ETH
    assert ocean.web3.eth.get_balance(wallet.address) > 0, "need test ETH"
    #Verify that Bob has OCEAN
    assert OCEAN_token.balanceOf(wallet.address) > 0, "need test OCEAN"
    # print(f"I have {pretty_ether_and_wei(data_token.balanceOf(wallet.address), data_token.symbol())}.")
    # assert data_token.balanceOf(wallet.address) >= to_wei(1), "Bob didn't get 1.0 datatokens"
    #Bob points to the service object
    fee_receiver = ZERO_ADDRESS # could also be market address
    #Bob buys 1.0 datatokens - the amount needed to consume the dataset.
    data_token = ocean.get_data_token(data_token_address)
    print('Buying Data Token')
    ocean.pool.buy_data_tokens(
        pool_address,
        amount=to_wei(1), # buy 1.0 datatoken
        max_OCEAN_amount=to_wei(10), # pay up to 10.0 OCEAN
        from_wallet=wallet
    )
    print(f"I have {pretty_ether_and_wei(data_token.balanceOf(wallet.address), data_token.symbol())}.")


    """
    Running C2D
    """

    DATA_did = DATA_ddo.did  # for convenience
    ALG_did = ALG_ddo.did
    DATA_DDO = ocean.assets.resolve(DATA_did)  # make sure we operate on the updated and indexed metadata_cache_uri versions
    ALG_DDO = ocean.assets.resolve(ALG_did)

    compute_service = DATA_DDO.get_service('compute')
    algo_service = ALG_DDO.get_service('access')

    from ocean_lib.web3_internal.constants import ZERO_ADDRESS
    from ocean_lib.models.compute_input import ComputeInput

    # order & pay for dataset
    dataset_order_requirements = ocean.assets.order(
        DATA_did, wallet.address, service_type=compute_service.type
    )

    DATA_order_tx_id = ocean.assets.pay_for_service(
            ocean.web3,
            dataset_order_requirements.amount,
            dataset_order_requirements.data_token_address,
            DATA_did,
            compute_service.index,
            ZERO_ADDRESS,
            wallet,
            dataset_order_requirements.computeAddress,
        )

    # order & pay for algo
    algo_order_requirements = ocean.assets.order(
        ALG_did, wallet.address, service_type=algo_service.type
    )
    ALG_order_tx_id = ocean.assets.pay_for_service(
            ocean.web3,
            algo_order_requirements.amount,
            algo_order_requirements.data_token_address,
            ALG_did,
            algo_service.index,
            ZERO_ADDRESS,
            wallet,
            algo_order_requirements.computeAddress,
    )

    compute_inputs = [ComputeInput(DATA_did, DATA_order_tx_id, compute_service.index)]
    job_id = ocean.compute.start(
        compute_inputs,
        wallet,
        algorithm_did=ALG_did,
        algorithm_tx_id=ALG_order_tx_id,
        algorithm_data_token=ALG_datatoken.address
    )
    print(f"Started compute job with id: {job_id}")

    # for monitoring C2D status
    print(ocean.compute.status(DATA_did, job_id, wallet))

    # retrieving result
    result = ocean.compute.result_file(DATA_did, job_id, 0, wallet)  # 0 index, means we retrieve the results from the first dataset index
    return result