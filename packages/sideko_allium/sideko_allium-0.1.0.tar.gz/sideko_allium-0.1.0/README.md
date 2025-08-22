
# Allium API Python SDK

## Overview
allium (0.1.0)

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
```

## Module Documentation and Snippets

### [admin](sideko_allium/resources/admin/README.md)


### [admin.data_transformations](sideko_allium/resources/admin/data_transformations/README.md)

* [refresh](sideko_allium/resources/admin/data_transformations/README.md#refresh) - Admin refresh a workflow

### [developer](sideko_allium/resources/developer/README.md)


### [developer.bitcoin](sideko_allium/resources/developer/bitcoin/README.md)


### [developer.bitcoin.mempool](sideko_allium/resources/developer/bitcoin/mempool/README.md)


### [developer.bitcoin.mempool.inputs](sideko_allium/resources/developer/bitcoin/mempool/inputs/README.md)

* [list](sideko_allium/resources/developer/bitcoin/mempool/inputs/README.md#list) - Get Mempool Inputs

### [developer.bitcoin.mempool.outputs](sideko_allium/resources/developer/bitcoin/mempool/outputs/README.md)

* [list](sideko_allium/resources/developer/bitcoin/mempool/outputs/README.md#list) - Get Mempool Outputs

### [developer.bitcoin.mempool.transactions](sideko_allium/resources/developer/bitcoin/mempool/transactions/README.md)

* [list](sideko_allium/resources/developer/bitcoin/mempool/transactions/README.md#list) - Get Mempool Transactions

### [developer.bitcoin.ordinals](sideko_allium/resources/developer/bitcoin/ordinals/README.md)


### [developer.bitcoin.ordinals.inscription_mints](sideko_allium/resources/developer/bitcoin/ordinals/inscription_mints/README.md)

* [list](sideko_allium/resources/developer/bitcoin/ordinals/inscription_mints/README.md#list) - Get Ordinals Inscription Mints

### [developer.bitcoin.ordinals.inscription_transfers](sideko_allium/resources/developer/bitcoin/ordinals/inscription_transfers/README.md)

* [list](sideko_allium/resources/developer/bitcoin/ordinals/inscription_transfers/README.md#list) - Get Ordinals Inscription Transfers

### [developer.bitcoin.ordinals.token_transfers](sideko_allium/resources/developer/bitcoin/ordinals/token_transfers/README.md)

* [list](sideko_allium/resources/developer/bitcoin/ordinals/token_transfers/README.md#list) - Get Ordinals Token Transfers

### [developer.bitcoin.raw](sideko_allium/resources/developer/bitcoin/raw/README.md)


### [developer.bitcoin.raw.blocks](sideko_allium/resources/developer/bitcoin/raw/blocks/README.md)

* [get](sideko_allium/resources/developer/bitcoin/raw/blocks/README.md#get) - Get Block
* [list](sideko_allium/resources/developer/bitcoin/raw/blocks/README.md#list) - Get Blocks

### [developer.bitcoin.raw.inputs](sideko_allium/resources/developer/bitcoin/raw/inputs/README.md)

* [list](sideko_allium/resources/developer/bitcoin/raw/inputs/README.md#list) - Get Inputs

### [developer.bitcoin.raw.outputs](sideko_allium/resources/developer/bitcoin/raw/outputs/README.md)

* [list](sideko_allium/resources/developer/bitcoin/raw/outputs/README.md#list) - Get Outputs

### [developer.bitcoin.raw.transactions](sideko_allium/resources/developer/bitcoin/raw/transactions/README.md)

* [get](sideko_allium/resources/developer/bitcoin/raw/transactions/README.md#get) - Get Transaction
* [list](sideko_allium/resources/developer/bitcoin/raw/transactions/README.md#list) - Get Transactions

### [developer.dex](sideko_allium/resources/developer/dex/README.md)


### [developer.dex.trades](sideko_allium/resources/developer/dex/trades/README.md)

* [list](sideko_allium/resources/developer/dex/trades/README.md#list) - Get Trades

### [developer.nfts](sideko_allium/resources/developer/nfts/README.md)


### [developer.nfts.activities](sideko_allium/resources/developer/nfts/activities/README.md)

* [list_by_contact_address](sideko_allium/resources/developer/nfts/activities/README.md#list_by_contact_address) - NFT Activities by Contract Address
* [list_by_token_id](sideko_allium/resources/developer/nfts/activities/README.md#list_by_token_id) - NFT Activities by Token ID

### [developer.nfts.collections](sideko_allium/resources/developer/nfts/collections/README.md)

* [get](sideko_allium/resources/developer/nfts/collections/README.md#get) - NFT Collections

### [developer.nfts.contracts](sideko_allium/resources/developer/nfts/contracts/README.md)

* [get_by_contract_and_token_id](sideko_allium/resources/developer/nfts/contracts/README.md#get_by_contract_and_token_id) - NFT Token by Contract and Token ID
* [get_metadata](sideko_allium/resources/developer/nfts/contracts/README.md#get_metadata) - NFT Contract

### [developer.nfts.contracts.tokens](sideko_allium/resources/developer/nfts/contracts/tokens/README.md)

* [list](sideko_allium/resources/developer/nfts/contracts/tokens/README.md#list) - NFT Tokens by Contract

### [developer.nfts.listings](sideko_allium/resources/developer/nfts/listings/README.md)

* [list_by_contact_address](sideko_allium/resources/developer/nfts/listings/README.md#list_by_contact_address) - NFT Listings by Contract Address
* [list_by_token_id](sideko_allium/resources/developer/nfts/listings/README.md#list_by_token_id) - NFT Listings by Token ID

### [developer.nfts.users](sideko_allium/resources/developer/nfts/users/README.md)


### [developer.nfts.users.tokens](sideko_allium/resources/developer/nfts/users/tokens/README.md)

* [list](sideko_allium/resources/developer/nfts/users/tokens/README.md#list) - NFT Tokens by User

### [developer.prices](sideko_allium/resources/developer/prices/README.md)

* [list](sideko_allium/resources/developer/prices/README.md#list) - Get Latest Prices
* [list_at_timestamp](sideko_allium/resources/developer/prices/README.md#list_at_timestamp) - Get Prices At Timestamp

### [developer.prices.history](sideko_allium/resources/developer/prices/history/README.md)

* [list](sideko_allium/resources/developer/prices/history/README.md#list) - Token Prices History

### [developer.prices.stats](sideko_allium/resources/developer/prices/stats/README.md)

* [get](sideko_allium/resources/developer/prices/stats/README.md#get) - Token Stats

### [developer.raw](sideko_allium/resources/developer/raw/README.md)


### [developer.raw.blocks](sideko_allium/resources/developer/raw/blocks/README.md)

* [get](sideko_allium/resources/developer/raw/blocks/README.md#get) - Get Block
* [list](sideko_allium/resources/developer/raw/blocks/README.md#list) - Get Blocks

### [developer.raw.erc1155_tokens](sideko_allium/resources/developer/raw/erc1155_tokens/README.md)

* [get](sideko_allium/resources/developer/raw/erc1155_tokens/README.md#get) - Get Erc1155 Token
* [list](sideko_allium/resources/developer/raw/erc1155_tokens/README.md#list) - Get Erc1155 Tokens

### [developer.raw.erc20_tokens](sideko_allium/resources/developer/raw/erc20_tokens/README.md)

* [get](sideko_allium/resources/developer/raw/erc20_tokens/README.md#get) - Get Erc20 Token
* [list](sideko_allium/resources/developer/raw/erc20_tokens/README.md#list) - Get Erc20 Tokens

### [developer.raw.erc721_tokens](sideko_allium/resources/developer/raw/erc721_tokens/README.md)

* [get](sideko_allium/resources/developer/raw/erc721_tokens/README.md#get) - Get Erc721 Token
* [list](sideko_allium/resources/developer/raw/erc721_tokens/README.md#list) - Get Erc721 Tokens

### [developer.raw.transactions](sideko_allium/resources/developer/raw/transactions/README.md)

* [get](sideko_allium/resources/developer/raw/transactions/README.md#get) - Get Transaction
* [list](sideko_allium/resources/developer/raw/transactions/README.md#list) - Get Transactions

### [developer.solana](sideko_allium/resources/developer/solana/README.md)


### [developer.solana.raw](sideko_allium/resources/developer/solana/raw/README.md)


### [developer.solana.raw.blocks](sideko_allium/resources/developer/solana/raw/blocks/README.md)

* [get](sideko_allium/resources/developer/solana/raw/blocks/README.md#get) - Get Block
* [list](sideko_allium/resources/developer/solana/raw/blocks/README.md#list) - Get Blocks

### [developer.solana.raw.inner_instructions](sideko_allium/resources/developer/solana/raw/inner_instructions/README.md)

* [get](sideko_allium/resources/developer/solana/raw/inner_instructions/README.md#get) - Get Inner Instructions

### [developer.solana.raw.instructions](sideko_allium/resources/developer/solana/raw/instructions/README.md)

* [get](sideko_allium/resources/developer/solana/raw/instructions/README.md#get) - Get Instructions

### [developer.solana.raw.transaction_and_instructions](sideko_allium/resources/developer/solana/raw/transaction_and_instructions/README.md)

* [get](sideko_allium/resources/developer/solana/raw/transaction_and_instructions/README.md#get) - Get Transaction And Instructions

### [developer.solana.raw.transactions](sideko_allium/resources/developer/solana/raw/transactions/README.md)

* [get](sideko_allium/resources/developer/solana/raw/transactions/README.md#get) - Get Transactions

### [developer.sql](sideko_allium/resources/developer/sql/README.md)

* [query](sideko_allium/resources/developer/sql/README.md#query) - Raw Sql Query

### [developer.state_prices](sideko_allium/resources/developer/state_prices/README.md)


### [developer.state_prices.historical](sideko_allium/resources/developer/state_prices/historical/README.md)

* [list](sideko_allium/resources/developer/state_prices/historical/README.md#list) - Get State Prices

### [developer.tokens](sideko_allium/resources/developer/tokens/README.md)

* [list](sideko_allium/resources/developer/tokens/README.md#list) - Get Tokens

### [developer.trading](sideko_allium/resources/developer/trading/README.md)


### [developer.trading.hyperliquid](sideko_allium/resources/developer/trading/hyperliquid/README.md)


### [developer.trading.hyperliquid.info](sideko_allium/resources/developer/trading/hyperliquid/info/README.md)

* [get](sideko_allium/resources/developer/trading/hyperliquid/info/README.md#get) - Get Info

### [developer.trading.hyperliquid.orderbook](sideko_allium/resources/developer/trading/hyperliquid/orderbook/README.md)


### [developer.trading.hyperliquid.orderbook.snapshot](sideko_allium/resources/developer/trading/hyperliquid/orderbook/snapshot/README.md)

* [list](sideko_allium/resources/developer/trading/hyperliquid/orderbook/snapshot/README.md#list) - Orderbook Snapshot

### [developer.wallet](sideko_allium/resources/developer/wallet/README.md)


### [developer.wallet.balances](sideko_allium/resources/developer/wallet/balances/README.md)

* [get](sideko_allium/resources/developer/wallet/balances/README.md#get) - Latest Fungible Token Balances

### [developer.wallet.balances.history](sideko_allium/resources/developer/wallet/balances/history/README.md)

* [get](sideko_allium/resources/developer/wallet/balances/history/README.md#get) - Historical Fungible Token Balances

### [developer.wallet.holdings](sideko_allium/resources/developer/wallet/holdings/README.md)


### [developer.wallet.holdings.history](sideko_allium/resources/developer/wallet/holdings/history/README.md)

* [get](sideko_allium/resources/developer/wallet/holdings/history/README.md#get) - Get Holdings History

### [developer.wallet.latest_nft_balances](sideko_allium/resources/developer/wallet/latest_nft_balances/README.md)

* [get](sideko_allium/resources/developer/wallet/latest_nft_balances/README.md#get) - Latest NFT Balances

### [developer.wallet.latest_solana_nft_balances](sideko_allium/resources/developer/wallet/latest_solana_nft_balances/README.md)

* [get](sideko_allium/resources/developer/wallet/latest_solana_nft_balances/README.md#get) - Latest Solana NFT Balances

### [developer.wallet.nft_collections](sideko_allium/resources/developer/wallet/nft_collections/README.md)

* [get](sideko_allium/resources/developer/wallet/nft_collections/README.md#get) - NFT Collections owned by wallet

### [developer.wallet.pnl](sideko_allium/resources/developer/wallet/pnl/README.md)

* [get](sideko_allium/resources/developer/wallet/pnl/README.md#get) - Get Pnl

### [developer.wallet.pnl.history](sideko_allium/resources/developer/wallet/pnl/history/README.md)

* [get](sideko_allium/resources/developer/wallet/pnl/history/README.md#get) - Get Pnl History

### [developer.wallet.pnl_by_token](sideko_allium/resources/developer/wallet/pnl_by_token/README.md)

* [get](sideko_allium/resources/developer/wallet/pnl_by_token/README.md#get) - Get Pnl By Token

### [developer.wallet.pnl_by_token.history](sideko_allium/resources/developer/wallet/pnl_by_token/history/README.md)

* [get](sideko_allium/resources/developer/wallet/pnl_by_token/history/README.md#get) - Get Pnl By Token With Historical Breakdown

### [developer.wallet.transactions](sideko_allium/resources/developer/wallet/transactions/README.md)

* [get](sideko_allium/resources/developer/wallet/transactions/README.md#get) - Transactions

### [explorer](sideko_allium/resources/explorer/README.md)


### [explorer.data_management](sideko_allium/resources/explorer/data_management/README.md)


### [explorer.data_management.ingest_jobs](sideko_allium/resources/explorer/data_management/ingest_jobs/README.md)

* [get](sideko_allium/resources/explorer/data_management/ingest_jobs/README.md#get) - Get Ingest Job
* [list](sideko_allium/resources/explorer/data_management/ingest_jobs/README.md#list) - Get Ingest Jobs

### [explorer.data_management.ingest_jobs.status](sideko_allium/resources/explorer/data_management/ingest_jobs/status/README.md)

* [list](sideko_allium/resources/explorer/data_management/ingest_jobs/status/README.md#list) - Ingest Job Status

### [explorer.data_management.tables](sideko_allium/resources/explorer/data_management/tables/README.md)

* [insert](sideko_allium/resources/explorer/data_management/tables/README.md#insert) - Insert data into Explorer table

### [explorer.metadata](sideko_allium/resources/explorer/metadata/README.md)


### [explorer.metadata.tables](sideko_allium/resources/explorer/metadata/tables/README.md)

* [get](sideko_allium/resources/explorer/metadata/tables/README.md#get) - Get Table Metadata By Id
* [list](sideko_allium/resources/explorer/metadata/tables/README.md#list) - Get Table Metadata

### [explorer.queries](sideko_allium/resources/explorer/queries/README.md)

* [run](sideko_allium/resources/explorer/queries/README.md#run) - Execute Query
* [run_async](sideko_allium/resources/explorer/queries/README.md#run_async) - Execute Query Async

### [explorer.query_runs](sideko_allium/resources/explorer/query_runs/README.md)

* [cancel](sideko_allium/resources/explorer/query_runs/README.md#cancel) - Cancel Query Run
* [get](sideko_allium/resources/explorer/query_runs/README.md#get) - Get Query Run Handler
* [list](sideko_allium/resources/explorer/query_runs/README.md#list) - Get Latest Query Run Handler

### [explorer.query_runs.error](sideko_allium/resources/explorer/query_runs/error/README.md)

* [get](sideko_allium/resources/explorer/query_runs/error/README.md#get) - Get Query Run Error

### [explorer.query_runs.results](sideko_allium/resources/explorer/query_runs/results/README.md)

* [get](sideko_allium/resources/explorer/query_runs/results/README.md#get) - Get Query Run Results With Ssa
* [list](sideko_allium/resources/explorer/query_runs/results/README.md#list) - Get Query Run Results

### [explorer.query_runs.status](sideko_allium/resources/explorer/query_runs/status/README.md)

* [get](sideko_allium/resources/explorer/query_runs/status/README.md#get) - Get Query Run Status

### [explorer.workflows](sideko_allium/resources/explorer/workflows/README.md)

* [run](sideko_allium/resources/explorer/workflows/README.md#run) - Run Workflow

### [streams](sideko_allium/resources/streams/README.md)


### [streams.data_management](sideko_allium/resources/streams/data_management/README.md)


### [streams.data_management.filter_data_sources](sideko_allium/resources/streams/data_management/filter_data_sources/README.md)

* [create](sideko_allium/resources/streams/data_management/filter_data_sources/README.md#create) - Filter Data Source
* [delete](sideko_allium/resources/streams/data_management/filter_data_sources/README.md#delete) - Delete a filter data source
* [get](sideko_allium/resources/streams/data_management/filter_data_sources/README.md#get) - Filter Data Source by ID
* [list](sideko_allium/resources/streams/data_management/filter_data_sources/README.md#list) - Filter Data Sources
* [update_values](sideko_allium/resources/streams/data_management/filter_data_sources/README.md#update_values) - Filter Data Source Values

### [streams.data_management.filters](sideko_allium/resources/streams/data_management/filters/README.md)

* [create](sideko_allium/resources/streams/data_management/filters/README.md#create) - Filter
* [delete](sideko_allium/resources/streams/data_management/filters/README.md#delete) - Delete a filter
* [get](sideko_allium/resources/streams/data_management/filters/README.md#get) - Filter by ID
* [list](sideko_allium/resources/streams/data_management/filters/README.md#list) - Filters
* [update](sideko_allium/resources/streams/data_management/filters/README.md#update) - Update a filter

### [streams.data_management.workflows](sideko_allium/resources/streams/data_management/workflows/README.md)

* [create](sideko_allium/resources/streams/data_management/workflows/README.md#create) - Workflow
* [delete](sideko_allium/resources/streams/data_management/workflows/README.md#delete) - Delete a workflow
* [get](sideko_allium/resources/streams/data_management/workflows/README.md#get) - Workflow by ID
* [list](sideko_allium/resources/streams/data_management/workflows/README.md#list) - Workflows
* [update](sideko_allium/resources/streams/data_management/workflows/README.md#update) - Update a workflow

### [supported_chains](sideko_allium/resources/supported_chains/README.md)


### [supported_chains.realtime_apis](sideko_allium/resources/supported_chains/realtime_apis/README.md)

* [get_chains](sideko_allium/resources/supported_chains/realtime_apis/README.md#get_chains) - Get Supported Chains
* [get_endpoints](sideko_allium/resources/supported_chains/realtime_apis/README.md#get_endpoints) - Get Supported Endpoints

<!-- MODULE DOCS END -->
