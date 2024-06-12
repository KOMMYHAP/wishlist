CREATE TABLE users (
	user_id bigint PRIMARY KEY,
	user_name text,
	first_name text,
	last_name text,
	chat_id bigint,
	wishlist_update_time timestamp,
	user_version integer
)