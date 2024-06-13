import argparse
import datetime
import os
import shutil
import tempfile

from backup_utils import collect_backups_list, run_external_tool


def make_backup(database_name: str, username: str, output_directory: str) -> bool:
    args = ['pg_dump',
            f'--dbname={database_name}',
            f'--jobs={os.cpu_count()}',
            f'--file={os.path.abspath(output_directory)}',
            f'--username={username}',
            '--format=directory',
            '--no-password']

    if not run_external_tool(args):
        print('Failed to make dump!')
        return False
    return True


def remove_outdated_backups(root: str, limit: int) -> bool:
    if limit < 1:
        print(f'Limit count of backups must be >= 1, but got {limit}')
        return False

    backups_list = collect_backups_list(root)
    backups_list.sort(reverse=True)

    outdated_backups = backups_list[limit - 1:]
    for path in outdated_backups:
        try:
            shutil.rmtree(path, ignore_errors=False)
        except OSError as e:
            print(e)
            return False

    return True


def make_datetime_now_str() -> str:
    now = datetime.datetime.now(datetime.UTC)
    return now.strftime('%Y_%m_%d_%H_%M_%S')


def move_new_backup(backup_directory: str, root: str) -> bool:
    datetime.datetime.now(datetime.UTC)
    if not os.path.isdir(backup_directory):
        print(f'Specified path of backup directory is not a directory: "{backup_directory}"!')
        return False

    backup_filename = f'backup_{make_datetime_now_str()}'
    new_directory = os.path.join(root, backup_filename)

    try:
        shutil.move(backup_directory, new_directory)
        return True
    except OSError as e:
        print(e)
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Specifies the name of the database to be dumped', required=True)
    parser.add_argument('--username', help='User name to connect as.', required=True)
    parser.add_argument('--output', help='The root directory for backup history.', required=True)
    parser.add_argument('--history-length', help='Specifies the count of backups to be stored.', required=True,
                        type=int)
    args = parser.parse_args()

    if args.history_length < 1:
        print(f'History must be >= 1, but got {args.history_length}!')
        return -1

    temp_output = tempfile.mkdtemp(prefix='wishlist_temp_backup_', suffix=f'_{make_datetime_now_str()}')
    print(f'Temp backup directory is "{temp_output}"')

    backup_completed = make_backup(args.database, args.username, temp_output)
    if not backup_completed:
        print('Failed to complete backup!')
        return -1

    if not remove_outdated_backups(args.output, args.history_length):
        print('Failed to remove outdated backups!')
        return -1

    if not move_new_backup(temp_output, args.output):
        print('Failed to move backup from temp to new directory!')
        return -1

    return 0


if __name__ == '__main__':
    error_code = main()
    exit(error_code)
