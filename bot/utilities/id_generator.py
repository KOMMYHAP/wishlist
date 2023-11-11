def id_generator():
    last_id = 0
    while True:
        yield last_id
        last_id += 1
