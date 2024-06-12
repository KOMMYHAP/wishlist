CREATE ROLE wishlist_backup WITH
    LOGIN
    PASSWORD :password;
GRANT pg_read_all_data to wishlist_backup;
