CREATE ROLE wishlist_bot WITH
    LOGIN
    PASSWORD :password;
GRANT pg_read_all_data to wishlist_bot;
GRANT pg_write_all_data to wishlist_bot;
