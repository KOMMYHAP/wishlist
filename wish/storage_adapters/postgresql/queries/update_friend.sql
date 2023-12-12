UPDATE friends SET
	requested_counter = %(requested_counter)s,
	access_time = %(access_time)s,
	wishlist_seen_time = %(wishlist_seen_time)s
WHERE user_id = %(user_id)s AND friend_id = %(friend_id)s;