#include <omp.h>
#include <mpi.h>

#include <stdio.h>
#include <stdlib.h>

int main (int argc, char *argv[]) 
{
  if (argc >1)
    omp_set_num_threads(atoi(argv[1]));
  else
    omp_set_num_threads(2);

  MPI_Init(&argc, &argv);

  int rank, size, num_threads;
  int   i, n;
  float a[100], b[100], local_sum, global_sum; 

  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  
  num_threads = omp_get_max_threads();

  if (!rank) 
    printf ("%d tasks, each with %d threads\n", size, num_threads);

  srand(rank+size*5);

  /* Some initializations */
  n = 100;
  for (i=0; i < n; i++) {
      a[i] = rand(); a[i] /= RAND_MAX;
      b[i] = rand(); b[i] /= RAND_MAX;
  } 
  local_sum = 0.0;
  global_sum = 0.0;
  
#pragma omp parallel for reduction(+:local_sum)
  for (i=0; i < n; ++i)
    local_sum = local_sum + (a[i] * b[i]);

  MPI_Reduce(&local_sum, &global_sum, 1, MPI_FLOAT, MPI_SUM, 0, MPI_COMM_WORLD);

  if (!rank)
    printf("   Sum = %f\n", global_sum);

  MPI_Finalize();
  return 0;
}
