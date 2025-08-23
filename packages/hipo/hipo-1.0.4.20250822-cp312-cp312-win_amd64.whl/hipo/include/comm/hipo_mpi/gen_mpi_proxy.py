from clang import cindex
cindex.Config.set_library_path('/home/cax/software/LLVM-20.1.0-Linux-X64/lib')

from clang.cindex import *
import sys,re,os

from string import Template
import collections


# 创建一个索引
index = Index.create()

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('mpi_h_fn', type=str, help='mpi.h: e.g. /usr/include/x86_64-linux-gnu/mpich/mpi.h')
parser.add_argument('--sym_type', type=str, default='MPI_H', help='symbol table', choices=['INTERNAL', 'MPI_H', 'EXTERNAL'])
parser.add_argument('--sym_fn', type=str, help='external symbol table filename')

args = parser.parse_args()




mpi_symbols = """
MPI_Init
MPI_Finalize
MPI_Initialized
MPI_Finalized
MPI_Aint

MPI_Comm
MPI_Status
MPI_Datatype
MPI_Request
MPI_Op
MPI_Win
MPI_Info
MPI_Errhandler

MPI_Comm_copy_attr_function
MPI_Comm_delete_attr_function
MPI_Comm_errhandler_function
MPI_User_function

MPI_CHAR
MPI_BYTE
MPI_INT8_T

MPI_SHORT
MPI_SHORT_INT
MPI_INT16_T

MPI_INT
MPI_INT32_T

MPI_LONG
MPI_LONG_INT
MPI_INT64_T

MPI_FLOAT
MPI_DOUBLE
MPI_COMPLEX
MPI_DOUBLE_COMPLEX

MPI_SUM
MPI_MAX
MPI_MIN

MPI_COMM_WORLD
MPI_COMM_SELF
MPI_IN_INPLACE
MPI_STATUS_IGNORE
MPI_STATUSES_IGNORE
MPI_SUCCESS

MPI_Comm_dup
MPI_Comm_free

MPI_Comm_size
MPI_Comm_rank

MPI_Send
MPI_Recv
MPI_Bcast
MPI_Gather
MPI_Gatherv
MPI_Scatter
MPI_Scatterv

MPI_Allgather
MPI_Allgatherv
MPI_Alltoall
MPI_Alltoallv
MPI_Allreduce

MPI_Isend
MPI_Irecv
MPI_Iallreduce


MPI_Wait
MPI_Waitall
MPI_Waitsome

MPI_Type_get_extent
MPI_Type_contiguous
MPI_Type_free
MPI_Type_commit

MPI_Op_create
MPI_Op_free

MPI_Fint
MPI_Comm_c2f

MPI_DATATYPE_NULL

MPI_IN_PLACE
MPI_REQUEST_NULL


MPI_Get_processor_name
MPI_MAX_PROCESSOR_NAME

MPI_Group

MPI_Abort
MPI_Allgather
MPI_Allgatherv
MPI_Allreduce
MPI_Alltoall
MPI_Barrier
MPI_Bcast
MPI_Comm_create
MPI_Comm_dup
MPI_Comm_free
MPI_Comm_group
MPI_Comm_rank
MPI_Comm_size
MPI_Comm_split
MPI_Finalize
MPI_Gather
MPI_Gatherv
MPI_Get_address
MPI_Get_count
MPI_Group_free
MPI_Group_incl
MPI_Init
MPI_Iprobe
MPI_Irecv
MPI_Irsend
MPI_Isend
MPI_Op_create
MPI_Op_free
MPI_Probe
MPI_Recv
MPI_Recv_init
MPI_Reduce
MPI_Request_free
MPI_Scan
MPI_Scatter
MPI_Scatterv
MPI_Send
MPI_Send_init
MPI_Startall
MPI_Test
MPI_Testall
MPI_Type_commit
MPI_Type_contiguous
MPI_Type_create_hvector
MPI_Type_create_struct
MPI_Type_free
MPI_Type_vector
MPI_Wait
MPI_Waitall
MPI_Waitany
MPI_Wtick
MPI_Wtime


MPI_Comm_c2f

MPI_Abort
MPI_Accumulate
MPI_Allgather
MPI_Allgatherv
MPI_Allreduce
MPI_Alltoall
MPI_Alltoallv
MPI_Alltoallw
MPI_Barrier
MPI_Bcast
MPI_Bsend
MPI_Bsend_init
MPI_Cancel
MPI_Cart_coords
MPI_Cart_create
MPI_Cartdim_get
MPI_Cart_get
MPI_Cart_map
MPI_Cart_rank
MPI_Cart_shift
MPI_Cart_sub
MPI_Comm_accept
MPI_Comm_compare
MPI_Comm_connect
MPI_Comm_create
MPI_Comm_create_errhandler
MPI_Comm_create_keyval
MPI_Comm_delete_attr
MPI_Comm_disconnect
MPI_Comm_dup
MPI_Comm_free
MPI_Comm_free_keyval
MPI_Comm_get_attr
MPI_Comm_get_errhandler
MPI_Comm_get_name
MPI_Comm_group
MPI_Comm_rank
MPI_Comm_remote_group
MPI_Comm_remote_size
MPI_Comm_set_attr
MPI_Comm_set_errhandler
MPI_Comm_set_name
MPI_Comm_size
MPI_Comm_spawn
MPI_Comm_spawn_multiple
MPI_Comm_split
MPI_Comm_test_inter
MPI_Errhandler_free
MPI_Error_string
MPI_Exscan
MPI_Finalize
MPI_Gather
MPI_Gatherv
MPI_Get
MPI_Get_address
MPI_Get_count
MPI_Get_elements
MPI_Get_processor_name
MPI_Graph_create
MPI_Graphdims_get
MPI_Graph_get
MPI_Graph_map
MPI_Graph_neighbors
MPI_Graph_neighbors_count
MPI_Grequest_complete
MPI_Group_excl
MPI_Group_free
MPI_Group_incl
MPI_Group_range_excl
MPI_Group_range_incl
MPI_Group_rank
MPI_Group_size
MPI_Group_translate_ranks
MPI_Ibsend
MPI_Info_delete
MPI_Info_dup
MPI_Info_free
MPI_Info_get
MPI_Info_get_nkeys
MPI_Info_get_nthkey
MPI_Info_get_valuelen
MPI_Info_set
MPI_Init
MPI_Initialized
MPI_Intercomm_create
MPI_Intercomm_merge
MPI_Iprobe
MPI_Irecv
MPI_Irsend
MPI_Isend
MPI_Issend
MPI_Op_commutative
MPI_Op_create
MPI_Op_free
MPI_Pack
MPI_Pack_external
MPI_Pack_external_size
MPI_Pack_size
MPI_Probe
MPI_Put
MPI_Recv
MPI_Recv_init
MPI_Reduce
MPI_Reduce_local
MPI_Reduce_scatter
MPI_Request_free
MPI_Request_get_status
MPI_Rsend
MPI_Rsend_init
MPI_Scan
MPI_Scatter
MPI_Scatterv
MPI_Send
MPI_Send_init
MPI_Sendrecv
MPI_Sendrecv_replace
MPI_Ssend
MPI_Ssend_init
MPI_Start
MPI_Status_set_cancelled
MPI_Status_set_elements
MPI_Test
MPI_Test_cancelled
MPI_Topo_test
MPI_Type_commit
MPI_Type_contiguous
MPI_Type_create_darray
MPI_Type_create_hindexed
MPI_Type_create_hvector
MPI_Type_create_indexed_block
MPI_Type_create_resized
MPI_Type_create_struct
MPI_Type_create_subarray
MPI_Type_delete_attr
MPI_Type_dup
MPI_Type_free
MPI_Type_get_attr
MPI_Type_get_contents
MPI_Type_get_envelope
MPI_Type_get_extent
MPI_Type_get_name
MPI_Type_get_true_extent
MPI_Type_indexed
MPI_Type_set_attr
MPI_Type_set_name
MPI_Type_size
MPI_Type_vector
MPI_Unpack
MPI_Unpack_external
MPI_Wait
MPI_Waitall
MPI_Win_call_errhandler
MPI_Win_complete
MPI_Win_delete_attr
MPI_Win_fence
MPI_Win_get_errhandler
MPI_Win_get_group
MPI_Win_get_name
MPI_Win_lock
MPI_Win_post
MPI_Win_set_attr
MPI_Win_set_errhandler
MPI_Win_set_name
MPI_Win_start
MPI_Win_test
MPI_Win_unlock
MPI_Win_wait

MPI_Abort
MPI_Allreduce
MPI_Barrier
MPI_Bcast
MPI_Comm_create
MPI_Comm_dup
MPI_Comm_free
MPI_Comm_get_attr
MPI_Comm_group
MPI_Comm_rank
MPI_Comm_size
MPI_Comm_split
MPI_Error_class
MPI_File_close
MPI_File_get_size
MPI_File_open
MPI_File_preallocate
MPI_File_read_at
MPI_File_write_at
MPI_File_write_at_all
MPI_Group_free
MPI_Group_incl
MPI_Init
MPI_Initialized
MPI_Irecv
MPI_Isend
MPI_Op_create
MPI_Op_free
MPI_Pack
MPI_Pack_size
MPI_Recv
MPI_Reduce
MPI_Rsend
MPI_Send
MPI_Sendrecv
MPI_Testall
MPI_Type_commit
MPI_Type_create_struct
MPI_Type_free
MPI_Type_match_size
MPI_Type_vector
MPI_Waitall
MPI_Wtime


MPI_COMM_NULL
MPI_UNDEFINED
MPI_PACKED
MPI_IDENT
MPI_CONGRUENT
MPI_PROC_NULL
MPI_KEYVAL_INVALID
MPI_ERRHANDLER_NULL
MPI_MAX_ERROR_STRING
MPI_ERR_IN_STATUS
"""



skip_table = {
    'MPI_T_event.*',
    'MPI_Info_c2f',
    'MPI_Status_f082f',
    'MPI_Status_c2f08',
    'MPI_Status_f082c',
    'MPI_Status_f2f08',
    'MPI_FILE_DEFINED',
    'MPI_PROTO_H_INCLUDED',
    'MPIO_INCLUDE',
    'MPIO_USES_MPI_REQUEST',
    'MPIO_REQUEST_DEFINED',
    #'MPI_Errhandler_.*',
    'MPI_Errhandler_create',
    'MPI_Errhandler_get',
    'MPI_Errhandler_set',
    #'MPI_Info_.*',
    'MPI_Info_create_env',
    'MPI_Info_get_string',
    'MPI_Precv_init',
    'MPI_Psend_init',
    #'MPI_T_source.*',
    'MPI_T_source_order',
    'MPI_T_.*',
    'MPI_Session_.*',
    'MPI_Isendrecv',
    'MPI_Isendrecv_replace',
    'MPI_Type_(hvector|struct|hindexed|extent|ub|lb)',
    'MPI_Pready.*',
    #'MPI_.*_init',
    'MPI_(Alltoall|Alltoallv|Alltoallw|Allgatherv|Allgather|Allreduce|Barrier|Bcast|Exscan|Gather|Gatherv|Reduce|Scan|Scatter|Scatterv)_init',
    'MPI_Reduce_scatter_block_init',
    'MPI_Reduce_scatter_init',
    'MPI_Neighbor_.*_init',
    'MPI_Comm_idup_with_info',
    'MPI_Intercomm_create_from_groups',
    'MPI_Comm_create_from_group',
    'MPI_Address',
    'MPI_Parrived',
    'MPI_Group_from_session_pset',
    'MPI_F_STATUS_SIZE',
    'MPI_F_SOURCE',
    'MPI_F_ERROR',
    'MPI_ERR_SESSION',
    'MPI_ERR_PROC_ABORTED',
    'MPI_CONVERSION_FN_NULL_C',
    'MPIO_REQUEST_NULL',
    'MPI_ERR_VALUE_TOO_LARGE',
    'MPI_LB',
    'MPI_UB',
    'MPI_INTEGER16',
    'MPI_SESSION_NULL',
    'MPI_MAX_STRINGTAG_LEN',
    'MPI_MAX_PSET_NAME_LEN',
    'MPI_ERRORS_ABORT',
    'MPI_COMM_TYPE_HW_GUIDED',
    'MPI_COMM_TYPE_HW_UNGUIDED',
    'MPI_AINT_FMT_DEC_SPEC',
    'MPI_AINT_FMT_HEX_SPEC',
    'MPI_F_TAG',
    'MPI_INCLUDED',
    'MPI_VERSION',
    'MPI_SUBVERSION',
    #'MPIO_Request',
    'MPIO_Wait',
    'MPIO_Test',

    # openmpi 1.8.5
    'MPI_Aint_add',
    'MPI_Aint_diff',
    'MPI_File_iread_at_all',
    'MPI_File_iwrite_at_all',
    'MPI_File_iread_all',
    'MPI_File_iwrite_all',


    # openmpi 1.6.5
    'MPI_User_function_c',
    'MPI_Datarep_conversion_function_c',
    'MPI_MESSAGE_NULL',
    'MPI_MESSAGE_NO_PROC',
    'MPI_REAL16',
    'MPI_COMPLEX32',
    'MPI_COUNT',
    'MPI_CXX_BOOL',
    'MPI_CXX_FLOAT_COMPLEX',
    'MPI_CXX_DOUBLE_COMPLEX',
    'MPI_CXX_LONG_DOUBLE_COMPLEX',
    'MPI_NO_OP',
    'MPI_WIN_CREATE_FLAVOR',
    'MPI_WIN_MODEL',
    'MPI_MAX_LIBRARY_VERSION_STRING',
    'MPI_INFO_ENV',
    'MPI_COMM_TYPE_SHARED',
    'MPI_Message',
    'MPI_Message_c2f',
    'MPI_Message',
    'MPI_ERR_RMA_RANGE',
    'MPI_ERR_RMA_ATTACH',
    'MPI_ERR_RMA_SHARED',
    'MPI_ERR_RMA_FLAVOR',
    'MPI_Iallgather',
    'MPI_Iallgatherv',
    'MPI_Iallreduce',
    'MPI_Ialltoall',
    'MPI_Ialltoallv',
    'MPI_Ialltoallw',
    'MPI_Ibarrier',
    'MPI_Ibcast',
    'MPI_Iexscan',
    'MPI_Igather',
    'MPI_Igatherv',
    'MPI_Ineighbor_allgather',
    'MPI_Ineighbor_allgatherv',
    'MPI_Ineighbor_alltoall',
    'MPI_Ineighbor_alltoallv',
    'MPI_Ineighbor_alltoallw',
    'MPI_Ireduce',
    'MPI_Ireduce_scatter',
    'MPI_Ireduce_scatter_block',
    'MPI_Iscan',
    'MPI_Iscatter',
    'MPI_Iscatterv',
    'MPI_Neighbor_allgather',
    'MPI_Neighbor_allgatherv',
    'MPI_Neighbor_alltoall',
    'MPI_Neighbor_alltoallv',
    'MPI_Neighbor_alltoallw',
    'MPI_Reduce_scatter_block',
    'MPI_Comm_create_group',
    'MPI_Comm_dup_with_info',
    'MPI_Comm_get_info',
    'MPI_Comm_idup',
    'MPI_Comm_set_info',
    'MPI_Comm_split_type',
    'MPI_Count',
    'MPI_Get_elements_x',
    'MPI_Count',
    'MPI_Status_set_elements_x',
    'MPI_Type_create_hindexed_block',
    'MPI_Count',
    'MPI_Type_get_extent_x',
    'MPI_Count',
    'MPI_Type_get_true_extent_x',
    'MPI_Count',
    'MPI_Type_size_x',
    'MPI_Get_library_version',
    'MPI_Message',
    'MPI_Improbe',
    'MPI_Message',
    'MPI_Imrecv',
    'MPI_Message',
    'MPI_Mprobe',
    'MPI_Message',
    'MPI_Mrecv',
    'MPI_Compare_and_swap',
    'MPI_Fetch_and_op',
    'MPI_Get_accumulate',
    'MPI_Raccumulate',
    'MPI_Rget',
    'MPI_Rget_accumulate',
    'MPI_Rput',
    'MPI_Win_allocate',
    'MPI_Win_allocate_shared',
    'MPI_Win_attach',
    'MPI_Win_create_dynamic',
    'MPI_Win_detach',
    'MPI_Win_flush',
    'MPI_Win_flush_all',
    'MPI_Win_flush_local',
    'MPI_Win_flush_local_all',
    'MPI_Win_get_info',
    'MPI_Win_lock_all',
    'MPI_Win_set_info',
    'MPI_Win_shared_query',
    'MPI_Win_sync',
    'MPI_Win_unlock_all',
    'MPI_Dist_graph_create',
    'MPI_Dist_graph_create_adjacent',
    'MPI_Dist_graph_neighbors',
    'MPI_Dist_graph_neighbors_count',



}
def in_skip_table(skip_table, symbol):
    for skip in skip_table:
        if skip == symbol or re.search(skip, symbol):
            return True
    return False


macro_list = []

int32_macro_list = [
    'MPI_MAX_PROCESSOR_NAME',
    'MPI_MAX_ERROR_STRING',
    'MPI_KEYVAL_INVALID',
    'MPI_ERR_IN_STATUS',
    'MPI_SUCCESS',
    'MPI_UNDEFINED',
    'MPI_PROC_NULL',
    'MPI_IDENT',
    'MPI_CONGRUENT',
    'MPI_MODE_CREATE',
    'MPI_MODE_RDONLY',
    'MPI_MODE_APPEND',
    'MPI_MODE_WRONLY',
    'MPI_COMM_TYPE_SHARED',
    'MPI_ANY_SOURCE',
    'MPI_MODE_NOCHECK',
    'MPI_LOCK_SHARED',
    'MPI_LOCK_EXCLUSIVE',
    'MPI_SEEK_SET',
    'MPI_MODE_UNIQUE_OPEN',
]

int64_macro_list = [
]

f2c_c2f_list = [
    'MPI_Comm_c2f',
    'MPI_Comm_f2c',
    'MPI_Type_c2f',
    'MPI_Type_f2c',
    'MPI_Group_c2f',
    'MPI_Group_f2c',
    'MPI_Info_c2f',
    'MPI_Info_f2c',
    'MPI_Request_f2c',
    'MPI_Request_c2f',
    'MPI_Op_c2f',
    'MPI_Op_f2c',
    'MPI_Errhandler_c2f',
    'MPI_Errhandler_f2c',
    'MPI_Win_c2f',
    'MPI_Win_f2c',
    'MPI_Message_c2f',
    'MPI_Message_f2c',
    'MPI_Session_c2f',
    'MPI_Session_f2c',
]

data_type_list = [
    'MPI_CHAR',
    'MPI_BYTE',
    'MPI_INT8_T',
    'MPI_SHORT',
    'MPI_SHORT_INT',
    'MPI_INT16_T',
    'MPI_INT',
    'MPI_INT32_T',
    'MPI_LONG',
    'MPI_LONG_INT',
    'MPI_INT64_T',
    'MPI_FLOAT',
    'MPI_DOUBLE',
    'MPI_COMPLEX',
    'MPI_DOUBLE_COMPLEX',
    'MPI_PACKED',
]

implicit_type_list = [
    'MPI_Status',
    'MPI_Datatype',
    'MPI_Comm',
    'MPI_Op',
    'MPI_Group',
    'MPI_Win',
    'MPI_Info',
    'MPI_Errhandler',
    'MPI_Request',
    'MPI_Aint',
    'MPI_Fint',
    'MPI_File',
    'MPI_Offset',
    'MPI_T_source_order',
    'MPI_Count',
    'MPI_Session',
    'MPI_Message',
    'MPIO_Request',
]

function_decl_list = [
    'MPI_Comm_copy_attr_function',
    'MPI_Comm_delete_attr_function',
    'MPI_Comm_errhandler_function',
    'MPI_User_function',
    'MPI_Win_copy_attr_function',
    'MPI_Win_delete_attr_function',
    'MPI_Win_errhandler_function',
    'MPI_Session_errhandler_function',
    'MPI_Datarep_conversion_function',
    'MPI_Datarep_extent_function',
    'MPI_Grequest_query_function',
    'MPI_Grequest_free_function',
    'MPI_Grequest_cancel_function',
    'MPI_File_errhandler_function',
    'MPI_Type_copy_attr_function',
    'MPI_Type_delete_attr_function',
    'MPI_Copy_function',
    'MPI_Delete_function',

]

mpi_alltoallw_list = [
    'MPI_Alltoallw',
    'MPI_Alltoallw_init',
    'MPI_Ialltoallw',
    'MPI_Ialltoallw_init',
    'MPI_Neighbor_alltoallw',
    'MPI_Neighbor_alltoallw_init',
    'MPI_Ineighbor_alltoallw',
    'MPI_Ineighbor_alltoallw_init',
]

compatible_symbols = {
    'MPI_Address':'MPI_Get_address',
    'MPI_Errhandler_create': 'MPI_Comm_create_errhandler',
    'MPI_Errhandler_get': 'MPI_Comm_get_errhandler',
    'MPI_Errhandler_set': 'MPI_Comm_set_errhandler',
    'MPI_Type_struct': 'MPI_Type_create_struct',
    'MPI_Type_hvector': 'MPI_Type_create_hvector',
    'MPI_Type_hindexed': 'MPI_Type_create_hindexed',
    'MPI_Type_extent': 'MPI_Type_create_extent',
    'MPI_Type_lb': 'MPI_Type_create_lb',
    'MPI_Type_ub': 'MPI_Type_create_ub',

    'MPI_Attr_delete': 'MPI_Comm_delete_attr',
    'MPI_Attr_get': 'MPI_Comm_get_attr',
    'MPI_Attr_put': 'MPI_Comm_set_attr',
    'MPI_Keyval_create': 'MPI_Comm_create_keyval',
    'MPI_Keyval_free': 'MPI_Comm_free_keyval',
}


void_star_type_list = []
for v in implicit_type_list:
    if v not in ['MPI_Aint', 'MPI_Status', 'MPI_T_source_order', 'MPI_Count', 'MPI_Offset', 'MPI_Fint']:
        void_star_type_list.append(v)


value_in_arg_list = implicit_type_list + [f'{v} *' for v in function_decl_list] + ['const MPI_Fint *']

value_out_arg_list = [f'{v} *' for v in implicit_type_list]

array_in_arg_list = [f'const {v}[]' for v in implicit_type_list]

array_out_arg_list = [f'{v}[]' for v in implicit_type_list]


print(f'implicit_type_list {implicit_type_list}')
print(f'void_star_type_list {void_star_type_list}')
print(f'value_in_arg_list {value_in_arg_list}')
print(f'value_out_arg_list {value_out_arg_list}')
print(f'array_in_arg_list {array_in_arg_list}')
print(f'array_out_arg_list {array_out_arg_list}')


class CodeBlock:
    macro_as_function = Template('''
hipo_${from_type} hipo_${varname}_CONST() {
#if !defined(DISABLE_${varname}) && !defined(HIPO_MPI_DUMMY_IMPL)
    ${from_type} ret = ${varname};
    hipo_${from_type} hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}
''')
    macro_as_function_simple = Template("""
${macro_type} hipo_${varname}_CONST() {
#if !defined(DISABLE_${varname}) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (${macro_type})(${varname});
#else
    return 0;
#endif
}
""")
    mpi_c2f = Template("""
hipo_MPI_Fint hipo_${c_type}_c2f(hipo_${d_type} ${varname}) {
#if !defined(DISABLE_${c_type}_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    ${d_type} ${varname}_in;
    copyValue(${varname}_in, ${varname});
    MPI_Fint ret = ${c_type}_c2f(${varname}_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}
""")
    mpi_f2c = Template("""
hipo_${d_type} hipo_${c_type}_f2c(hipo_MPI_Fint ${varname}) {
#if !defined(DISABLE_${c_type}_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint ${varname}_in;
    copyValue(${varname}_in, ${varname});
    ${d_type} ret = ${c_type}_f2c(${varname}_in);
    hipo_${d_type} hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}
""")
    mpi_status_input = Template('''
    ${to_type} ${varname}_data;
    ${to_type}* ${varname}_in = MPI_STATUS_IGNORE;
    if (${varname} != hipo_MPI_STATUS_IGNORE) {
        ${varname}_in = &${varname}_data;
        copyValue(${varname}_in, ${varname});
    }
''')
    mpi_status_output = Template('''
    if (${varname} != hipo_MPI_STATUS_IGNORE) {
        copyValue(${varname}, ${varname}_in);
    }
''')
    array_type_input = Template('''
    ${to_type} ${varname}_in[${cntname}];
    for (int i=0; i<${cntname}; i++) {
        copyValue(${varname}_in[i], ${varname}[i]);
    }
''')
    array_type_output = Template('''
    for (int i=0; i<${cntname}; i++) {
        copyValue(${varname}[i], ${varname}_in[i]);
    }
''')
    body = Template('''
{
#if !defined(DISABLE_${func_name}) && !defined(HIPO_MPI_DUMMY_IMPL)
${copy_in}    ${ret_type} ret = ${func_name}(${call});
${copy_out}
${return_stat}
#else
    printf("error: ${func_name} is a dummy function\\n");
    return 0;
#endif
}''')


script_dir = os.path.dirname(os.path.abspath(__file__))

print(f'script_dir is {script_dir}')

# 解析文件
tu = index.parse(
    args.mpi_h_fn,
    args=f'-I/usr/include/ -DOMPI_DECLSPEC'.split(),
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
)

def getAllSymbols(tu):
    sym_dic = collections.OrderedDict()
    for node in tu.cursor.get_children():
        name = node.spelling
        if name.startswith('MPI_') or name.startswith('MPIO_'):
            if not in_skip_table(skip_table, name):
                sym_dic[name] = 1
    return sym_dic


def test():
    assert in_skip_table(skip_table, 'MPI_T_source_order') == True


test()

def sym_split(str):
    sym_table = collections.OrderedDict()
    for sym in re.split(r'[\n \t]+', str, 0, re.MULTILINE):
            if len(sym) > 0:
                sym_table[sym] = 1
    return sym_table

if args.sym_type == 'INTERNAL':
    sym_table = sym_split(mpi_symbols)
elif args.sym_type == 'MPI_H':
    sym_table = getAllSymbols(tu)
elif args.sym_type == 'EXTERNAL':
    with open(args.sym_fn) as fn:
        sym_table = sym_split(fn.read())



for v in data_type_list + implicit_type_list:
    if not in_skip_table(skip_table,v):
        sym_table[v] = 1

print(f'sym_table {len(sym_table)}')


root_node = tu.cursor

hpp_data = ''
hpp_macro_data = ''
cpp_data = ''


# 打印节点的类型和位置
#print(f"top node {node.kind}: {node.displayname} at {location}")
#g_tokens = None

def get_token_string(node):
    tokens = []
    # if node.spelling == 'MPI_Status':
    #     #global g_tokens
    #     #g_tokens = list(node.get_tokens())
    #     for idx, token in enumerate(node.get_tokens()):
    #         pass
    #         #print('token ', idx, vars(token))
    for token in node.get_tokens():
        #if token.kind != TokenKind.REF:
        #if (token.extent.start.line >= node.location.line):
            tokens.append(token.spelling)
        #else:
        #    print (token.kind)
    return ' '.join(tokens)

def get_child(node, i):
    return list(node.get_children())[i]

kinds = {}

output_symbols = collections.OrderedDict()


class ConstCast:
    def __init__(self, typename):
        self.typename = typename
        self.const_tag = re.search(r'const.*', typename)
        const_cast_type = re.sub(r'const (\S+) \*', r'\1', typename)
        #print(f'const_cast_type is {const_cast_type} param type {typename}')
        if const_cast_type == typename:
            const_cast_type = re.sub(r'const (\S+)\[\]', r'\1', typename)
        self.const_cast_type = const_cast_type

    def cast_varname(self, varname):
        if self.const_tag and self.const_cast_type in ['void', 'char', 'int', 'MPI_Fint']:
            return f'const_cast<{self.const_cast_type}*>({varname})'
        else:
            return varname


assert root_node.kind == CursorKind.TRANSLATION_UNIT
if True:
    for node in root_node.get_children():
        
        print(f"CHECK {node.kind}: {node.spelling}, {node.displayname} num children {len(list(node.get_children()))} tokens ")

        # nodename = node.spelling.lower()
        # if not (nodename.startswith('mpi_') or nodename.startswith('mpio_')):
        #     continue

        # if in_skip_table(node.spelling):
        #     continue

        if node.spelling not in sym_table or sym_table[node.spelling] == 0:
            continue
        #sym_table[node.spelling] = 1


        type_name = node.spelling
        if type_name not in output_symbols:
            output_symbols[type_name] = 0
        output_symbols[type_name] += 1

        if output_symbols[type_name] > 1 and type_name in ['MPIO_Request']:
            continue



        #print(f"    {node.kind}: {node.spelling}, {node.displayname}")
        if node.kind not in kinds:
            kinds[node.kind] = 0
        kinds[node.kind] += 1
        #continue
        #if node.spelling in sym_table:
        if True:
            #sym_table[node.spelling] = 0
            tokens = get_token_string(node)
            fname = node.spelling
            tokens = re.sub(r'\bMPI_', 'hipo_MPI_', tokens)
            tokens = re.sub(r'\bMPIO_', 'hipo_MPIO_', tokens)
            
           


            # if node.spelling == 'MPI_Datatype':
            #     print('stop', tokens)
            #     break
            body = ''
            
            if node.kind == CursorKind.MACRO_INSTANTIATION or node.kind == CursorKind.MACRO_DEFINITION:
                if node.spelling in ['MPIO_Request']:
                    hpp_data += 'typedef void* hipo_MPIO_Request;\n'
                    continue
                
                if node.spelling in f2c_c2f_list:
                    #continue
                    c_type = re.sub('_f2c|_c2f', '', node.spelling)
                    varname = re.sub('MPI_', '', c_type).lower()
                    d_type = c_type
                    if c_type == 'MPI_Type':
                        d_type = 'MPI_Datatype'
                    if node.spelling.endswith('_c2f'):
                        hpp_macro_data += f"hipo_MPI_Fint hipo_{c_type}_c2f(hipo_{d_type} {varname});\n"
                        cpp_data += CodeBlock.mpi_c2f.substitute(varname = varname, c_type = c_type, d_type = d_type)
                    if node.spelling.endswith('_f2c'):
                        hpp_macro_data += f"hipo_{d_type} hipo_{c_type}_f2c(hipo_MPI_Fint {varname});\n"
                        cpp_data += CodeBlock.mpi_f2c.substitute(varname = varname, c_type = c_type, d_type = d_type)
                    continue

            if node.kind == CursorKind.MACRO_DEFINITION:
                if node.spelling in ['MPI_INCLUDED']:
                    continue

                macro_type = 'void*'
                if node.spelling in ['MPI_STATUSES_IGNORE', 'MPI_STATUS_IGNORE']:
                    macro_type = 'hipo_MPI_Status*'

                elif node.spelling in ['MPI_REQUEST_NULL']:
                    macro_type = 'hipo_MPI_Request'
                
                elif node.spelling in ['MPI_DATATYPE_NULL']:
                    macro_type = 'hipo_MPI_Datatype'
                
                elif node.spelling in ['MPI_COMM_WORLD', 'MPI_COMM_SELF', 'MPI_COMM_NULL']:
                    macro_type = 'hipo_MPI_Comm'

                elif node.spelling in ['MPI_ERRHANDLER_NULL']:
                    macro_type = 'hipo_MPI_Errhandler'

                elif node.spelling in int64_macro_list:
                    macro_type = 'int64_t'

                elif node.spelling in int32_macro_list:
                    macro_type = 'int'

                elif node.spelling in ['MPI_MAX', 'MPI_MIN', 'MPI_SUM']:
                    macro_type = 'hipo_MPI_Op'

                elif node.spelling in data_type_list:
                    macro_type = 'hipo_MPI_Datatype'

                elif node.spelling in ['MPI_COMM_NULL_DELETE_FN']:
                    macro_type = 'hipo_MPI_Comm_delete_attr_function*'

                elif node.spelling in ['MPI_COMM_DUP_FN']:
                    macro_type = 'hipo_MPI_Comm_copy_attr_function*'
                
                elif node.spelling.upper() != node.spelling:
                    print(f"macro section: warning : {node.spelling} is not capitalized")

                #print(f"       {node.kind}: {node.spelling}, {node.displayname} num children {len(list(node.get_children()))} tokens {tokens}")
                #hpp_data += "#define " + tokens + "\n"
                from_type = re.sub('hipo_', '', macro_type)
                if from_type != macro_type:
                    cpp_data += CodeBlock.macro_as_function.substitute(from_type=from_type, varname = node.spelling)
                else:
                    #cpp_data += f'{macro_type} hipo_{node.spelling}_CONST() ' + '{' + f' return ({macro_type})({node.spelling});' + '}\n'
                    cpp_data += CodeBlock.macro_as_function_simple.substitute(macro_type=macro_type, varname=node.spelling)
                    pass
                if node.spelling == 'MPI_MAX_PROCESSOR_NAME':
                    hpp_data += f'#define hipo_{node.spelling} 256\n'
                    hpp_macro_data += f'{macro_type} hipo_{node.spelling}_CONST();\n'
                    continue
                hpp_macro_data += f'{macro_type} hipo_{node.spelling}_CONST();\n'
                hpp_data += f'#define hipo_{node.spelling} hipo_{node.spelling}_CONST()\n'
                continue

            elif node.kind == CursorKind.TYPEDEF_DECL:
                #if len(list(node.get_children())) == 1:
                if node.spelling == 'MPI_Status':
                    tokens = re.sub(r'\bhipo_MPI_(SOURCE|TAG|ERROR)', r'MPI_\1', tokens)
                    tokens = re.sub(r'int count_lo ; int count_hi_and_cancelled ;', '', tokens)
                
                if node.spelling in void_star_type_list:
                    hpp_data += f'typedef void* hipo_{node.spelling};\n'
                else:
                    hpp_data += tokens + ';\n'
                continue

            elif node.kind == CursorKind.FUNCTION_DECL:
               
                # if node.spelling == 'MPI_Allgather':
                #    print('stop', tokens)
                #    break
                
                #args = get_token_string(node)
                args = tokens
                fname = node.spelling

                if re.match(r'.*_c$', fname):
                    continue
                
                
                #args = re.sub(r'^MPI_', 'hipo_MPI_', args)
                
                calllist = []
                decl = ''
                retu = ''
                nodes = list(node.get_children())
                if node.spelling in mpi_alltoallw_list:
                    decl += '    int nprocs;\n    hipo_MPI_Comm_size(comm, &nprocs);\n'
                for idx, i in enumerate(nodes):
                    if i.kind == CursorKind.PARM_DECL:
                        
                        const_cast = ConstCast(i.type.spelling)

                        if i.type.spelling in ['MPI_Status *', 'const MPI_Status *']:
                            to_type = re.sub(r'.*(MPI_Status).*', r'\1', i.type.spelling)
                            from_type = f'hipo_{to_type}'
                            decl += CodeBlock.mpi_status_input.substitute(to_type=to_type, from_type=from_type, varname=i.spelling)
                            
                            calllist.append(f'{i.spelling}_in')
                            if not const_cast.const_tag:
                                retu += CodeBlock.mpi_status_output.substitute(to_type=to_type, from_type=from_type, varname=i.spelling)
                        elif i.type.spelling in value_in_arg_list:
                            decl += f'    {i.type.spelling} {i.spelling}_in;\n    copyValue({i.spelling}_in, {i.spelling});\n'
                            calllist.append(const_cast.cast_varname(f'{i.spelling}_in'))
                        elif i.type.spelling in value_out_arg_list:
                            to_type = re.sub(r' \*', '', i.type.spelling)
                            from_type = f'hipo_{to_type}'
                            decl += f'    {to_type} {i.spelling}_in;\n    copyValue({i.spelling}_in, *{i.spelling});\n'
                            calllist.append(f'&{i.spelling}_in')
                            retu += f'    copyValue(*{i.spelling}, {i.spelling}_in);\n'
                        
                        elif i.type.spelling in array_in_arg_list + array_out_arg_list:
                            cntname = nodes[0].spelling
                            if node.spelling in mpi_alltoallw_list:
                                cntname = 'nprocs'
                            if node.spelling in ['MPI_Type_get_contents']:
                                cntname = re.sub('array_of_', 'max_', i.spelling)
                            print('the array type is ', i.type.spelling)
                            to_type = re.sub(r'.*(MPI_.*)\[\]', r'\1', i.type.spelling)
                            from_type = f'hipo_{to_type}'
                            
                            decl += CodeBlock.array_type_input.substitute(to_type=to_type, cntname = cntname, varname = i.spelling)
                            calllist.append(f'{i.spelling}_in')
                            if const_cast.const_tag or (node.spelling in ['MPI_Wait', 'MPI_Waitany', 'MPI_Waitall', 'MPI_Waitsome'] and to_type == 'MPI_Request'):
                                pass
                            else:
                                retu += CodeBlock.array_type_output.substitute(from_type=from_type, cntname = cntname, varname = i.spelling)
                        else:
                            calllist.append(const_cast.cast_varname(f'{i.spelling}'))
                # for i in list(node.get_arguments()):
                #     val = i.spelling
                #     if val == 'comm':
                #         val = f'(MPI_Comm){val}'
                #     elif val == 'newcomm':
                #         val = f'(MPI_Comm*){val}'
                #     elif val in ['datatype', 'sendtype', 'recvtype']:
                #         val = f'(MPI_Datatype){val}'
                #     elif val == 'request':
                #         val = f'(MPI_Request*){val}'
                    
                #     calllist.append(val)
                call = ', '.join(calllist)


                ret_type = node.result_type.spelling
                if ret_type in implicit_type_list:
                    return_stat = f'    hipo_{ret_type} ret_out;\n    copyValue(ret_out, ret);\n    return ret_out;'
                else:
                    return_stat = f'    return ret;'
                
                #body = '\n{\n' + decl + f'    {ret_type} ret = {node.spelling}({call});\n{retu}\n{return_stat}\n' + '}'
                body = CodeBlock.body.substitute(copy_in=decl, ret_type=ret_type, 
                                                func_name =node.spelling, call=call,
                                                copy_out=retu, return_stat=return_stat)
                
                #outdata += f'inline {node.result_type.spelling} {node.spelling}({args_str}) ' + body + '\n'
                hpp_data += args + ';\n'
                cpp_data += args + body + '\n'
                continue
            else:
                continue


hpp_header = '''
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

'''

hpp_footer = """
#ifdef __cplusplus
}
#endif
"""

cpp_header = '''
#include "hipo_mpi.hpp"
#include <stdio.h>
#include <stdint.h>

#if !defined(HIPO_MPI_DUMMY_IMPL)
#include <mpi.h>

namespace {
template <class T1, class T2>
void copyValue(T1& to, const T2& from) {
    to = (T1)from;
}

template <class T>
void copyValue(int& to, T* from) {
    to = (int)(uint64_t)from;
}

template <class T>
void copyValue(int& to, const T* from) {
    to = (int)(uint64_t)from;
}

template <class T>
void copyValue(T*& to,  int from) {
    to = (T*)(uint64_t)from;
}

void copyValue(MPI_Status& stat, const hipo_MPI_Status& hipo_stat) {
    stat.MPI_SOURCE = hipo_stat.MPI_SOURCE;
    stat.MPI_TAG = hipo_stat.MPI_TAG;
    stat.MPI_ERROR = hipo_stat.MPI_ERROR;
}

void copyValue(hipo_MPI_Status& hipo_stat, const MPI_Status& stat) {
    hipo_stat.MPI_SOURCE = stat.MPI_SOURCE;
    hipo_stat.MPI_TAG = stat.MPI_TAG;
    hipo_stat.MPI_ERROR = stat.MPI_ERROR;
}
}

#endif

'''


hpp_header += "#ifdef HIPO_MPI_IMPORTS\n"
for sym, val in sym_table.items():
    if val > 0:
        hpp_header += f'#define {sym} hipo_{sym}\n'


# MPI_Type_(hvector|struct|hindexed|extent|ub|lb
for sym, sym_new in compatible_symbols.items():
    if sym not in sym_table:
        hpp_header += f'#define {sym} hipo_{sym_new}\n'

hpp_header += "#endif\n"

hpp_src = hpp_header + hpp_data + hpp_macro_data + hpp_footer
cpp_src = cpp_header + cpp_data


print('kinds', kinds)

with open('hipo_mpi_symbols.txt', 'w') as fp:
    for sym in sym_table:
        fp.write(sym + "\n")

with open('hipo_mpi.hpp', 'w') as fp:
    fp.write(hpp_src)

with open('hipo_mpi.cpp', 'w') as fp:
    fp.write(cpp_src)



