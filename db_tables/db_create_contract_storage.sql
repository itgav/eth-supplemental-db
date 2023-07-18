-- I'm anticipating tx_state_diff to have ~7B rows in total, so going to assume ~1B rows for this table (7x per address)

CREATE TABLE IF NOT EXISTS public.contract_storage
(
	contract_address text NOT NULL CHECK (LENGTH(contract_address) = 42),
	token_id text NOT NULL,
    wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
    storage_slot text NOT NULL CHECK (LENGTH(storage_slot) = 66)
) PARTITION BY HASH (wallet_address);

----------------------------------------------------------------
----------------------------------------------------------------
-- Partitions:
-- anticipating ~1B rows, so will use a modulus of 50 to get us to 20M rows per partition
----------------------------------------------------------------
----------------------------------------------------------------
CREATE TABLE contract_storage_0 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 0);
CREATE TABLE contract_storage_1 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 1);
CREATE TABLE contract_storage_2 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 2);
CREATE TABLE contract_storage_3 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 3);
CREATE TABLE contract_storage_4 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 4);
CREATE TABLE contract_storage_5 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 5);
CREATE TABLE contract_storage_6 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 6);
CREATE TABLE contract_storage_7 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 7);
CREATE TABLE contract_storage_8 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 8);
CREATE TABLE contract_storage_9 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 9);
----------------------------------------------------------------
CREATE TABLE contract_storage_10 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 10);
CREATE TABLE contract_storage_11 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 11);
CREATE TABLE contract_storage_12 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 12);
CREATE TABLE contract_storage_13 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 13);
CREATE TABLE contract_storage_14 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 14);
CREATE TABLE contract_storage_15 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 15);
CREATE TABLE contract_storage_16 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 16);
CREATE TABLE contract_storage_17 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 17);
CREATE TABLE contract_storage_18 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 18);
CREATE TABLE contract_storage_19 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 19);
----------------------------------------------------------------
CREATE TABLE contract_storage_20 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 20);
CREATE TABLE contract_storage_21 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 21);
CREATE TABLE contract_storage_22 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 22);
CREATE TABLE contract_storage_23 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 23);
CREATE TABLE contract_storage_24 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 24);
CREATE TABLE contract_storage_25 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 25);
CREATE TABLE contract_storage_26 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 26);
CREATE TABLE contract_storage_27 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 27);
CREATE TABLE contract_storage_28 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 28);
CREATE TABLE contract_storage_29 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 29);
----------------------------------------------------------------
CREATE TABLE contract_storage_30 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 30);
CREATE TABLE contract_storage_31 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 31);
CREATE TABLE contract_storage_32 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 32);
CREATE TABLE contract_storage_33 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 33);
CREATE TABLE contract_storage_34 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 34);
CREATE TABLE contract_storage_35 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 35);
CREATE TABLE contract_storage_36 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 36);
CREATE TABLE contract_storage_37 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 37);
CREATE TABLE contract_storage_38 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 38);
CREATE TABLE contract_storage_39 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 39);
----------------------------------------------------------------
CREATE TABLE contract_storage_40 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 40);
CREATE TABLE contract_storage_41 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 41);
CREATE TABLE contract_storage_42 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 42);
CREATE TABLE contract_storage_43 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 43);
CREATE TABLE contract_storage_44 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 44);
CREATE TABLE contract_storage_45 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 45);
CREATE TABLE contract_storage_46 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 46);
CREATE TABLE contract_storage_47 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 47);
CREATE TABLE contract_storage_48 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 48);
CREATE TABLE contract_storage_49 PARTITION OF contract_storage
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 50, REMAINDER 49);
----------------------------------------------------------------
