UPDATE wishes SET
    owner_id = %(owner_id)s,
    title = %(title)s,
    hint = %(hint)s,
    cost = %(cost)s,
    reserved_by_user_id = %(reserved_by_user_id)s
WHERE wish_id = %(wish_id)s;