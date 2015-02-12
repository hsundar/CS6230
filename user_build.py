#!/usr/bin/python

import sys
import tarfile
import os
import random
import subprocess

def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise ProcessException(command, exitCode, output)

def show_help():
    print 'user_build.py <user> <command> [command-options]'
    print 'command : compile test archive'
    print ' '
    print '  compile-option : <program-name> <data-type> <reduction-op>'
    print ' '
    print '    program-name : Reduce Scan'
    print '    data-type    : int long float double'
    print '    reduction-op : SUM PROD MIN MAX'
    print ' '
    print 'Examples:'
    print '  user_build.py uxxxxxxx compile Reduce int SUM'
    print '  user_build.py uxxxxxxx test'
    print '  user_build.py uxxxxxxx archive'
    sys.exit(0)

# will take 1 arguments ...
if len(sys.argv) < 2:
    show_help();

user = sys.argv[1];
user_dir = './students/' + user + '/';

command = sys.argv[2];

#print 'user: {}'.format(user)
#print 'user_dir: {}'.format(user_dir)

if command == 'compile':
    if len(sys.argv) != 6:
        print 'Missing compile arguments'
        show_help()
    #
    program_name_list=['Reduce','Scan']
    data_type_list=['int','float','double','long']
    reduction_op_list=['SUM','PROD','MIN','MAX']
    #
    program_name = sys.argv[3];
    data_type    = sys.argv[4].lower();
    reduction_op = sys.argv[5].upper();
    #
    check_input = True;
    if program_name not in program_name_list:
        print 'Invalid program name: {}'.format(program_name);
        check_input = False;
    if data_type not in data_type_list:
        print 'Invalid data type: {}'.format(data_type);
        check_input = False;
    if reduction_op not in reduction_op_list:
        print 'Invalid reduction_op: {}'.format(reduction_op);
        check_input = False;
    if not check_input:
        show_help()
    #
    #write main
    user_main = open(user_dir+'main.c','w');
    user_main.write('#include<mpi.h>\n');
    user_main.write('#include<stdio.h>\n');
    user_main.write('#include<stdlib.h>\n');
    user_main.write('\n');
    if(program_name=='Reduce'):
      user_main.write('extern void '+user+'_'+program_name+'(const void* sendbuf, void* recvbuf, int count, MPI_Datatype datatype, MPI_Op op, int root, MPI_Comm comm);\n')
    else:
      user_main.write('extern '+user+'_'+program_name+'(const void* sendbuf, void* recvbuf, int count, MPI_Datatype datatype, MPI_Op op, MPI_Comm comm);\n')
    user_main.write('\n');
    user_main.write('int main(int argc, char *argv[])\n');
    user_main.write('{\n');
    user_main.write('  typedef '+data_type+' data_type;\n');
    user_main.write('  int parallel_rank, parallel_size;\n');
    user_main.write('  MPI_Comm parallel_comm = MPI_COMM_WORLD;\n');
    user_main.write('  int element_count, i;\n');
    user_main.write('  void * buffer;\n');
    user_main.write('  data_type *original, *result, *gold_result;\n');
    user_main.write('  int local_errors, global_errors, root;\n');
    user_main.write('  double t1, t2, user_time, gold_time;\n');
    user_main.write('  \n');
    user_main.write('  MPI_Init(&argc,&argv);\n');
    user_main.write('  MPI_Comm_rank(parallel_comm, &parallel_rank);\n');
    user_main.write('  MPI_Comm_size(parallel_comm, &parallel_size);\n');
    user_main.write('  \n');
    user_main.write('  element_count = argc > 1 ? atoi(argv[1]) : 1;\n');
    user_main.write('  \n');
    user_main.write('  buffer = malloc(3*sizeof(data_type)*element_count);\n');
    user_main.write('  original = (data_type*)buffer;\n');
    user_main.write('  result = ((data_type*)buffer) + element_count;\n');
    user_main.write('  gold_result = ((data_type*)buffer) + 2*element_count;\n');
    user_main.write('  \n');
    user_main.write('  srand((unsigned)(element_count*parallel_rank));\n');
    user_main.write('  for (i=0; i < element_count; ++i) { original[i] = (data_type)(rand()%100); }\n');
    if program_name=='Reduce':
        user_main.write('  root = parallel_size/2;\n');
        user_main.write('  t1 = MPI_Wtime();\n');
        user_main.write('  MPI_Reduce(original,gold_result,element_count,MPI_'+data_type.upper()+',MPI_'+reduction_op+',root,MPI_COMM_WORLD);\n')
        user_main.write('  t2 = MPI_Wtime() - t1;\n');
        user_main.write('  MPI_Reduce(&t2,&gold_time,1,MPI_DOUBLE,MPI_SUM,root,parallel_comm);\n\t')
        user_main.write('  t1 = MPI_Wtime();\n');
        user_main.write('  '+user+'_Reduce(original,result,element_count,MPI_'+data_type.upper()+',MPI_'+reduction_op+',root,MPI_COMM_WORLD);\n')
        user_main.write('  t2 = MPI_Wtime() - t1;\n');
        user_main.write('  MPI_Reduce(&t2,&user_time,1,MPI_DOUBLE,MPI_SUM,root,parallel_comm);\n\t')
        user_main.write('  if (root == parallel_rank) {\n');
        user_main.write('    local_errors = 0;\n');
        user_main.write('    for (i=0; i < element_count; ++i) {\n');
        user_main.write('      if ( gold_result[i] != result[i] ) { ++local_errors; }\n');
        user_main.write('    }\n');
        user_main.write('    if ( local_errors == 0 ) {\n');
        user_main.write('      printf("%s   correct     user-time=%1.2e  gold-time=%1.2e   parallel-size=%d   element-count=%d  root=%d\\n","'+user+'",user_time,gold_time,parallel_size,element_count,root);\n');
        user_main.write('    } else {\n');
        user_main.write('      printf("%s   incorrect   user-time=%1.2e  gold-time=%1.2e   parallel-size=%d   element-count=%d  root=%d\\n","'+user+'",user_time,gold_time,parallel_size,element_count,root);\n');
        user_main.write('    }\n');
        user_main.write('  }\n');
    elif program_name=='Scan':
        user_main.write('  t1 = MPI_Wtime();\n');
        user_main.write('  MPI_Scan(original,gold_result,element_count,MPI_'+data_type.upper()+',MPI_'+reduction_op+',MPI_COMM_WORLD);\n')
        user_main.write('  t2 = MPI_Wtime() - t1;\n');
        user_main.write('  MPI_Reduce(&t2,&gold_time,1,MPI_DOUBLE,MPI_SUM,0,parallel_comm);\n\t')
        user_main.write('  t1 = MPI_Wtime();\n');
        user_main.write('  '+user+'_Scan(original,result,element_count,MPI_'+data_type.upper()+',MPI_'+reduction_op+',MPI_COMM_WORLD);\n')
        user_main.write('  t2 = MPI_Wtime() - t1;\n');
        user_main.write('  MPI_Reduce(&t2,&user_time,1,MPI_DOUBLE,MPI_SUM,0,parallel_comm);\n\t')
        user_main.write('  local_errors = 0;\n');
        user_main.write('  for (i=0; i < element_count; ++i) {\n');
        user_main.write('    if ( gold_result[i] != result[i] ) { ++local_errors; }\n');
        user_main.write('  }\n');
        user_main.write('  MPI_Reduce(&local_errors,&global_errors,1,MPI_INT,MPI_SUM,0,parallel_comm);\n\t')
        user_main.write('  if ( parallel_rank==0 && global_errors == 0 ) {\n');
        user_main.write('    printf("%s   correct     user-time=%1.2e  gold-time=%1.2e   parallel-size=%d   element-count=%d\\n","'+user+'",user_time,gold_time,parallel_size,element_count);\n');
        user_main.write('  } else if ( parallel_rank == 0 ) {\n');
        user_main.write('    printf("%s   incorrect   user-time=%1.2e  gold-time=%1.2e   parallel-size=%d   element-count=%d\\n","'+user+'",user_time,gold_time,parallel_size,element_count);\n');
        user_main.write('  }\n');
    #
    user_main.write('  free(buffer);\n');
    user_main.write('  MPI_Finalize();\n');
    user_main.write('  return 0;\n');
    user_main.write('}\n');
    user_main.close();
    #
    execute('mpicc -o '+user_dir+'test.x '+user_dir+'main.c '+user_dir+program_name+'.c');
    command = 'test';

if command == 'test':
    if os.path.isfile(user_dir+'test.x'):
        for x in range(1,16):
            execute('mpirun -np '+str(x)+' ./'+user_dir+'test.x '+str(random.randrange(1,15)))
    sys.exit(0);

if command == 'archive':
    tar = tarfile.open(user+'.tgz', 'w:gz');
    for base_dir, dirs, files in os.walk(user_dir):
        for name in files:
            print 'adding: {}'.format(base_dir + name);
            tar.add(os.path.join(base_dir,name));
    tar.close();
    sys.exit(0);

print 'Unknow command {}'.format(command)
sys.exit(1)
