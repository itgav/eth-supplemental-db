-- # GOAL:
-- ################################################################################################

CREATE TABLE IF NOT EXISTS public.wallet_info
(
	wallet_address text NOT NULL CHECK (LENGTH(wallet_address) = 42),
	wallet_name text NOT NULL,
    protocol text NOT NULL,
    address_category text NOT NULL,
    protocol_category text NOT NULL,
    address_url text NOT NULL,
    beacon_depositor boolean NOT NULL,
    CONSTRAINT wallet_info_pkey PRIMARY KEY (wallet_address)
);