#!/bin/bash
#SBATCH -J myMPI           # job name
#SBATCH -o myMPI.o%j       # output and error file name (%j expands to jobID)
#SBATCH -N 2 -n 32         # total number of mpi tasks requested - 2 nodes, 32 tasks
#SBATCH -p normal          # queue (partition) -- normal, development, etc.
#SBATCH -t 01:30:00        # run time (hh:mm:ss) - 1.5 hours
#SBATCH --mail-user=username@tacc.utexas.edu   # email address for notification
#SBATCH --mail-type=begin  # email me when the job starts
#SBATCH --mail-type=end    # email me when the job finishes

ibrun ./hello_mpi              # run the MPI executable named hello_mpi

