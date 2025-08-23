cmake_minimum_required(VERSION 3.10)

project(hipo_mpi C CXX)

set(LIB_NAME hipo_mpi)

add_library(${LIB_NAME} SHARED include/hipo_mpi.cpp)

if (ENABLE_MPI)

  set(USE_MPI TRUE)

  file(GLOB MPI_INCLUDE_DIRS
    ${MPI_PATH}/include
    ${MPI_PATH}/Include
  )
  file(GLOB MPI_LIBRARIES
    ${MPI_PATH}/lib/libmpi.so*
    ${MPI_PATH}/Lib/x64/msmpi.lib
  )
  file(GLOB MPI_BINARIES
    ${MPI_PATH}/bin/mpiexec.hydra
    ${MPI_PATH}/bin/hydra_pmi_proxy
    ${MPI_PATH}/Bin/mpiexec
  )
  message("MPI is ${MPI_PATH} ${MPI_INCLUDE_DIRS} ${MPI_LIBRARIES}")

else ()
  set_target_properties(${LIB_NAME} PROPERTIES COMPILE_FLAGS "-DHIPO_MPI_DUMMY_IMPL")
endif ()


target_include_directories(${LIB_NAME} PUBLIC ${MPI_INCLUDE_DIRS})
target_link_libraries(${LIB_NAME} ${MPI_LIBRARIES})

install(FILES ${MPI_LIBRARIES} DESTINATION lib)
install(FILES ${MPI_BINARIES} DESTINATION bin)


if (UNIX)
  set_target_properties(${LIB_NAME} PROPERTIES
      LINK_FLAGS "-Wl,-z,defs,--as-needed,-rpath,\$ORIGIN:\$ORIGIN/lib:\$ORIGIN/../lib"
  )
endif ()

install(DIRECTORY include/ DESTINATION include)
install(FILES CMakeLists.txt DESTINATION .)
install(TARGETS ${LIB_NAME} DESTINATION lib)
