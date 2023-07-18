-- contract_storage
-- table desc: this will hold all balance storage_slots that have been linked to a specific wallet
-- columns:
	-- contract_address
	-- slot_address
	-- wallet_address

----------------------------------------------------------------------------------------------
-- Use this query to test how large columns are and optimize their order
----------------------------------------------------------------------------------------------
-- SELECT 
-- 	pg_column_size(row()) AS empty_row,
-- 	pg_column_size(row('0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT, 
-- 					   '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT,
-- 					   '0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT
-- 					  )) as normal,
-- 	pg_column_size(row('0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT, 
-- 					   '0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT,
-- 					   '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT
-- 					  )) as hash_last,
-- 	pg_column_size(row('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT)) AS tx_hash, -- 66+1
-- 	pg_column_size(row('0xa1e4380a3b1f749673e270229993ee55f35663b4'::TEXT)) AS wallet_address -- 42+1

----------------------------------------------------------------------------------------------
-- Use this query to create a mock table to then insert data into a check size
----------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.test_tx_size
(
    contract_address text NOT NULL CHECK (LENGTH(contract_address) = 42),
    wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
    storage_slot text NOT NULL CHECK (LENGTH(storage_slot) = 66)
);

----------------------------------------------------------------------------------------------
-- insert mock data into mock table to check how size compares
----------------------------------------------------------------------------------------------
INSERT INTO public.test_tx_size (
    contract_address, wallet_address, storage_slot
)
SELECT '0xa1e4380a3b1f749673e270229993ee55f35663b4', 
		'0xa1e4380a3b1f749673e270229993ee55f35663b4', 
		'0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bf5ed1be16dfba1b2206'
  FROM generate_series(1, 3000000);

----------------------------------------------------------------------------------------------
-- get size of mock table --> can use to see how size compares based on changes in column order
----------------------------------------------------------------------------------------------
SELECT pg_relation_size('test_tx_size') AS size_bytes,
       pg_size_pretty(pg_relation_size('test_tx_size')) AS size_pretty;
