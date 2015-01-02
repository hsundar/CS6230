#include <stdio.h>
#include <mpi.h>

#include "common.h"

int sample_hello(MPI_Comm comm);

int sample_hello(MPI_Comm comm) {
  int rank, size;
  MPI_Comm_rank(comm, &rank);
  MPI_Comm_size(comm, &size);

  char host[256];
  int len;
  MPI_Get_processor_name(host, &len);

  printf("Hello from sample.\n I am process %d of %d.\nMy name is %s", rank, size, host);

  return CS6230_SUCCESS;
}
