# Developing and training AI models in the decentralized web

## Ocean Protocol and Decentralized AI

The SAME Project allows data scientists to easily turn their Jupyter notebooks into executable scripts that can automatically be sent to any compute pipeline.

Ocean Protocol builds tools for the decentralized data economy, particularly, one of the core features of Ocean Protocol is the ability to train your models on private data, called Compute-to-Data (C2D).

In C2D, the data scientist first searches the Ocean Market for data they want to traain their algorithm on. Once they found a dataset they like, they would buy access to that dataset through Ocean Protocol's data tokens, which act as tickets denoting who can access some dataset and under what conditions. The data scientist must then publish their model on the Ocean Market as well and execute a series of steps to train their algorithm on the dataset on a separate Compute Provider. More details on C2D can be found [here](https://blog.oceanprotocol.com/v2-ocean-compute-to-data-guide-9a3491034b64).

Long-story short, the Ocean C2D is a perfect fit for the SAME Project, allowing data scientists to focus more on their model development rather than learning the ins and outs of Ocean Protocol's libraries.

## SAME-Ocean Template Quickstart

This short guide assumes you've already installed the SAME Project in your local environment, [here](https://sameproject.ml/getting-started/installing/) is a guide to get you started. 

While most of the Ocean deployment code is abstracted away in the SAME-Ocean template, there are some config parameters that you need to fill in to interact with the Ocean Market, in particular, you'll need a [Web3 wallet](https://metamask.io/) and a wallet private key. To ensure security, make sure to never expose your wallet private key anywhere outside your local environment. For running C2D, export your wallet private key as a local environment variable:
```
export WALLET_PRIVATE_KEY=='YOUR_PRIVATE_KEY'
```

When you're ready to run C2D, navigate to your working Jupyter notebook and in your terminal run
```
same run -t ocean
```
Note that at the end of the command, you'll have to add the options shown below. This is done by adding `--option-name=value`
### SAME-Ocean Runtime Options

* `algo-verified`: bool - specify whether algorithm was verified by the data provider for C2D
* `algo-pushed`: bool - specify whether algorithm was published to GitHub (currently required, aimed to be removed)
* `network`: str - network URL to access Ocean Market on
* `provider-address`: str - address of compute provider
* `wallet-private-key`: str - private key for paying transactions in the pipeline
* `dt-did`: str - Decentralized Identifier of the dataset (found through Ocean Market)
* `dt-pool`: str - address of the dataset liquidity pool (applicable if dataset has dynamic pricing)
* `algo-tag`: str - tag to refer to the model as
* `algo-version`: str - version number of the published model
* `algo-url`: str - GitHub URL to raw model code
* `algo-name`: str - name of model
* `author`: str - model author name
* `licence`: str - model licence
* `max-dt-price`: int - max price willing to pay for dataset (in OCEAN)


## The SAME Community

SAME is entirely open-source and non-commercial. We plan on donating it to a foundation as soon as we can identify one that matches our project's goals.

What can you do? Please join our community!

### Public web content

* [Website](https://sameproject.ml)
* [Google Group](https://groups.google.com/u/2/g/same-project)
* [Slack](https://join.slack.com/t/sameproject/shared_invite/zt-lq9rk2g6-Jyfv3AXu_qnX9LqWCmV7HA)
  
### Come join our repo

* [GitHub Organization](https://github.com/SAME-Project) / [GitHub Project](https://github.com/SAME-Project/same-project)
* Try it out (build instructions included)
* Complain about missing features
* EXPERTS ONLY: Add your own

Regardless, we are very open to taking your feedback. Thank you so much - onward!

-- The Co-founders of the SAME Project ([David Aronchick](https://twitter.com/aronchick) & [Luke Marsden](https://twitter.com/lmarsden))
