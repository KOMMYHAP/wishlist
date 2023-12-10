CREATE TABLE friends (
	user_id bigint REFERENCES users(user_id),
	friend_id bigint REFERENCES users(user_id),
	request_counter integer,
	wishlist_seen_time timestamp,
	PRIMARY KEY (user_id, friend_id)
)