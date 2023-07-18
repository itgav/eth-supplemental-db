CREATE TABLE IF NOT EXISTS public.tester
(
	contract_address text NOT NULL CHECK (LENGTH(contract_address) = 42),
	token_id text NOT NULL,
    wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
    storage_slot text NOT NULL CHECK (LENGTH(storage_slot) = 66)
) PARTITION BY HASH (wallet_address);


CREATE TABLE tester_0 PARTITION OF tester
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 2, REMAINDER 0);
CREATE TABLE tester_1 PARTITION OF tester
-- 	(UNIQUE (contract_address, token_id, wallet_address, storage_slot))
	FOR VALUES WITH (MODULUS 2, REMAINDER 1);
