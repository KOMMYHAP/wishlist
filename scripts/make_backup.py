import argparse
import datetime
import os
import shutil
import subprocess
import tempfile


def make_backup(database_name: str, username: str, output_directory: str) -> bool:
    port = 5432
    jobs = os.cpu_count()

    args = ['pg_dump',
            f'--dbname={database_name}',
            f'--port={port}',
            f'--jobs={jobs}',
            f'--file={os.path.abspath(output_directory)}',
            f'--username={username}',
            '--format=directory',
            '--no-password']

    try:
        subprocess.run(args, capture_output=True, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(e)
        return False

    return True


def remove_outdated_backups(root: str, limit: int) -> bool:
    if limit <= 1:
        print(f'Limit count of backups must be >= 1, but got {limit}')
        return False

    backups_list = []

    with os.scandir(root) as it:
        for entry in it:
            if entry.is_file():
                print(f'Suspicious file "{entry.name}" skipped.')
                continue
            backups_list.append(entry.path)

    backups_list.sort()

    outdated_backups = backups_list[limit:]
    for path in outdated_backups:
        os.remove(path)

    return True


def move_new_backup(backup_directory: str, root: str) -> bool:
    now = datetime.datetime.now(datetime.UTC)
    if not os.path.isdir(backup_directory):
        print(f'Specified path of backup directory is not a directory: "{backup_directory}"!')
        return False

    backup_filename = f'backup_{now.strftime('%Y_%m_%d_%H:%M:%S')}'
    new_directory = os.path.join(root, backup_filename)
    shutil.move(backup_directory, new_directory)

    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', 'Specifies the name of the database to be dumped', required=True)
    parser.add_argument('--username', 'User name to connect as.', required=True)
    parser.add_argument('--output', 'The root directory for backup history.', required=True)
    parser.add_argument('--history', 'Specifies the count of backups to be stored.', required=True, type=int)
    args = parser.parse_args()

    if args.history < 1:
        print(f'History must be >= 1, but got {args.history}!')

    temp_output = tempfile.mkdtemp('wishlist_temp_backup_')
    print(f'Temp backup directory is "{temp_output}"')

    backup_completed = make_backup(args.database, args.username, temp_output)
    if not backup_completed:
        print('Failed to complete backup!')
        exit(-2)

    if not remove_outdated_backups(args.output, args.history):
        print('Failed to remove outdated backups!')
        exit(-3)

    if not move_new_backup(temp_output, args.output):
        print('Failed to move backup from temp to new directory!')
        exit(-4)

    return 0


if __name__ == '__main__':
    error_code = main()
    exit(error_code)
