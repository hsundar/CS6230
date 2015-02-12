#!/usr/bin/python 

import sys
import tarfile
import os
import random

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

# generate the code main.c && compile
if sys.argv[1]=='compile':
  if len(sys.argv) != 5:
    print 'Please enter the program name in command line argument!!! See below for reference'
    print 'python build.py compile <Program_name> <Data_Type> <Operation_Type>'
    sys.exit()
  Data_type_list=['int','float','double','long']
  Operation_type_list=['SUM','PROD','MIN','MAX']
  program_name_list=['Reduce.c','Scan.c']
  program_name=sys.argv[2]
  Data_type=sys.argv[3].lower()
  Operation_type=sys.argv[4].upper()
  if any(program_name in slist for slist in program_name_list):
    check=0
  else:
    print 'ERROR in program name!!Program name should be Scan.c or Reduce.c'
    sys.exit()
  if any(Data_type in slist for slist in Data_type_list):
    check=0
  else:
    print 'ERROR in data type!!Data type should be int,float,long or double'
    sys.exit()
  if any(Operation_type in slist for slist in Operation_type_list):
    check=0
  else:
    print 'ERROR in Operation type!!Operation type should be sum,prod,max,min'
    sys.exit()

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
  for user in users:
    if program_name=='Reduce.c':
      file_out.write('extern void '+user+'_Reduce(const void* sendbuf, void* recvbuf, int count, MPI_Datatype datatype, MPI_Op op, int root, MPI_Comm comm);\n')
    elif program_name=='Scan.c':
      file_out.write('extern void '+user+'_Scan(const void* sendbuf, void* recvbuf, int count, MPI_Datatype datatype, MPI_Op op, MPI_Comm comm);\n');
  file_out.write('int main(int argc, char *argv[]){\n\tint Rank=0,i,flag=0,flag1=0,ProcessRank,NumberofProcess,numberofElements;\n\t'+Data_type+' *number,*copy,*stud_result,*result,*temp;\n\tFILE *fptr=fopen("Results.txt","a");\n\tdouble t1,t2,timetaken;')
  file_out.write('\n\tMPI_Init(&argc,&argv);\n\tMPI_Comm_rank(MPI_COMM_WORLD,&ProcessRank);\n\tMPI_Comm_size(MPI_COMM_WORLD,&NumberofProcess);\n\t Rank=NumberofProcess/2;\n')
  file_out.write('\tnumberofElements= atoi(argv[1]);\n\tnumber = ('+Data_type+'*) malloc(sizeof('+Data_type+')*numberofElements);\n\tresult=('+Data_type+'*) malloc(sizeof('+Data_type+')*numberofElements);\n\tstud_result=('+Data_type+'*)malloc(sizeof('+Data_type+')*numberofElements);\n\tcopy=('+Data_type+'*)malloc(sizeof('+Data_type+')*numberofElements);\n\tsrand((unsigned int) (numberofElements*ProcessRank));\n\tfor(i=0;i<numberofElements;i++)\n\t\tnumber[i]= rand()%100;\n\t')
  if(program_name=='Reduce.c'):
    file_out.write('MPI_Reduce(('+Data_type+'*)number,('+Data_type+'*)result,numberofElements,MPI_'+Data_type.upper()+',MPI_'+Operation_type+',Rank,MPI_COMM_WORLD);\n\t')
  elif(program_name=='Scan.c'):
    file_out.write('\n\tMPI_Scan(('+Data_type+'*)number,('+Data_type+'*)result,numberofElements,MPI_'+Data_type.upper()+',MPI_'+Operation_type+',MPI_COMM_WORLD);\n\t')
  for user in users:
    file_out.write('for(i=0;i<numberofElements;i++)\n\t\t copy[i]=number[i];');
    file_out.write('t1=MPI_Wtime();\n\t')
    if(program_name=='Reduce.c'):
      file_out.write(user+'_'+program_name[:len(program_name)-2]+'(('+Data_type+'*)copy,('+Data_type+'*)stud_result,numberofElements,MPI_'+Data_type.upper()+',MPI_'+Operation_type+',Rank,MPI_COMM_WORLD);\n\t')
    if(program_name=='Scan.c'):
      file_out.write(user+'_'+program_name[:len(program_name)-2]+'(('+Data_type+'*)copy,('+Data_type+'*)stud_result,numberofElements,MPI_'+Data_type.upper()+',MPI_'+Operation_type+',MPI_COMM_WORLD);\n\t')
      
    file_out.write('t2=MPI_Wtime()-t1;\n\tMPI_Reduce((double*)&t2,(double*)&timetaken,1,MPI_DOUBLE,MPI_SUM,Rank,MPI_COMM_WORLD);\n\t')
    command+=' students/'+user+'/'+program_name
    if program_name == 'Reduce.c':
      file_out.write('if(ProcessRank==Rank){\n\t\tfor(i=0;i<numberofElements;i++)\n\t\t\tif(result[i]!=stud_result[i]){\n\t\t\t\tfprintf(fptr,"\\n%s\\t incorrect\\t %f\\t %d","'+user+'",timetaken,NumberofProcess);\n\t\t\t\tbreak;\n\t\t\t}\n\t\tif(i==numberofElements)\n\t\t\tfprintf(fptr,"\\n%s\\t correct\\t %f\\t %d","'+user+'",timetaken,NumberofProcess);\n\t}\n\t')
    if program_name == 'Scan.c':
      file_out.write('\n\t for(i=0;i<numberofElements;i++)\n\t\tif(result[i]!=stud_result[i]){\n\t\t\tflag=1;\n\t\t\tbreak;\n\t\
\t}\n\tMPI_Reduce((int*)&flag,(int*)&flag1,1,MPI_INT,MPI_SUM,Rank,MPI_COMM_WORLD);')
      file_out.write('\n\t if(ProcessRank==Rank){\n\t\tif(flag1==0)\n\t\t\tfprintf(fptr,"\\n%s\\t correct\\t %f\\t %d","'+user+'",timetaken,NumberofProcess);\n\telse\n\t\t\tfprintf(fptr,"\\n%s\\t not correct\\t%f\\t%d","'+user+'",timetaken,NumberofProcess);}\n\tflag1=flag=0;\n\t' )
  file_out.write('MPI_Finalize();\n\t');
  file_out.write('fclose(fptr);\n}')
  print 'mpicc -o output main.c '+command
  file_out.close()
  if(os.path.isfile(os.getcwd()+'/output')):
       os.remove(os.getcwd()+'/output')
  check=os.system('mpicc -o output main.c '+command)
  if check==0:
    if(os.path.isfile(os.getcwd()+'/Results.txt')):
      os.remove(os.getcwd()+'/Results.txt')
    for x in range(1,16):
      check=os.system('mpirun -np '+str(x)+' ./output '+str(random.randrange(1,15)))
      if check != 0:
        print 'Error in program runtime.Check your code'
        sys.exit()
  else:
    print 'Compilation error: Check your program'

# build
