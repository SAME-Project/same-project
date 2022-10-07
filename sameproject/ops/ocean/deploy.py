from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import os

def deploy(base_path: Path,
           root_file: str, # root function with notebook code (string)
           config: SameConfig):
    return
#     ocean, OCEAN_token, provider_url = configure_ocean(config=config)
#     wallet = Wallet(ocean.web3, config.runtime_options.get("wallet_private_key"), transaction_timeout=20, block_confirmations=0)
#     print(f"wallet.address = '{wallet.address}'")
#     assert wallet.web3.eth.get_balance(wallet.address) > 0, "need ETH"
    
#     DATA_did = config.runtime_options.get("dt_did")
#     ALG_did = config.runtime_options.get("algo_did")
#     DATA_DDO = ocean.assets.resolve(DATA_did)  # make sure we operate on the updated and indexed metadata_cache_uri versions
#     ALG_DDO = ocean.assets.resolve(ALG_did)
#     compute_service = DATA_DDO.get_service('compute')
#     algo_service = ALG_DDO.get_service('access')
#     print(f'Algorithm DDO is {ALG_DDO}')        

#     if config.runtime_options.get("algo_verified") == False:
#         try:
#             trusted_algorithms.add_publisher_trusted_algorithm(DATA_DDO, ALG_DDO.did, 'https://aquarius.oceanprotocol.com')
#             ocean.assets.update(DATA_DDO, publisher_wallet=wallet)
#             verified = True
#         except:
#             verified = False
#             pass

#     # Datatoken buying
#     data_token_address = f'0x{DATA_did[7:]}'
#     data_token = ocean.get_data_token(data_token_address)
#     if data_token.balanceOf(wallet.address) < to_wei(1):
#         print('Not enough datatokens in wallet, buying...')
#         buy_dt(config, wallet, ocean, OCEAN_token, DATA_did)

#     algo_token_address = f'0x{ALG_did[7:]}'
#     algo_token = ocean.get_data_token(algo_token_address)
#     print(f"You have {pretty_ether_and_wei(algo_token.balanceOf(wallet.address), algo_token.symbol())} algorithm tokens.")
#     if config.runtime_options.get("algo_verified") == True or verified == True:
#         result = run_c2d(ocean, wallet, DATA_did, ALG_did, ALG_datatoken, compute_service, algo_service)
#         return result

# def configure_ocean(config):
#     conf = {
#     'network' : 'https://rinkeby.infura.io/v3/d163c48816434b0bbb3ac3925d6c6c80' if config.runtime_options.get("network") is None else config.runtime_options.get("network"),
#     'BLOCK_CONFIRMATIONS': 0,
#     'metadataCacheUri' : 'https://aquarius.oceanprotocol.com',
#     'providerUri' : 'https://provider.rinkeby.oceanprotocol.com',
#     'PROVIDER_ADDRESS': '0x00bd138abd70e2f00903268f3db08f2d25677c9e' if config.runtime_options.get("provider_address") is None else config.runtime_options.get("provider_address"),
#     'downloads.path': 'consume-downloads',
#     }

#     ocean = Ocean(conf)
#     OCEAN_token = BToken(ocean.web3, ocean.OCEAN_address)
#     provider_url = DataServiceProvider.get_url(ocean.config)

#     return ocean, OCEAN_token, provider_url

# def buy_dt(config, wallet, ocean, OCEAN_token, did):
#     """
#     Datatoken buying

#     Requirements:
#     - wallet from previous step
#     - datatoken DID and pool address
#     """
#     pool_address = config.runtime_options.get("dt_pool")
#     assert wallet is not None, "Wallet error, run pipeline again"
#     # Get asset, datatoken_address
#     asset = ocean.assets.resolve(did)
#     data_token_address = f'0x{did[7:]}'

#     print('Executing Transaction')
#     #my wallet
#     print(f"Environment Wallet Address = '{wallet.address}'")
#     print(f"Wallet OCEAN = {pretty_ether_and_wei(OCEAN_token.balanceOf(wallet.address))}")
#     print(f"Wallet ETH = {pretty_ether_and_wei(ocean.web3.eth.get_balance(wallet.address))}")
#     #Verify that wallet has ETH
#     assert ocean.web3.eth.get_balance(wallet.address) > 0, "need test ETH"
#     #Verify that wallet has OCEAN
#     assert OCEAN_token.balanceOf(wallet.address) > 0, "need test OCEAN"
#     data_token = ocean.get_data_token(data_token_address)
#     print('Buying Data Token')
#     ocean.pool.buy_data_tokens(
#         pool_address,
#         amount=to_wei(1), # buy 1.0 datatoken
#         max_OCEAN_amount=to_wei(config.runtime_options.get("max_dt_price")), # pay up to 10.0 OCEAN
#         from_wallet=wallet
#     )
#     print(f"You have {pretty_ether_and_wei(data_token.balanceOf(wallet.address), data_token.symbol())}.")

# def run_c2d(ocean, wallet, DATA_did, ALG_did, ALG_datatoken, compute_service, algo_service):
#     """
#     Running C2D
#     """
#     # order & pay for dataset
#     dataset_order_requirements = ocean.assets.order(
#         DATA_did, wallet.address, service_type=compute_service.type
#     )

#     DATA_order_tx_id = ocean.assets.pay_for_service(
#             ocean.web3,
#             dataset_order_requirements.amount,
#             dataset_order_requirements.data_token_address,
#             DATA_did,
#             compute_service.index,
#             ZERO_ADDRESS,
#             wallet,
#             dataset_order_requirements.computeAddress,
#         )

#     # order & pay for algo
#     algo_order_requirements = ocean.assets.order(
#         ALG_did, wallet.address, service_type=algo_service.type
#     )
#     ALG_order_tx_id = ocean.assets.pay_for_service(
#             ocean.web3,
#             algo_order_requirements.amount,
#             algo_order_requirements.data_token_address,
#             ALG_did,
#             algo_service.index,
#             ZERO_ADDRESS,
#             wallet,
#             algo_order_requirements.computeAddress,
#     )

#     compute_inputs = [ComputeInput(DATA_did, DATA_order_tx_id, compute_service.index)]
#     job_id = ocean.compute.start(
#         compute_inputs,
#         wallet,
#         algorithm_did=ALG_did,
#         algorithm_tx_id=ALG_order_tx_id,
#         algorithm_data_token=ALG_datatoken.address
#     )
#     print(f"Started compute job with id: {job_id}")

#     # for monitoring C2D status
#     while ocean.compute.status(DATA_did, job_id, wallet)['statusText'] != 'Job finished':
#         print(ocean.compute.status(DATA_did, job_id, wallet)['statusText'])
#         pass

#     # retrieving result
#     result = ocean.compute.result_file(DATA_did, job_id, 0, wallet)  # 0 index, means we retrieve the results from the first dataset index
#     return result