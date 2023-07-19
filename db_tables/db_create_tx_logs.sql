-- # GOAL:
-- ################################################################################################

CREATE TABLE IF NOT EXISTS public.tx_logs
(
    tx_hash text NOT NULL CHECK (LENGTH(tx_hash) = 66),
    block_number int4 NOT NULL CHECK (block_number >= 0),
    emit_address text NOT NULL CHECK (LENGTH(emit_address) = 42),
    log_topic_1 text NOT NULL CHECK (log_topic_1 = '0x' OR LENGTH(log_topic_1) = 66),
	log_topic_2 text NOT NULL CHECK (log_topic_2 = '0x' OR LENGTH(log_topic_2) = 66),
	log_topic_3 text NOT NULL CHECK (log_topic_3 = '0x' OR LENGTH(log_topic_3) = 66),
	log_topic_4 text NOT NULL CHECK (log_topic_4 = '0x' OR LENGTH(log_topic_4) = 66),
    log_data text NOT NULL
) PARTITION BY RANGE (block_number);

----------------------------------------------------------------
----------------------------------------------------------------
-- Partitions: Lvl 1
-- will use Lvl 2 partitions to get sub-partitions of ~20M rows
----------------------------------------------------------------
----------------------------------------------------------------
CREATE TABLE tx_logs_0 PARTITION OF tx_logs
	FOR VALUES FROM (0) TO (3000000); -- est. rows: 12M
CREATE TABLE tx_logs_3000 PARTITION OF tx_logs
	FOR VALUES FROM (3000000) TO (4000000); -- est. rows: 14M
CREATE TABLE tx_logs_4000 PARTITION OF tx_logs
	FOR VALUES FROM (4000000) TO (5000000)
	PARTITION BY HASH(block_number); -- est. rows: 65M
CREATE TABLE tx_logs_5000 PARTITION OF tx_logs
	FOR VALUES FROM (5000000) TO (6000000)
	PARTITION BY HASH(block_number); -- est. rows: 100M
CREATE TABLE tx_logs_6000 PARTITION OF tx_logs
	FOR VALUES FROM (6000000) TO (7000000)
	PARTITION BY HASH(block_number); -- est. rows: 110M
CREATE TABLE tx_logs_7000 PARTITION OF tx_logs
	FOR VALUES FROM (7000000) TO (8000000)
	PARTITION BY HASH(block_number); -- est. rows: 100M
CREATE TABLE tx_logs_8000 PARTITION OF tx_logs
	FOR VALUES FROM (8000000) TO (9000000)
	PARTITION BY HASH(block_number); -- est. rows: 100M
CREATE TABLE tx_logs_9000 PARTITION OF tx_logs
	FOR VALUES FROM (9000000) TO (10000000)
	PARTITION BY HASH(block_number); -- est. rows: 105M
CREATE TABLE tx_logs_10000 PARTITION OF tx_logs
	FOR VALUES FROM (10000000) TO (11000000)
	PARTITION BY HASH(block_number); -- est. rows: 155M
CREATE TABLE tx_logs_11000 PARTITION OF tx_logs
	FOR VALUES FROM (11000000) TO (12000000)
	PARTITION BY HASH(block_number); -- est. rows: 175M
CREATE TABLE tx_logs_12000 PARTITION OF tx_logs
	FOR VALUES FROM (12000000) TO (13000000)
	PARTITION BY HASH(block_number); -- est. rows: 195M
CREATE TABLE tx_logs_13000 PARTITION OF tx_logs
	FOR VALUES FROM (13000000) TO (14000000)
	PARTITION BY HASH(block_number); -- est. rows: 190M
CREATE TABLE tx_logs_14000 PARTITION OF tx_logs
	FOR VALUES FROM (14000000) TO (15000000)
	PARTITION BY HASH(block_number); -- est. rows: 180M
CREATE TABLE tx_logs_15000 PARTITION OF tx_logs
	FOR VALUES FROM (15000000) TO (16000000)
	PARTITION BY HASH(block_number); -- est. rows: 170M
CREATE TABLE tx_logs_16000 PARTITION OF tx_logs
	FOR VALUES FROM (16000000) TO (17000000)
	PARTITION BY HASH(block_number); -- est. rows: 150M
CREATE TABLE tx_logs_17000 PARTITION OF tx_logs
	FOR VALUES FROM (17000000) TO (18000000)
	PARTITION BY HASH(block_number); -- est. rows: 150M
----------------------------------------------------------------
----------------------------------------------------------------
-- Partitions: Lvl 2
----------------------------------------------------------------
----------------------------------------------------------------
-- tx_logs_4000 -- est. rows: 65M, rows/part: 22M
CREATE TABLE tx_logs_4000_1 PARTITION OF tx_logs_4000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 3, remainder 0);
CREATE TABLE tx_logs_4000_2 PARTITION OF tx_logs_4000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 3, remainder 1);
CREATE TABLE tx_logs_4000_3 PARTITION OF tx_logs_4000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 3, remainder 2);
----------------------------------------------------------------
-- tx_logs_5000 -- est. rows: 100M, rows/part: 20M
CREATE TABLE tx_logs_5000_1 PARTITION OF tx_logs_5000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_logs_5000_2 PARTITION OF tx_logs_5000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_logs_5000_3 PARTITION OF tx_logs_5000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_logs_5000_4 PARTITION OF tx_logs_5000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_logs_5000_5 PARTITION OF tx_logs_5000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_logs_6000 -- est. rows: 110M, rows/part: 22M
CREATE TABLE tx_logs_6000_1 PARTITION OF tx_logs_6000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_logs_6000_2 PARTITION OF tx_logs_6000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_logs_6000_3 PARTITION OF tx_logs_6000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_logs_6000_4 PARTITION OF tx_logs_6000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_logs_6000_5 PARTITION OF tx_logs_6000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_logs_7000 -- est. rows: 100M, rows/part: 20M
CREATE TABLE tx_logs_7000_1 PARTITION OF tx_logs_7000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_logs_7000_2 PARTITION OF tx_logs_7000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_logs_7000_3 PARTITION OF tx_logs_7000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_logs_7000_4 PARTITION OF tx_logs_7000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_logs_7000_5 PARTITION OF tx_logs_7000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_logs_8000 -- est. rows: 100M, rows/part: 20M
CREATE TABLE tx_logs_8000_1 PARTITION OF tx_logs_8000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_logs_8000_2 PARTITION OF tx_logs_8000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_logs_8000_3 PARTITION OF tx_logs_8000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_logs_8000_4 PARTITION OF tx_logs_8000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_logs_8000_5 PARTITION OF tx_logs_8000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_logs_9000 -- est. rows: 105M, rows/part: 21M
CREATE TABLE tx_logs_9000_1 PARTITION OF tx_logs_9000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 0);
CREATE TABLE tx_logs_9000_2 PARTITION OF tx_logs_9000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 1);
CREATE TABLE tx_logs_9000_3 PARTITION OF tx_logs_9000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 2);
CREATE TABLE tx_logs_9000_4 PARTITION OF tx_logs_9000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 3);
CREATE TABLE tx_logs_9000_5 PARTITION OF tx_logs_9000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 5, remainder 4);
----------------------------------------------------------------
-- tx_logs_10000 -- est. rows: 155M, rows/part: 22M
CREATE TABLE tx_logs_10000_1 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 0);
CREATE TABLE tx_logs_10000_2 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 1);
CREATE TABLE tx_logs_10000_3 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 2);
CREATE TABLE tx_logs_10000_4 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 3);
CREATE TABLE tx_logs_10000_5 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 4);
CREATE TABLE tx_logs_10000_6 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 5);
CREATE TABLE tx_logs_10000_7 PARTITION OF tx_logs_10000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 6);
----------------------------------------------------------------
-- tx_logs_11000 -- est. rows: 175M, rows/part: 22M
CREATE TABLE tx_logs_11000_1 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_logs_11000_2 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_logs_11000_3 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_logs_11000_4 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_logs_11000_5 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_logs_11000_6 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_logs_11000_7 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_logs_11000_8 PARTITION OF tx_logs_11000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_logs_12000 -- est. rows: 195M, rows/part: 22M
CREATE TABLE tx_logs_12000_1 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_logs_12000_2 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_logs_12000_3 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_logs_12000_4 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_logs_12000_5 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_logs_12000_6 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_logs_12000_7 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_logs_12000_8 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_logs_12000_9 PARTITION OF tx_logs_12000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_logs_13000 -- est. rows: 190M, rows/part: 22M
CREATE TABLE tx_logs_13000_1 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_logs_13000_2 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_logs_13000_3 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_logs_13000_4 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_logs_13000_5 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_logs_13000_6 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_logs_13000_7 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_logs_13000_8 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_logs_13000_9 PARTITION OF tx_logs_13000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_logs_14000 -- est. rows: 180M, rows/part: 20M
CREATE TABLE tx_logs_14000_1 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 0);
CREATE TABLE tx_logs_14000_2 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 1);
CREATE TABLE tx_logs_14000_3 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 2);
CREATE TABLE tx_logs_14000_4 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 3);
CREATE TABLE tx_logs_14000_5 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 4);
CREATE TABLE tx_logs_14000_6 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 5);
CREATE TABLE tx_logs_14000_7 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 6);
CREATE TABLE tx_logs_14000_8 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 7);
CREATE TABLE tx_logs_14000_9 PARTITION OF tx_logs_14000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 9, remainder 8);
----------------------------------------------------------------
-- tx_logs_15000 -- est. rows: 170M, rows/part: 22M
CREATE TABLE tx_logs_15000_1 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 0);
CREATE TABLE tx_logs_15000_2 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 1);
CREATE TABLE tx_logs_15000_3 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 2);
CREATE TABLE tx_logs_15000_4 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 3);
CREATE TABLE tx_logs_15000_5 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 4);
CREATE TABLE tx_logs_15000_6 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 5);
CREATE TABLE tx_logs_15000_7 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 6);
CREATE TABLE tx_logs_15000_8 PARTITION OF tx_logs_15000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 8, remainder 7);
----------------------------------------------------------------
-- tx_logs_16000 -- est. rows: 150M, rows/part: 22M
CREATE TABLE tx_logs_16000_1 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 0);
CREATE TABLE tx_logs_16000_2 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 1);
CREATE TABLE tx_logs_16000_3 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 2);
CREATE TABLE tx_logs_16000_4 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 3);
CREATE TABLE tx_logs_16000_5 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 4);
CREATE TABLE tx_logs_16000_6 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 5);
CREATE TABLE tx_logs_16000_7 PARTITION OF tx_logs_16000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 6);
----------------------------------------------------------------
-- tx_logs_17000 -- est. rows: 150M, rows/part: 22M
CREATE TABLE tx_logs_17000_1 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 0);
CREATE TABLE tx_logs_17000_2 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 1);
CREATE TABLE tx_logs_17000_3 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 2);
CREATE TABLE tx_logs_17000_4 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 3);
CREATE TABLE tx_logs_17000_5 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 4);
CREATE TABLE tx_logs_17000_6 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 5);
CREATE TABLE tx_logs_17000_7 PARTITION OF tx_logs_17000 (
	PRIMARY KEY (tx_hash)) FOR VALUES WITH (modulus 7, remainder 6);
----------------------------------------------------------------

-- END;