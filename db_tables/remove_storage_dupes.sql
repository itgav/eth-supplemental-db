-- can have full duplicates and more than 1 'wallet_address' linked to a contract's 'storage_slot'
-- 	- full duplicates: remove all but 1
-- 	- non-unique 'storage_slot': remove all but 1 for each wallet, create a count of wallet's with occupying the 'storage_slot'
-- 		, then look into actual examples further and handle from there


-- count records that are duplicates based on all columns ("full dupes")
WITH duplicates AS (
	SELECT 
	ROW_NUMBER() OVER (PARTITION BY contract_address, wallet_address, storage_slot) as full_dupe
	FROM public.contract_storage
	)

-- delete full dupes from the table
DELETE FROM public.contract_storage
(SELECT contract_address, wallet_address, storage_slot FROM duplicates WHERE full_dupe > 1);

-- use vacuum to remove dead rows
VACUUM FULL public.contract_storage;



-- NEW QUERY TO SEE DUPES THAT ARE OF DIFFERING 'wallet_address'
SELECT *
FROM dupes
	(SELECT * 
	, ROW_NUMBER() OVER (PARTITION BY contract_address, storage_slot) as slot_dupe
	FROM public.contract_storage) dupes
WHERE slot_dupe > 1