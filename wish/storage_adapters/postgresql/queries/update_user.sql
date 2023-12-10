UPDATE users SET
	user_name = %(user_name)s,
	first_name = %(first_name)s,
	last_name = %(last_name)s,
	chat_id = %(chat_id)s,
	wishlist_update_time = %(wishlist_update_time)s,
	user_version = %(user_version)s
WHERE user_id = %(user_id)s;