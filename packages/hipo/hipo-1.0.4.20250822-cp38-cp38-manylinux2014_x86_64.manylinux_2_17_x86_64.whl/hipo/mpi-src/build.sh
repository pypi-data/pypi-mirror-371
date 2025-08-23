#g++ hipo_mpi.cpp -o libhipo_mpi.so -shared -fPIC -fno-rtti -fno-exceptions -DHIPO_MPI_DUMMY_IMPL
mpicxx hipo_mpi.cpp -o libhipo_mpi.so -shared -O3 -fPIC -fno-rtti -fno-exceptions
