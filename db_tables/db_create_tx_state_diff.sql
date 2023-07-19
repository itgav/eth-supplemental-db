-- # GOAL:
-- ################################################################################################

CREATE TABLE IF NOT EXISTS public.tx_state_diff
(
	tx_hash text NOT NULL CHECK (LENGTH(tx_hash) = 66),
	block_number int4 NOT NULL CHECK (block_number >= 0),
    wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
	token_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
    token_id text NOT NULL,
    start_value NUMERIC NOT NULL CHECK (start_value >= 0),
    end_value NUMERIC NOT NULL CHECK (end_value >= 0)
) PARTITION BY RANGE (block_number);

----------------------------------------------------------------
----------------------------------------------------------------
-- Experimented with 1k blocks in the 13M block range which has avg 190 tx per block
-- Sampled 1k blocks and have 738k rows --> 738M per 1M blocks (~4 per tx)..... oof
----------------------------------------------------------------
----------------------------------------------------------------
-- Partitions: Lvl 1
-- will use Lvl 2 partitions to get sub-partitions of ~40M rows
----------------------------------------------------------------
----------------------------------------------------------------
CREATE TABLE tx_state_diff_0 PARTITION OF tx_state_diff
	FOR VALUES FROM (0) TO (3000000); -- est. tx: 12M, rows: 48M
CREATE TABLE tx_state_diff_3000 PARTITION OF tx_state_diff
	FOR VALUES FROM (3000000) TO (4000000); -- est. tx: 14M, rows: 56M
CREATE TABLE tx_state_diff_4000 PARTITION OF tx_state_diff
	FOR VALUES FROM (4000000) TO (5000000)
	PARTITION BY HASH(block_number); -- est. tx: 65M, rows: 260M
CREATE TABLE tx_state_diff_5000 PARTITION OF tx_state_diff
	FOR VALUES FROM (5000000) TO (6000000)
	PARTITION BY HASH(block_number); -- est. tx: 100M, rows: 400M
CREATE TABLE tx_state_diff_6000 PARTITION OF tx_state_diff
	FOR VALUES FROM (6000000) TO (7000000)
	PARTITION BY HASH(block_number); -- est. tx: 110M, rows: 440M
CREATE TABLE tx_state_diff_7000 PARTITION OF tx_state_diff
	FOR VALUES FROM (7000000) TO (8000000)
	PARTITION BY HASH(block_number); -- est. tx: 100M, rows: 400M
CREATE TABLE tx_state_diff_8000 PARTITION OF tx_state_diff
	FOR VALUES FROM (8000000) TO (9000000)
	PARTITION BY HASH(block_number); -- est. tx: 100M, rows: 400M
CREATE TABLE tx_state_diff_9000 PARTITION OF tx_state_diff
	FOR VALUES FROM (9000000) TO (10000000)
	PARTITION BY HASH(block_number); -- est. tx: 105M, rows: 420M
-- start splitting up by 500k blocks
CREATE TABLE tx_state_diff_10000 PARTITION OF tx_state_diff
	FOR VALUES FROM (10000000) TO (10500000)
	PARTITION BY HASH(block_number); -- est. tx: 75M, rows: 300M
CREATE TABLE tx_state_diff_10500 PARTITION OF tx_state_diff
	FOR VALUES FROM (10500000) TO (11000000)
	PARTITION BY HASH(block_number); -- est. tx: 80M, rows: 320M
CREATE TABLE tx_state_diff_11000 PARTITION OF tx_state_diff
	FOR VALUES FROM (11000000) TO (11500000)
	PARTITION BY HASH(block_number); -- est. tx: 85M, rows: 340M
CREATE TABLE tx_state_diff_11500 PARTITION OF tx_state_diff
	FOR VALUES FROM (11500000) TO (12000000)
	PARTITION BY HASH(block_number); -- est. tx: 90M, rows: 360M
CREATE TABLE tx_state_diff_12000 PARTITION OF tx_state_diff
	FOR VALUES FROM (12000000) TO (12500000)
	PARTITION BY HASH(block_number); -- est. tx: 95M, rows: 380M
CREATE TABLE tx_state_diff_12500 PARTITION OF tx_state_diff
	FOR VALUES FROM (12500000) TO (13000000)
	PARTITION BY HASH(block_number); -- est. tx: 100M, rows: 400M
CREATE TABLE tx_state_diff_13000 PARTITION OF tx_state_diff
	FOR VALUES FROM (13000000) TO (13500000)
	PARTITION BY HASH(block_number); -- est. tx: 95M, rows: 380M
CREATE TABLE tx_state_diff_13500 PARTITION OF tx_state_diff
	FOR VALUES FROM (13500000) TO (14000000)
	PARTITION BY HASH(block_number); -- est. tx: 95M, rows: 380M
CREATE TABLE tx_state_diff_14000 PARTITION OF tx_state_diff
	FOR VALUES FROM (14000000) TO (14500000)
	PARTITION BY HASH(block_number); -- est. tx: 90M, rows: 360M
CREATE TABLE tx_state_diff_14500 PARTITION OF tx_state_diff
	FOR VALUES FROM (14500000) TO (15000000)
	PARTITION BY HASH(block_number); -- est. tx: 90M, rows: 360M
CREATE TABLE tx_state_diff_15000 PARTITION OF tx_state_diff
	FOR VALUES FROM (15000000) TO (15500000)
	PARTITION BY HASH(block_number); -- est. tx: 85M, rows: 340M
CREATE TABLE tx_state_diff_15500 PARTITION OF tx_state_diff
	FOR VALUES FROM (15500000) TO (16000000)
	PARTITION BY HASH(block_number); -- est. tx: 85M, rows: 340M
CREATE TABLE tx_state_diff_16000 PARTITION OF tx_state_diff
	FOR VALUES FROM (16000000) TO (16500000)
	PARTITION BY HASH(block_number); -- est. tx: 75M, rows: 300M
CREATE TABLE tx_state_diff_16500 PARTITION OF tx_state_diff
	FOR VALUES FROM (16500000) TO (17000000)
	PARTITION BY HASH(block_number); -- est. tx: 75M, rows: 300M
CREATE TABLE tx_state_diff_17000 PARTITION OF tx_state_diff
	FOR VALUES FROM (17000000) TO (17500000)
	PARTITION BY HASH(block_number); -- est. tx: 75M, rows: 300M
CREATE TABLE tx_state_diff_17500 PARTITION OF tx_state_diff
	FOR VALUES FROM (17500000) TO (18000000)
	PARTITION BY HASH(block_number); -- est. tx: 75M, rows: 300M
----------------------------------------------------------------
----------------------------------------------------------------
-- Partitions: Lvl 2
----------------------------------------------------------------
----------------------------------------------------------------
-- tx_state_diff_4000 -- est. tx: 65M, rows: 260M, rows/part: 52M
CREATE TABLE tx_state_diff_4000_1 PARTITION OF tx_state_diff_4000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_state_diff_4000_2 PARTITION OF tx_state_diff_4000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_state_diff_4000_3 PARTITION OF tx_state_diff_4000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_state_diff_4000_4 PARTITION OF tx_state_diff_4000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_state_diff_4000_5 PARTITION OF tx_state_diff_4000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_state_diff_5000 -- est. tx: 100M, rows: 400M, rows/part: 50
CREATE TABLE tx_state_diff_5000_1 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_5000_2 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_5000_3 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_5000_4 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_5000_5 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_5000_6 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_5000_7 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_5000_8 PARTITION OF tx_state_diff_5000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_6000 -- est. tx: 110M, rows: 440M, rows/part: 55M 
CREATE TABLE tx_state_diff_6000_1 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_6000_2 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_6000_3 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_6000_4 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_6000_5 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_6000_6 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_6000_7 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_6000_8 PARTITION OF tx_state_diff_6000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_7000 -- est. tx: 100M, rows: 400M, rows/part: 50M
CREATE TABLE tx_state_diff_7000_1 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_7000_2 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_7000_3 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_7000_4 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_7000_5 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_7000_6 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_7000_7 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_7000_8 PARTITION OF tx_state_diff_7000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_8000 -- est. tx: 100M, rows: 400M, rows/part: 50M
CREATE TABLE tx_state_diff_8000_1 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_8000_2 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_8000_3 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_8000_4 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_8000_5 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_8000_6 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_8000_7 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_8000_8 PARTITION OF tx_state_diff_8000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_9000 -- est. tx: 105M, rows: 420M, rows/part: 52M
CREATE TABLE tx_state_diff_9000_1 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_9000_2 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_9000_3 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_9000_4 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_9000_5 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_9000_6 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_9000_7 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_9000_8 PARTITION OF tx_state_diff_9000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- primary partitions start to be every 500k blocks
----------------------------------------------------------------
-- tx_state_diff_10000 -- est. tx: 75M, rows: 300M, rows/part: 43M
CREATE TABLE tx_state_diff_10000_1 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 0);
CREATE TABLE tx_state_diff_10000_2 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 1);
CREATE TABLE tx_state_diff_10000_3 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 2);
CREATE TABLE tx_state_diff_10000_4 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 3);
CREATE TABLE tx_state_diff_10000_5 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 4);
CREATE TABLE tx_state_diff_10000_6 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 5);
CREATE TABLE tx_state_diff_10000_7 PARTITION OF tx_state_diff_10000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 7, remainder 6);
----------------------------------------------------------------
-- tx_state_diff_10500 -- est. tx: 80M, rows: 320M, rows/part: 40M
CREATE TABLE tx_state_diff_10500_1 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_10500_2 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_10500_3 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_10500_4 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_10500_5 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_10500_6 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_10500_7 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_10500_8 PARTITION OF tx_state_diff_10500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_11000 -- est. tx: 85M, rows: 340M, rows/part: 42M
CREATE TABLE tx_state_diff_11000_1 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_state_diff_11000_2 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_state_diff_11000_3 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_state_diff_11000_4 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_state_diff_11000_5 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_state_diff_11000_6 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_state_diff_11000_7 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_state_diff_11000_8 PARTITION OF tx_state_diff_11000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_state_diff_11500 -- est. tx: 90M, rows: 360M, rows/part: 40M
CREATE TABLE tx_state_diff_11500_1 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_state_diff_11500_2 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_state_diff_11500_3 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_state_diff_11500_4 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_state_diff_11500_5 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_state_diff_11500_6 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_state_diff_11500_7 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_state_diff_11500_8 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_state_diff_11500_9 PARTITION OF tx_state_diff_11500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_state_diff_12000 -- est. tx: 95M, rows: 380M, rows/part: 38M 
CREATE TABLE tx_state_diff_12000_1 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_12000_2 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_12000_3 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_12000_4 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_12000_5 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_12000_6 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_12000_7 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_12000_8 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_12000_9 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_12000_10 PARTITION OF tx_state_diff_12000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_12500 -- est. tx: 100M, rows: 400M, rows/part: 40M
CREATE TABLE tx_state_diff_12500_1 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_12500_2 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_12500_3 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_12500_4 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_12500_5 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_12500_6 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_12500_7 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_12500_8 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_12500_9 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_12500_10 PARTITION OF tx_state_diff_12500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_13000 -- est. tx: 95M, rows: 380M, rows/part: 38M
CREATE TABLE tx_state_diff_13000_1 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_13000_2 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_13000_3 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_13000_4 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_13000_5 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_13000_6 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_13000_7 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_13000_8 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_13000_9 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_13000_10 PARTITION OF tx_state_diff_13000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_13500 -- est. tx: 95M, rows: 380M, rows/part: 38M
CREATE TABLE tx_state_diff_13500_1 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_13500_2 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_13500_3 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_13500_4 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_13500_5 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_13500_6 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_13500_7 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_13500_8 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_13500_9 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_13500_10 PARTITION OF tx_state_diff_13500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_14000 -- est. tx: 90M, rows: 360M, rows/part: 40M
CREATE TABLE tx_state_diff_14000_1 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_state_diff_14000_2 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_state_diff_14000_3 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_state_diff_14000_4 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_state_diff_14000_5 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_state_diff_14000_6 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_state_diff_14000_7 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_state_diff_14000_8 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_state_diff_14000_9 PARTITION OF tx_state_diff_14000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_state_diff_14500 -- est. tx: 90M, rows: 360M, rows/part: 40M
CREATE TABLE tx_state_diff_14500_1 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_state_diff_14500_2 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_state_diff_14500_3 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_state_diff_14500_4 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_state_diff_14500_5 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_state_diff_14500_6 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_state_diff_14500_7 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_state_diff_14500_8 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_state_diff_14500_9 PARTITION OF tx_state_diff_14500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_state_diff_15000 -- est. tx: 85M, rows: 340M, rows/part: 38M
CREATE TABLE tx_state_diff_15000_1 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_state_diff_15000_2 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_state_diff_15000_3 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_state_diff_15000_4 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_state_diff_15000_5 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_state_diff_15000_6 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_state_diff_15000_7 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_state_diff_15000_8 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_state_diff_15000_9 PARTITION OF tx_state_diff_15000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_state_diff_15500 -- est. tx: 85M, rows: 340M, rows/part: 37M
CREATE TABLE tx_state_diff_15500_1 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_state_diff_15500_2 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_state_diff_15500_3 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_state_diff_15500_4 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_state_diff_15500_5 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_state_diff_15500_6 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_state_diff_15500_7 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_state_diff_15500_8 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_state_diff_15500_9 PARTITION OF tx_state_diff_15500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_state_diff_16000 -- est. tx: 75M, rows: 300M, rows/part: 30M
CREATE TABLE tx_state_diff_16000_1 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_16000_2 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_16000_3 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_16000_4 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_16000_5 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_16000_6 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_16000_7 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_16000_8 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_16000_9 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_16000_10 PARTITION OF tx_state_diff_16000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_16500 -- est. tx: 75M, rows: 300M, rows/part: 30M
CREATE TABLE tx_state_diff_16500_1 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_16500_2 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_16500_3 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_16500_4 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_16500_5 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_16500_6 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_16500_7 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_16500_8 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_16500_9 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_16500_10 PARTITION OF tx_state_diff_16500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_17000 -- est. tx: 75M, rows: 300M, rows/part: 30M
CREATE TABLE tx_state_diff_17000_1 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_17000_2 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_17000_3 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_17000_4 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_17000_5 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_17000_6 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_17000_7 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_17000_8 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_17000_9 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_17000_10 PARTITION OF tx_state_diff_17000 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------
-- tx_state_diff_17500 -- est. tx: 75M, rows: 300M, rows/part: 30M
CREATE TABLE tx_state_diff_17500_1 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 0);
CREATE TABLE tx_state_diff_17500_2 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 1);
CREATE TABLE tx_state_diff_17500_3 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 2);
CREATE TABLE tx_state_diff_17500_4 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 3);
CREATE TABLE tx_state_diff_17500_5 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 4);
CREATE TABLE tx_state_diff_17500_6 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 5);
CREATE TABLE tx_state_diff_17500_7 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 6);
CREATE TABLE tx_state_diff_17500_8 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 7);
CREATE TABLE tx_state_diff_17500_9 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 8);
CREATE TABLE tx_state_diff_17500_10 PARTITION OF tx_state_diff_17500 (
	UNIQUE (tx_hash, block_number, wallet_address, token_address, token_id)) FOR VALUES WITH (modulus 10, remainder 9);
----------------------------------------------------------------

-- END;