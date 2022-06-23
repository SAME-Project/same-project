from sameproject.ops.runtime_options import register_option

register_option(
    "network",
    "The network to use for publishing algorithm and getting the dataset.",
    backend="ocean",
)

register_option(
    "provider_address",
    "Address of compute provider",
    backend="ocean",
)

register_option(
    "wallet_private_key",
    "Private key of user wallet",
    backend="ocean",
)

register_option(
    "dt_did",
    "Datatoken DID",
    backend="ocean",
)

register_option(
    "dt_pool",
    "Pool address for datatoken",
    backend="ocean",
)

register_option(
    "algo_tag",
    "Tag to refer to algorithm by",
    backend="ocean",
)

register_option(
    "algo_version",
    "Version of algorithm",
    backend="ocean",
)

register_option(
    "algo_url",
    "URL where Algorithm is stored",
    backend="ocean",
)

register_option(
    "algo_name",
    "Name of algorithm",
    backend="ocean",
)

register_option(
    "author",
    "Author of algorithm",
    backend="ocean",
)

register_option(
    "licence",
    "Algorithm Licence",
    backend="ocean",
)

register_option(
    "max_dt_price",
    "Maximum price willing to spend on datatokens.",
    backend="ocean",
)



