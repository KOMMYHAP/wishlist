CREATE TABLE wishes (
	wish_id serial,
	owner_id bigint REFERENCES users(user_id),
	title text,
	hint text,
	cost text,
	reserved_by_user_id bigint REFERENCES users(user_id)
)