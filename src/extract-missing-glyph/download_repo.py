import os
import shutil
from git import Repo, GitCommandError
from pathlib import Path

org_name = "OpenPecha-Data"


def read_repo_names(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def clone_repo(repo_name):
    repo_url = f"https://github.com/{org_name}/{repo_name}.git"
    clone_dir = Path(f"./tmp/{repo_name}")
    if not clone_dir.exists():
        clone_dir.mkdir(parents=True)
        try:
            Repo.clone_from(repo_url, clone_dir)
        except GitCommandError:
            return None
    return clone_dir


def find_opf_directories(repo_path):
    opf_directories = []
    for item in os.listdir(repo_path):
        item_path = os.path.join(repo_path, item)
        if os.path.isdir(item_path) and item.endswith('.opf'):
            opf_directories.append(item_path)
    return opf_directories


def copy_opf_directories(opf_directories, destination_path):
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    for opf_dir in opf_directories:
        dest_dir = os.path.join(destination_path, os.path.basename(opf_dir))
        print(f"copying {opf_dir} to {dest_dir}")
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        shutil.copytree(opf_dir, dest_dir)


def main():
    repo_list_file = '../../data/opf_pecha.txt'
    destination_path = '../../data/opf'
    repo_names = read_repo_names(repo_list_file)
    for repo_name in repo_names:
        repo_path = clone_repo(repo_name)
        if repo_path:
            opf_directories = find_opf_directories(repo_path)
            if opf_directories:
                copy_opf_directories(opf_directories, destination_path)


if __name__ == "__main__":
    main()
