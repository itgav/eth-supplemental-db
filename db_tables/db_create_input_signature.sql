CREATE TABLE IF NOT EXISTS public.input_signature
(
	hex_signature text NOT NULL CHECK (LENGTH(hex_signature) = 10),
	text_signature text NOT NULL,
    id_from_source integer,
    info_source text NOT NULL,
    CONSTRAINT input_signature_pkey PRIMARY KEY (hex_signature)
);