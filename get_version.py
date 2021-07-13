#!/usr/bin/python
# coding=utf-8

import git, shutil, os, sys

print(sys.version_info)

if os.path.exists('self-checking'):
    os.chdir(os.path.join(os.getcwd(), 'self-checking'))

print(os.listdir(os.getcwd()))

git.Repo('.').remotes['origin'].pull()

files_path = os.getcwd()+'/files'
if os.path.exists(files_path):
    shutil.rmtree(files_path)

import init_db

print('done')