from . import api
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="cmods - a simple package manager for C and C++.")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="sub-command help")

    parser_init = subparsers.add_parser("init", help="Initializes cmods.")

    parser_make = subparsers.add_parser("make", help="Build's the build.")
    parser_make.add_argument("path", type=str, help="Path to the project dir.")

    parser_add_repo = subparsers.add_parser("add-repo", help="Add a new repo.")
    parser_add_repo.add_argument("name", type=str, help="Repo name.")
    parser_add_repo.add_argument("url", type=str, help="Repo url.")


    parser_del_repo = subparsers.add_parser("del-repo", help="Deletes a repo.")
    parser_del_repo.add_argument("name", type=str, help="Repo name.")

    parser_add_mod = subparsers.add_parser("add-mod", help="Adds a Module.")
    parser_add_mod.add_argument("name", type=str, help="Module name.")
    parser_add_mod.add_argument("repo", type=str, help="Module repo.")

    parser_del_mod = subparsers.add_parser("del-mod", help="Deletes a Module.")
    parser_del_mod.add_argument("name", type=str, help="Module name.")

    parser_cflags = subparsers.add_parser("set-cflags", help="Set CFLAGS.")
    parser_cflags.add_argument("flags", nargs=argparse.REMAINDER, help="Cflags.")

    args = parser.parse_args()

    if args.command == "set-cflags":
        api.manage.cmods_set_cflags(" ".join(args.flags))
    elif args.command == "init":
        api.init.init_project()
    elif args.command == "make":
        api.make.make(args.path)
    elif args.command == "add-repo":
        api.manage.cmods_repo_add(args.name, args.url)
    elif args.command == "del-repo":
        api.manage.cmods_repo_del(args.name)
    elif args.command == "add-mod":
        api.manage.cmods_mod_add(args.name, args.repo)
    elif args.command == "del-mod":
        api.manage.cmods_mod_del(args.name)
