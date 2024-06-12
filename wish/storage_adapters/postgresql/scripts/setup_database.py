import argparse
import os.path

from backup_utils import run_external_tool


def run_sql(database: str | None, username: str, file: str, sql_vars: dict) -> bool:
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "../queries/system", file))
    args = ['psql',
            f'--file={filename}',
            f'--username={username}',
            '--no-password']
    if database:
        args.append(f'--dbname={database}')
    for key, value in sql_vars.items():
        args.append(f'--variable={key}={value}')
    if not run_external_tool(args):
        print(f'Failed to run sql query "{file}"!')
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Specifies the name of the database to be dumped', required=True)
    parser.add_argument('--username', help='User name to connect as.', required=True)
    parser.add_argument('--password-bot', help='Password for wishlist_bot role.', required=True)
    parser.add_argument('--password-backup', help='Password for wishlist_backup role.', required=True)
    args = parser.parse_args()

    if not run_sql(None, args.username, 'create_database.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'create_users.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'create_friends.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'create_wishes.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'index_users.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'index_wishes.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'index_friends.sql', {}):
        return -1
    if not run_sql(args.database, args.username, 'create_role_bot.sql', {'password': args.password_bot}):
        return -1
    if not run_sql(args.database, args.username, 'create_role_backup.sql', {"password": args.password_backup}):
        return -1

    return 0


if __name__ == '__main__':
    error_code = main()
    exit(error_code)
