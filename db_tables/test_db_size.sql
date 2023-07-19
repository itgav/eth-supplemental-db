-- # GOAL:
-- ################################################################################################

-- tx_state_diff
-- table desc: this will hold all the addresses and their resulting statediff from each tx
	-- many:1 relationship between # rows and tx_hash
-- columns:
	-- tx_hash (length = 66)
	-- wallet_address (length = 42)
	-- slot_address (length = 66)
	-- start value (NUMERIC(0,40))
	-- end value (NUMERIC(0,40))

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
-- 	pg_column_size(row('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT, 
-- 					   '0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT,
-- 					   '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT, 
-- 					   389898800000088::NUMERIC(40,0), 
-- 					   389898800000088::NUMERIC(40,0)
-- 					  )) as normal,
-- 	pg_column_size(row('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT, 
-- 					   '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT,
-- 					   '0x5df9b87991262f6ba471f09758cde1c0fc1de734'::TEXT, 
-- 					   389898800000000088::NUMERIC(40,0), 
-- 					   389898800000000088::NUMERIC(40,0)
-- 					  )) as hash_first,
-- 	pg_column_size(row('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT)) AS tx_hash, -- 66+1
-- 	pg_column_size(row('0xa1e4380a3b1f749673e270229993ee55f35663b4'::TEXT)) AS wallet_address, -- 42+1
--     pg_column_size(row('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'::TEXT)) AS storage_slot, -- 66+1
--     pg_column_size(row(389898800000000088::NUMERIC(40,0))) AS eth_start_value, -- (0-4digits: 5, 5-8:7, 9-12:9)
-- 	pg_column_size(row(389898800000000088::NUMERIC(40,0))) AS eth_end_value -- (0-4digits: 5, 5-8:7, 9-12:9)

----------------------------------------------------------------------------------------------
-- Use this query to create a mock table to then insert data into a check size
----------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.test_tx_size
(
    tx_hash text NOT NULL CHECK (LENGTH(tx_hash) = 66),
    wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
    storage_slot text NOT NULL CHECK (LENGTH(storage_slot) = 66),
    start_value NUMERIC(40, 0) NOT NULL CHECK (start_value >= 0),
    end_value NUMERIC(40, 0) NOT NULL CHECK (end_value >= 0)
);

----------------------------------------------------------------------------------------------
-- insert mock data into mock table to check how size compares
----------------------------------------------------------------------------------------------
INSERT INTO public.test_tx_size (
    tx_hash, wallet_address, storage_slot, start_value, end_value
)
SELECT '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060', 
		'0xa1e4380a3b1f749673e270229993ee55f35663b4', 
		'0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060',
		389898800000088,
		389898800000088
  FROM generate_series(1, 3000000);

----------------------------------------------------------------------------------------------
-- get size of mock table --> can use to see how size compares based on changes in column order
----------------------------------------------------------------------------------------------
SELECT pg_relation_size('test_tx_size') AS size_bytes,
       pg_size_pretty(pg_relation_size('test_tx_size')) AS size_pretty;
