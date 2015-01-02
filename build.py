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
print students

# will take 1 arguments ...
if len(sys.argv) < 2:
  usage();

cmd  = sys.argv[1];

if cmd == 'test':
  print 'will test the program'
  sys.exit(0)
  
if cmd == 'archive':
  print 'will create an archive of files under students/'
  if len(students) == 1:
    tar = tarfile.open(students[1]+'.tar', "w")
    for name in os.walk('./students/'+students[1]):
      tar.add(name)
    tar.close()
  else:
    tar = tarfile.open('all.tar', "w")
    for name in os.walk('./students/'):
      tar.add(name)
    tar.close()

  sys.exit(0)

print 'Will compile code for problem ', cmd

