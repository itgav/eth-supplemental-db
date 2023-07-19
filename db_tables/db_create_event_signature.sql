-- # GOAL:
-- ################################################################################################

CREATE TABLE IF NOT EXISTS public.event_signature
(
	hex_signature text NOT NULL CHECK (LENGTH(hex_signature) = 66),
	text_signature text NOT NULL,
    id_from_source integer,
    info_source text NOT NULL,
    CONSTRAINT event_signature_pkey PRIMARY KEY (hex_signature)
);