#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from hashlib import sha1
from datetime import datetime


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument('command', help='put command')
    parser.add_argument('filename', nargs='*')
    parser.add_argument('--author', default=os.environ['LOGNAME'])
    parser.add_argument('-m', "--commit-message")
    args = parser.parse_args()
    return args

# The command lgit init will create the directory structure.
def create_lgit():
    os.mkdir('.lgit')
    os.mkdir('.lgit/objects')
    os.mkdir('.lgit/commits')
    os.mkdir('.lgit/snapshots')

    index = os.open('.lgit/index', os.O_RDWR | os.O_CREAT)
    config = os.open('.lgit/config', os.O_RDWR | os.O_CREAT)
    var_name = os.environ['LOGNAME'].encode()
    os.write(config, var_name)
    os.close(index)
    os.close(config)


def get_lgit_base():
    current_dir = os.getcwd()
    paths = current_dir.split('/')
    for i in range(len(paths), 0, -1):
        current_testing_path = '/'.join(paths[:i])
        if os.path.exists(current_testing_path + '/.lgit'):
            return current_testing_path


def lgit_exist():
    exist = False
    current_dir = os.getcwd()
    paths = current_dir.split('/')
    for i in range(len(paths), 0, -1):
        current_testing_path = '/'.join(paths[:i]) + '/.lgit'
        if os.path.exists(current_testing_path):
            exist = True
            break
    return exist


def add_both(names):
    for name in names:
        if os.path.isfile(name):
            add_object(name)
            add_index(name)
        # print('Name:', name)
        for root, _, files in os.walk(name):
            for file in files:
                if '.lgit' not in root:
                    file_path = os.path.join(root, file)
                    # if 'lgit' not in file_path:
                    add_object(file_path)
                    add_index(file_path)


def encode_file(filename):
    file = os.open(filename, os.O_RDONLY)
    file_read = os.read(file, os.stat(file).st_size)
    file_hash = sha1(file_read).hexdigest()
    os.close(file)     # not sure if needed
    return file_hash, file_read


def get_line(file_path, index_content):
    lines = index_content.decode().split('\n')
    summ = 0
    for line in lines:
        if line != '':
            info = line.split()
            if not info == [] and file_path == info[-1]:
                return lines.index(line), summ
            summ += len(info[-1])


def add_index(file_path):
    file_hash = encode_file(file_path)[0]
    timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y%m%d%H%M%S")
    
    lgit_base = get_lgit_base()
    with open(lgit_base + "/.lgit/index", "r+") as index_file:
        current_indice = index_file.readlines()
        index_file.seek(0)
        # check if path has already been in index
        already_in = False
        file_path = (os.getcwd() + '/' + file_path)[len(lgit_base) + 1:]
        for index_line in current_indice:
            if file_path in index_line:
                already_in = True
                new_index_line = timestamp +  ' ' + file_hash + ' ' + file_hash + ' ' + index_line[97:]
                index_file.write(new_index_line)
            else:
                index_file.write(index_line)

        if not already_in:
            index_file.write(timestamp + ' ' + file_hash + ' ' + file_hash + ' ' + (' ' * 40) + ' ' + file_path + '\n')

        index_file.truncate()


def update_indice():
    changes_to_be_commited = []
    changes_not_staged_for_commit = []
    untracked_files = []

    # Get all the files in the current pwd
    for root, _, files in os.walk(get_lgit_base()):
        for file in files:
            file_path = os.path.join(root, file)
            if ".lgit" not in file_path:
                untracked_files.append(file_path)

    lgit_base = get_lgit_base()
    with open(lgit_base + "/.lgit/index", "r+") as index_file:
        current_indice = index_file.readlines()
        index_file.seek(0)
        for index_line in current_indice:
            file_path = lgit_base + '/' + index_line[138:].strip()
            current_time_of_file = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y%m%d%H%M%S")
            file_hash = encode_file(file_path)[0]
            current_added_hash = index_line[56:96]
            current_commited_hash = index_line[97:137]

            if file_hash != current_added_hash:
                changes_not_staged_for_commit.append(file_path[len(lgit_base) + 1:])

            if current_added_hash != current_commited_hash:
                changes_to_be_commited.append(file_path[len(lgit_base) + 1:])

            if file_path in untracked_files:
                untracked_files.remove(file_path)

            # update the index line
            new_index = current_time_of_file + ' ' + file_hash + index_line[55:]
            index_file.write(new_index)
        index_file.truncate()
    
    return changes_to_be_commited, changes_not_staged_for_commit, [path[len(lgit_base) + 1:] for path in untracked_files]


#pos:
#   1: the timestamp of the file in the working directory
#   2: the SHA1 of the content in the working directory
#   3: the SHA1 of the file content after you lgit add'ed it
#   4: the SHA1 of the file content after you lgit commit'ed it
#   5: the file pathname
def update_index(file_path, content, pos):
    with open(get_lgit_base() + "/.lgit/index") as index_file:
        current_indice = index_file.readlines()
        index_file.seek(0)
        for index_line in current_indice:
            new_index = index_line

            if file_path in index_line:
                if pos == 1:
                    new_index = content + index_line[14:]
                elif pos == 2:
                    index_line[:15] + content + index_line[55:]
                elif pos == 3:
                    index_line[:55] + content + index_line[95:]
                elif pos == 4:
                    index_line[:95] + content + index_line[135:]
                else:
                    index_line[:135] + content
            
            index_file.write(new_index)


#pos:
#   1: the timestamp of the file in the working directory
#   2: the SHA1 of the content in the working directory
#   3: the SHA1 of the file content after you lgit add'ed it
#   4: the SHA1 of the file content after you lgit commit'ed it
#   5: the file pathname
def get_index_info(file_path, pos):
    with open(get_lgit_base() + "/.lgit/index", "r") as index_file:
        current_indice = index_file.readlines()
        index_file.seek(0)
        for index_line in current_indice:
            if file_path in index_line:
                return index_line.split(' ')[pos - 1]


def add_object(file_path):
    encode_content, file_content = encode_file(file_path)
    dir_path = get_lgit_base() + '/.lgit/objects/' + encode_content[:2]
    if os.path.isdir(dir_path) is False:
        os.mkdir(dir_path)  # make dir
    object_name = os.open(dir_path + '/' + encode_content[2:], os.O_RDWR | os.O_CREAT)
    os.write(object_name, file_content)  # os.write object content
    os.close(object_name)


def config_file(args):
    # if args is not None:
    config_f = os.open(get_lgit_base() + '/.lgit/config', os.O_TRUNC | os.O_RDWR)
    os.write(config_f, args.encode())


def list_files():
    current_dir = os.getcwd()
    files_in_dir = []

    for file in os.listdir(current_dir):
        if os.path.isfile(file):
            files_in_dir.append(current_dir + '/' + file)

    lgit_base = get_lgit_base()
    with open(lgit_base + "/.lgit/index", "r") as index_file:
        current_indice = index_file.readlines()
        intersection = [index[138:].strip("\n") for index in current_indice if (lgit_base + '/' + index[138:].strip("\n")) in files_in_dir]
        
        if len(intersection) > 0:
            print("Tracking file:")
            print()
            for file in intersection:
                print("\t" + file)


def get_status():
    # Update index
    to_commit, not_staged, untracked_files = update_indice()
    print("On branch master")
    print()
    # print changes to be commited
    print("Changes to be committed:")
    print("\t(use \"./lgit.py reset HEAD ...\" to unstage)")
    print()
    for file_path in to_commit:
        print("\t\t" + file_path)
    print()
    #print changes not staged for commit
    print("Changes not staged for commit:")
    print("\t(use \"./lgit.py add ...\" to update what will be committed)")
    print("\t(use \"./lgit.py checkout -- ...\" to discard changes in working directory)")
    print()
    for file_path in not_staged:
        print("\t\tmodified: " + file_path)
    print()

    # print untracked
    print("Untracked files:")
    print("\t(use \"./lgit.py add <file>...\" to include in what will be committed)")
    for file_path in untracked_files:
        print("\t\t" + file_path)

    if len(to_commit) == 0 and len(untracked_files) > 0:
        print()
        print("nothing added to commit but untracked files present (use \"./lgit.py add\" to track)")


def commit_all(args):
    commiting_files = []
    with open(get_lgit_base() + "/.lgit/index", "r+") as index_file:
        current_indice = index_file.readlines()
        index_file.seek(0)
        for index_line in current_indice:
            new_index_line = index_line
            current_added_hash = index_line[56:96]
            current_commited_hash = index_line[97:137]
            if current_added_hash != current_commited_hash:
                commiting_files.append(current_added_hash + index_line[137:].strip("\n"))
                new_index_line = index_line[:96] + ' ' + current_added_hash + index_line[137:]

            index_file.write(new_index_line)
        index_file.truncate()

    if len(commiting_files) > 0:
        # preparation
        timestamp = str(datetime.now().timestamp())
        author = os.environ['LOGNAME']
        with open(get_lgit_base() + "/.lgit/config", "r") as config_file:
            author = config_file.readline()

        # create the commit file
        commit_file = os.open(get_lgit_base() + "/.lgit/commits/" + timestamp, os.O_RDWR | os.O_CREAT)
        commit_content = author + '\n' + timestamp + "\n\n" + args.commit_message
        os.write(commit_file, commit_content.encode())
        os.close(commit_file)
        
        snapshot_file = os.open(get_lgit_base() + "/.lgit/snapshots/" + timestamp, os.O_RDWR | os.O_CREAT)
        snapshot_content = "\n".join(commiting_files)
        os.write(snapshot_file, snapshot_content.encode())
        os.close(snapshot_file)
    else:
        print("(Nothing to commit)")


def show_log():
    commits = []
    for root, _, files in os.walk(get_lgit_base() + "/.lgit/commits"):
        for file in files:
            file_path = os.path.join(root, file)
            commits.insert(0, file_path)

    for commit_path in commits:
        with open(commit_path, 'r') as commit_file:
            commit_content = commit_file.readlines()
            author = commit_content[0].strip("\n")
            time = commit_content[1].strip("\n")
            message = commit_content[3]
            print("commit " + commit_path.split('/')[-1])
            print("Author: " + author)
            print("Date: " + datetime.fromtimestamp(float(time)).strftime("%a %b %d %H:%M:%S %Y"))
            print()
            print("\t" + message)
            print()
            print()



class Commands:
    def __init__(self):
        self.args = get_arguments()
        if self.args.command != 'init':
            if lgit_exist():
                self.do_command(self.args.command)
            else:
                print('fatal: not a git repository (or any of the parent directories)')
        else:
            self.do_command(self.args.command)

    def do_command(self, command):
        if command == 'ls-files':
            command = 'ls'
        return getattr(self, str(command))(self.args)

    def init(self, args):
        if len(args.filename) == 0:
            if lgit_exist() is False:
                create_lgit()
        else:
            folder_path = args.filename[0]
            # if filename is a file - print FatalError
            if os.path.isfile(folder_path):
                print('fatal: cannot mkdir %s: File exists' % folder_path)
                return
            # if filename not exists make a dir
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            os.chdir(folder_path)
            create_lgit()
        print('init')

    def add(self, args):
        # lgit add: stages changes, should work with files and recursively with directories
        if args.filename is None:
            print('Nothing specified, nothing added.')
            return
        add_both(args.filename)


    def rm(self, args):
        # lgit rm: os.removes a file from the working directory and the index
        # os.remove a file:
        # os.remove(args.filename)
        with open('.lgit/index', "r+") as index_file:
            current_indice = index_file.readlines()
            index_file.seek(0)
            for index in current_indice:
                if args.filename not in index:
                    index_file.write(index)
            index_file.truncate()


    def config(self, args):
        # lgit config --author: sets a user for authoring the commits
        config_file(args.author)

    def commit(self, args):
        # lgit commit -m: creates a commit with the changes currently staged
        # (if the config file is empty, this should not be possible!)
        commit_all(args)

    def status(self, args):
        # lgit os.status:
        # updates the index with the content of the working directory and displays the os.status of tracked/untracked files
        get_status()

    def ls(self, args):
        # lgit ls-files: lists all the files currently tracked in the index, relative to the current directory
        list_files()

    def log(self, args):
        # lgit log: shows the commit history
        show_log()

    def base(self, args):
        get_lgit_base()


def main():
    # DON'T FIX THIS
    Commands()


if __name__ == '__main__':
    main()
