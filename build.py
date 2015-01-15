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

# generate the correct code main.c && compile

if sys.argv[1]=='compile':
    if len(sys.argv) < 3:
        print 'Please enter the program name in command line argument!!! See below for reference'
        print 'python build.py compile <Program_name>'
        sys.exit()
    program_name=sys.argv[2]
    count=0
    users=[]
    command=''
    for dirname in os.walk(os.getcwd()+'/students'):
        file_path=dirname[0]+'/'+program_name
        if os.path.isfile(file_path):
            count=count+1
            users.append(dirname[0][len(dirname[0])-8:])
    if count==0:
        print 'No valid c file names to compile\n check c file names'
        sys.exit()
    file_out=open("main.c","w")
    file_out.write("#include<mpi.h> \n#include<stdio.h> \n#include<time.h> \n#include<stdlib.h>\n")
    file_out.write('int main(int argc, char *argv[]){\n\tint i,*result,*stud_result,ProcessRank,*number,numberofElements;\n\tFILE *fptr=fopen("Results.txt","w");')
    file_out.write('\n\tMPI_Init(&argc,&argv);\n\tMPI_Comm_rank(MPI_COMM_WORLD,&ProcessRank);\n')
    file_out.write('\tnumberofElements= atoi(argv[1]);\n\tnumber = (int*) malloc(sizeof(int)*numberofElements);\n\tresult=(int*) malloc(sizeof(int)*numberofElements);\n\tsrand((unsigned int) (numberofElements*ProcessRank));\n\tfor(i=0;i<numberofElements;i++)\n\t\tnumber[i]= rand()%100;\n\tMPI_Reduce(number,result,numberofElements,MPI_INT,MPI_SUM,0,MPI_COMM_WORLD);\n\t')
    for user in users:
        file_out.write('stud_result='+user+'_'+program_name[:len(program_name)-2]+'(number,numberofElements);\n\tMPI_Barrier(MPI_COMM_WORLD);\n\t');
        command+=' students/'+user+'/'+program_name
        if program_name == 'Reduce.c':
          file_out.write('if(ProcessRank==0){\n\t\tfor(i=0;i<numberofElements;i++)\n\t\t\tif(result[i]!=stud_result[i]){\n\t\t\t\tprintf("the user %s result is not correct\\n","'+user+'");\n\t\t\t\tbreak;\n\t\t\t}\n\t\tif(i==numberofElements)\n\t\t\tprintf("the user %s result is correct\\n","'+user+'");\n\t}\n\t')
    file_out.write('MPI_Finalize();\n\t');
    file_out.write('fclose(fptr);\n}')
    print 'mpicc -o a main.c'+command
    file_out.close()
    os.system('mpicc -o a main.c'+command)
    os.system('mpirun -n 7 ./a 4')
    

# build
