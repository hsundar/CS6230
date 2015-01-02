#!/usr/bin/python 

import sys
import tarfile
import os

def usage():
  print 'Usage: build.py <command>'
  print '    where,'
  print '          command: problem_name\n                 : test\n                 : archive'
  print ' '
  print 'examples: '
  print '          ./build.py hello'
  print '          ./build test'
  sys.exit(1)

students = os.listdir('./students');
# print students

# will take 1 arguments ...
if len(sys.argv) < 2:
  usage();

cmd  = sys.argv[1];

if cmd == 'test':
  print 'will test the program'
  sys.exit(0)
  
if cmd == 'archive':
  if len(sys.argv) > 2:
    pt = sys.argv[2].split('/');
    pt = filter(None, pt);
    tar = tarfile.open(pt[-1] +'.tgz', "w:gz")
    for root, dirs, files in os.walk(sys.argv[2]):
      for name in files:
        print 'adding: ', os.path.join(root, name)
        tar.add(os.path.join(root, name))
    tar.close()
  else:
    tar = tarfile.open('all.tgz', "w:gz")
    for root, dirs, files in os.walk('./students/'):
      for name in files:
        print 'adding: ', os.path.join(root, name)
        tar.add(os.path.join(root, name))
    tar.close()

  sys.exit(0)

print 'Will compile code for problem ', cmd

# generate the correct code autogen.c

# build
