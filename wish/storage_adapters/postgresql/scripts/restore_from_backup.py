import argparse
import os

from backup_utils import collect_backups_list, run_external_tool


def found_best_backup(root: str) -> str | None:
    backups_list = collect_backups_list(root)
    if len(backups_list) == 0:
        return None
    backups_list.sort(reverse=True)
    return backups_list[0]


def restore_database(backup_directory: str, database_name: str, username: str) -> bool:
    restore_db = ['pg_restore',
                  '--clean',
                  '--exit-on-error',
                  f'--jobs={os.cpu_count()}',
                  f'--dbname={database_name}',
                  f'--username={username}',
                  '--format=directory',
                  '--no-password',
                  backup_directory]
    if not run_external_tool(restore_db):
        print('pg_restore failed!')
        return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Specifies the name of the database to be dumped', required=True)
    parser.add_argument('--username', help='User name to connect as.', required=True)
    parser.add_argument('--backups-root', help='The root directory of backup history.', required=True)
    args = parser.parse_args()

    backup_directory = found_best_backup(args.backups_root)
    if backup_directory is None:
        print('Failed to found best backup!')
        return -1

    print(f'Trying to restore database from {backup_directory}...')

    if not restore_database(backup_directory, args.database, args.username):
        print('Failed to restore database!')
        return -1

    print('Database has been successfully restored!')
    return 0


if __name__ == '__main__':
    error_code = main()
    exit(error_code)
