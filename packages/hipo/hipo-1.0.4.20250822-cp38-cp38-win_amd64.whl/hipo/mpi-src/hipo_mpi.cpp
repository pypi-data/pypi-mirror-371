
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


hipo_MPI_Comm hipo_MPI_COMM_NULL_CONST() {
#if !defined(DISABLE_MPI_COMM_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm ret = MPI_COMM_NULL;
    hipo_MPI_Comm hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_OP_NULL_CONST() {
#if !defined(DISABLE_MPI_OP_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_OP_NULL);
#else
    return 0;
#endif
}

void* hipo_MPI_GROUP_NULL_CONST() {
#if !defined(DISABLE_MPI_GROUP_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_GROUP_NULL);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_DATATYPE_NULL_CONST() {
#if !defined(DISABLE_MPI_DATATYPE_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_DATATYPE_NULL;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Request hipo_MPI_REQUEST_NULL_CONST() {
#if !defined(DISABLE_MPI_REQUEST_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request ret = MPI_REQUEST_NULL;
    hipo_MPI_Request hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Errhandler hipo_MPI_ERRHANDLER_NULL_CONST() {
#if !defined(DISABLE_MPI_ERRHANDLER_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Errhandler ret = MPI_ERRHANDLER_NULL;
    hipo_MPI_Errhandler hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

int hipo_MPI_IDENT_CONST() {
#if !defined(DISABLE_MPI_IDENT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_IDENT);
#else
    return 0;
#endif
}

int hipo_MPI_CONGRUENT_CONST() {
#if !defined(DISABLE_MPI_CONGRUENT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_CONGRUENT);
#else
    return 0;
#endif
}

void* hipo_MPI_SIMILAR_CONST() {
#if !defined(DISABLE_MPI_SIMILAR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_SIMILAR);
#else
    return 0;
#endif
}

void* hipo_MPI_UNEQUAL_CONST() {
#if !defined(DISABLE_MPI_UNEQUAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNEQUAL);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_CHAR_CONST() {
#if !defined(DISABLE_MPI_CHAR) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_CHAR;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_SIGNED_CHAR_CONST() {
#if !defined(DISABLE_MPI_SIGNED_CHAR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_SIGNED_CHAR);
#else
    return 0;
#endif
}

void* hipo_MPI_UNSIGNED_CHAR_CONST() {
#if !defined(DISABLE_MPI_UNSIGNED_CHAR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNSIGNED_CHAR);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_BYTE_CONST() {
#if !defined(DISABLE_MPI_BYTE) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_BYTE;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_WCHAR_CONST() {
#if !defined(DISABLE_MPI_WCHAR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WCHAR);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_SHORT_CONST() {
#if !defined(DISABLE_MPI_SHORT) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_SHORT;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_UNSIGNED_SHORT_CONST() {
#if !defined(DISABLE_MPI_UNSIGNED_SHORT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNSIGNED_SHORT);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_INT_CONST() {
#if !defined(DISABLE_MPI_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_INT;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_UNSIGNED_CONST() {
#if !defined(DISABLE_MPI_UNSIGNED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNSIGNED);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_LONG_CONST() {
#if !defined(DISABLE_MPI_LONG) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_LONG;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_UNSIGNED_LONG_CONST() {
#if !defined(DISABLE_MPI_UNSIGNED_LONG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNSIGNED_LONG);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_FLOAT_CONST() {
#if !defined(DISABLE_MPI_FLOAT) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_FLOAT;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_DOUBLE_CONST() {
#if !defined(DISABLE_MPI_DOUBLE) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_DOUBLE;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_LONG_DOUBLE_CONST() {
#if !defined(DISABLE_MPI_LONG_DOUBLE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LONG_DOUBLE);
#else
    return 0;
#endif
}

void* hipo_MPI_LONG_LONG_INT_CONST() {
#if !defined(DISABLE_MPI_LONG_LONG_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LONG_LONG_INT);
#else
    return 0;
#endif
}

void* hipo_MPI_UNSIGNED_LONG_LONG_CONST() {
#if !defined(DISABLE_MPI_UNSIGNED_LONG_LONG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNSIGNED_LONG_LONG);
#else
    return 0;
#endif
}

void* hipo_MPI_LONG_LONG_CONST() {
#if !defined(DISABLE_MPI_LONG_LONG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LONG_LONG);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_PACKED_CONST() {
#if !defined(DISABLE_MPI_PACKED) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_PACKED;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_FLOAT_INT_CONST() {
#if !defined(DISABLE_MPI_FLOAT_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_FLOAT_INT);
#else
    return 0;
#endif
}

void* hipo_MPI_DOUBLE_INT_CONST() {
#if !defined(DISABLE_MPI_DOUBLE_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DOUBLE_INT);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_LONG_INT_CONST() {
#if !defined(DISABLE_MPI_LONG_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_LONG_INT;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_SHORT_INT_CONST() {
#if !defined(DISABLE_MPI_SHORT_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_SHORT_INT;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_2INT_CONST() {
#if !defined(DISABLE_MPI_2INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_2INT);
#else
    return 0;
#endif
}

void* hipo_MPI_LONG_DOUBLE_INT_CONST() {
#if !defined(DISABLE_MPI_LONG_DOUBLE_INT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LONG_DOUBLE_INT);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_COMPLEX;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_DOUBLE_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_DOUBLE_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_DOUBLE_COMPLEX;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_LOGICAL_CONST() {
#if !defined(DISABLE_MPI_LOGICAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LOGICAL);
#else
    return 0;
#endif
}

void* hipo_MPI_REAL_CONST() {
#if !defined(DISABLE_MPI_REAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_REAL);
#else
    return 0;
#endif
}

void* hipo_MPI_DOUBLE_PRECISION_CONST() {
#if !defined(DISABLE_MPI_DOUBLE_PRECISION) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DOUBLE_PRECISION);
#else
    return 0;
#endif
}

void* hipo_MPI_INTEGER_CONST() {
#if !defined(DISABLE_MPI_INTEGER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INTEGER);
#else
    return 0;
#endif
}

void* hipo_MPI_2INTEGER_CONST() {
#if !defined(DISABLE_MPI_2INTEGER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_2INTEGER);
#else
    return 0;
#endif
}

void* hipo_MPI_2REAL_CONST() {
#if !defined(DISABLE_MPI_2REAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_2REAL);
#else
    return 0;
#endif
}

void* hipo_MPI_2DOUBLE_PRECISION_CONST() {
#if !defined(DISABLE_MPI_2DOUBLE_PRECISION) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_2DOUBLE_PRECISION);
#else
    return 0;
#endif
}

void* hipo_MPI_CHARACTER_CONST() {
#if !defined(DISABLE_MPI_CHARACTER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_CHARACTER);
#else
    return 0;
#endif
}

void* hipo_MPI_REAL4_CONST() {
#if !defined(DISABLE_MPI_REAL4) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_REAL4);
#else
    return 0;
#endif
}

void* hipo_MPI_REAL8_CONST() {
#if !defined(DISABLE_MPI_REAL8) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_REAL8);
#else
    return 0;
#endif
}

void* hipo_MPI_COMPLEX8_CONST() {
#if !defined(DISABLE_MPI_COMPLEX8) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_COMPLEX8);
#else
    return 0;
#endif
}

void* hipo_MPI_COMPLEX16_CONST() {
#if !defined(DISABLE_MPI_COMPLEX16) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_COMPLEX16);
#else
    return 0;
#endif
}

void* hipo_MPI_INTEGER1_CONST() {
#if !defined(DISABLE_MPI_INTEGER1) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INTEGER1);
#else
    return 0;
#endif
}

void* hipo_MPI_INTEGER2_CONST() {
#if !defined(DISABLE_MPI_INTEGER2) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INTEGER2);
#else
    return 0;
#endif
}

void* hipo_MPI_INTEGER4_CONST() {
#if !defined(DISABLE_MPI_INTEGER4) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INTEGER4);
#else
    return 0;
#endif
}

void* hipo_MPI_INTEGER8_CONST() {
#if !defined(DISABLE_MPI_INTEGER8) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INTEGER8);
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_INT8_T_CONST() {
#if !defined(DISABLE_MPI_INT8_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_INT8_T;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_INT16_T_CONST() {
#if !defined(DISABLE_MPI_INT16_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_INT16_T;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_INT32_T_CONST() {
#if !defined(DISABLE_MPI_INT32_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_INT32_T;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_INT64_T_CONST() {
#if !defined(DISABLE_MPI_INT64_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype ret = MPI_INT64_T;
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_UINT8_T_CONST() {
#if !defined(DISABLE_MPI_UINT8_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UINT8_T);
#else
    return 0;
#endif
}

void* hipo_MPI_UINT16_T_CONST() {
#if !defined(DISABLE_MPI_UINT16_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UINT16_T);
#else
    return 0;
#endif
}

void* hipo_MPI_UINT32_T_CONST() {
#if !defined(DISABLE_MPI_UINT32_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UINT32_T);
#else
    return 0;
#endif
}

void* hipo_MPI_UINT64_T_CONST() {
#if !defined(DISABLE_MPI_UINT64_T) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UINT64_T);
#else
    return 0;
#endif
}

void* hipo_MPI_C_BOOL_CONST() {
#if !defined(DISABLE_MPI_C_BOOL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_C_BOOL);
#else
    return 0;
#endif
}

void* hipo_MPI_C_FLOAT_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_C_FLOAT_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_C_FLOAT_COMPLEX);
#else
    return 0;
#endif
}

void* hipo_MPI_C_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_C_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_C_COMPLEX);
#else
    return 0;
#endif
}

void* hipo_MPI_C_DOUBLE_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_C_DOUBLE_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_C_DOUBLE_COMPLEX);
#else
    return 0;
#endif
}

void* hipo_MPI_C_LONG_DOUBLE_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_C_LONG_DOUBLE_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_C_LONG_DOUBLE_COMPLEX);
#else
    return 0;
#endif
}

void* hipo_MPI_AINT_CONST() {
#if !defined(DISABLE_MPI_AINT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_AINT);
#else
    return 0;
#endif
}

void* hipo_MPI_OFFSET_CONST() {
#if !defined(DISABLE_MPI_OFFSET) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_OFFSET);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPECLASS_REAL_CONST() {
#if !defined(DISABLE_MPI_TYPECLASS_REAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPECLASS_REAL);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPECLASS_INTEGER_CONST() {
#if !defined(DISABLE_MPI_TYPECLASS_INTEGER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPECLASS_INTEGER);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPECLASS_COMPLEX_CONST() {
#if !defined(DISABLE_MPI_TYPECLASS_COMPLEX) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPECLASS_COMPLEX);
#else
    return 0;
#endif
}

hipo_MPI_Comm hipo_MPI_COMM_WORLD_CONST() {
#if !defined(DISABLE_MPI_COMM_WORLD) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm ret = MPI_COMM_WORLD;
    hipo_MPI_Comm hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Comm hipo_MPI_COMM_SELF_CONST() {
#if !defined(DISABLE_MPI_COMM_SELF) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm ret = MPI_COMM_SELF;
    hipo_MPI_Comm hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_GROUP_EMPTY_CONST() {
#if !defined(DISABLE_MPI_GROUP_EMPTY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_GROUP_EMPTY);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_NULL_CONST() {
#if !defined(DISABLE_MPI_WIN_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_NULL);
#else
    return 0;
#endif
}

void* hipo_MPI_FILE_NULL_CONST() {
#if !defined(DISABLE_MPI_FILE_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_FILE_NULL);
#else
    return 0;
#endif
}

hipo_MPI_Op hipo_MPI_MAX_CONST() {
#if !defined(DISABLE_MPI_MAX) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op ret = MPI_MAX;
    hipo_MPI_Op hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Op hipo_MPI_MIN_CONST() {
#if !defined(DISABLE_MPI_MIN) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op ret = MPI_MIN;
    hipo_MPI_Op hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Op hipo_MPI_SUM_CONST() {
#if !defined(DISABLE_MPI_SUM) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op ret = MPI_SUM;
    hipo_MPI_Op hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_PROD_CONST() {
#if !defined(DISABLE_MPI_PROD) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_PROD);
#else
    return 0;
#endif
}

void* hipo_MPI_LAND_CONST() {
#if !defined(DISABLE_MPI_LAND) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LAND);
#else
    return 0;
#endif
}

void* hipo_MPI_BAND_CONST() {
#if !defined(DISABLE_MPI_BAND) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_BAND);
#else
    return 0;
#endif
}

void* hipo_MPI_LOR_CONST() {
#if !defined(DISABLE_MPI_LOR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LOR);
#else
    return 0;
#endif
}

void* hipo_MPI_BOR_CONST() {
#if !defined(DISABLE_MPI_BOR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_BOR);
#else
    return 0;
#endif
}

void* hipo_MPI_LXOR_CONST() {
#if !defined(DISABLE_MPI_LXOR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LXOR);
#else
    return 0;
#endif
}

void* hipo_MPI_BXOR_CONST() {
#if !defined(DISABLE_MPI_BXOR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_BXOR);
#else
    return 0;
#endif
}

void* hipo_MPI_MINLOC_CONST() {
#if !defined(DISABLE_MPI_MINLOC) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MINLOC);
#else
    return 0;
#endif
}

void* hipo_MPI_MAXLOC_CONST() {
#if !defined(DISABLE_MPI_MAXLOC) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAXLOC);
#else
    return 0;
#endif
}

void* hipo_MPI_REPLACE_CONST() {
#if !defined(DISABLE_MPI_REPLACE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_REPLACE);
#else
    return 0;
#endif
}

void* hipo_MPI_TAG_UB_CONST() {
#if !defined(DISABLE_MPI_TAG_UB) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TAG_UB);
#else
    return 0;
#endif
}

void* hipo_MPI_HOST_CONST() {
#if !defined(DISABLE_MPI_HOST) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_HOST);
#else
    return 0;
#endif
}

void* hipo_MPI_IO_CONST() {
#if !defined(DISABLE_MPI_IO) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_IO);
#else
    return 0;
#endif
}

void* hipo_MPI_WTIME_IS_GLOBAL_CONST() {
#if !defined(DISABLE_MPI_WTIME_IS_GLOBAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WTIME_IS_GLOBAL);
#else
    return 0;
#endif
}

void* hipo_MPI_UNIVERSE_SIZE_CONST() {
#if !defined(DISABLE_MPI_UNIVERSE_SIZE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_UNIVERSE_SIZE);
#else
    return 0;
#endif
}

void* hipo_MPI_LASTUSEDCODE_CONST() {
#if !defined(DISABLE_MPI_LASTUSEDCODE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_LASTUSEDCODE);
#else
    return 0;
#endif
}

void* hipo_MPI_APPNUM_CONST() {
#if !defined(DISABLE_MPI_APPNUM) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_APPNUM);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_BASE_CONST() {
#if !defined(DISABLE_MPI_WIN_BASE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_BASE);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_SIZE_CONST() {
#if !defined(DISABLE_MPI_WIN_SIZE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_SIZE);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_DISP_UNIT_CONST() {
#if !defined(DISABLE_MPI_WIN_DISP_UNIT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_DISP_UNIT);
#else
    return 0;
#endif
}

int hipo_MPI_MAX_PROCESSOR_NAME_CONST() {
#if !defined(DISABLE_MPI_MAX_PROCESSOR_NAME) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MAX_PROCESSOR_NAME);
#else
    return 0;
#endif
}

int hipo_MPI_MAX_ERROR_STRING_CONST() {
#if !defined(DISABLE_MPI_MAX_ERROR_STRING) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MAX_ERROR_STRING);
#else
    return 0;
#endif
}

void* hipo_MPI_MAX_PORT_NAME_CONST() {
#if !defined(DISABLE_MPI_MAX_PORT_NAME) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAX_PORT_NAME);
#else
    return 0;
#endif
}

void* hipo_MPI_MAX_OBJECT_NAME_CONST() {
#if !defined(DISABLE_MPI_MAX_OBJECT_NAME) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAX_OBJECT_NAME);
#else
    return 0;
#endif
}

int hipo_MPI_UNDEFINED_CONST() {
#if !defined(DISABLE_MPI_UNDEFINED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_UNDEFINED);
#else
    return 0;
#endif
}

int hipo_MPI_KEYVAL_INVALID_CONST() {
#if !defined(DISABLE_MPI_KEYVAL_INVALID) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_KEYVAL_INVALID);
#else
    return 0;
#endif
}

void* hipo_MPI_BSEND_OVERHEAD_CONST() {
#if !defined(DISABLE_MPI_BSEND_OVERHEAD) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_BSEND_OVERHEAD);
#else
    return 0;
#endif
}

void* hipo_MPI_BOTTOM_CONST() {
#if !defined(DISABLE_MPI_BOTTOM) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_BOTTOM);
#else
    return 0;
#endif
}

int hipo_MPI_PROC_NULL_CONST() {
#if !defined(DISABLE_MPI_PROC_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_PROC_NULL);
#else
    return 0;
#endif
}

int hipo_MPI_ANY_SOURCE_CONST() {
#if !defined(DISABLE_MPI_ANY_SOURCE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_ANY_SOURCE);
#else
    return 0;
#endif
}

void* hipo_MPI_ROOT_CONST() {
#if !defined(DISABLE_MPI_ROOT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ROOT);
#else
    return 0;
#endif
}

void* hipo_MPI_ANY_TAG_CONST() {
#if !defined(DISABLE_MPI_ANY_TAG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ANY_TAG);
#else
    return 0;
#endif
}

int hipo_MPI_LOCK_EXCLUSIVE_CONST() {
#if !defined(DISABLE_MPI_LOCK_EXCLUSIVE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_LOCK_EXCLUSIVE);
#else
    return 0;
#endif
}

int hipo_MPI_LOCK_SHARED_CONST() {
#if !defined(DISABLE_MPI_LOCK_SHARED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_LOCK_SHARED);
#else
    return 0;
#endif
}

void* hipo_MPI_ERRORS_ARE_FATAL_CONST() {
#if !defined(DISABLE_MPI_ERRORS_ARE_FATAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERRORS_ARE_FATAL);
#else
    return 0;
#endif
}

void* hipo_MPI_ERRORS_RETURN_CONST() {
#if !defined(DISABLE_MPI_ERRORS_RETURN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERRORS_RETURN);
#else
    return 0;
#endif
}

void* hipo_MPI_NULL_COPY_FN_CONST() {
#if !defined(DISABLE_MPI_NULL_COPY_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_NULL_COPY_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_NULL_DELETE_FN_CONST() {
#if !defined(DISABLE_MPI_NULL_DELETE_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_NULL_DELETE_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_DUP_FN_CONST() {
#if !defined(DISABLE_MPI_DUP_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DUP_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_COMM_NULL_COPY_FN_CONST() {
#if !defined(DISABLE_MPI_COMM_NULL_COPY_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_COMM_NULL_COPY_FN);
#else
    return 0;
#endif
}

hipo_MPI_Comm_delete_attr_function* hipo_MPI_COMM_NULL_DELETE_FN_CONST() {
#if !defined(DISABLE_MPI_COMM_NULL_DELETE_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm_delete_attr_function* ret = MPI_COMM_NULL_DELETE_FN;
    hipo_MPI_Comm_delete_attr_function* hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Comm_copy_attr_function* hipo_MPI_COMM_DUP_FN_CONST() {
#if !defined(DISABLE_MPI_COMM_DUP_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm_copy_attr_function* ret = MPI_COMM_DUP_FN;
    hipo_MPI_Comm_copy_attr_function* hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_NULL_COPY_FN_CONST() {
#if !defined(DISABLE_MPI_WIN_NULL_COPY_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_NULL_COPY_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_NULL_DELETE_FN_CONST() {
#if !defined(DISABLE_MPI_WIN_NULL_DELETE_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_NULL_DELETE_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_WIN_DUP_FN_CONST() {
#if !defined(DISABLE_MPI_WIN_DUP_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_WIN_DUP_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPE_NULL_COPY_FN_CONST() {
#if !defined(DISABLE_MPI_TYPE_NULL_COPY_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPE_NULL_COPY_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPE_NULL_DELETE_FN_CONST() {
#if !defined(DISABLE_MPI_TYPE_NULL_DELETE_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPE_NULL_DELETE_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_TYPE_DUP_FN_CONST() {
#if !defined(DISABLE_MPI_TYPE_DUP_FN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_TYPE_DUP_FN);
#else
    return 0;
#endif
}

void* hipo_MPI_INFO_NULL_CONST() {
#if !defined(DISABLE_MPI_INFO_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_INFO_NULL);
#else
    return 0;
#endif
}

void* hipo_MPI_MAX_INFO_KEY_CONST() {
#if !defined(DISABLE_MPI_MAX_INFO_KEY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAX_INFO_KEY);
#else
    return 0;
#endif
}

void* hipo_MPI_MAX_INFO_VAL_CONST() {
#if !defined(DISABLE_MPI_MAX_INFO_VAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAX_INFO_VAL);
#else
    return 0;
#endif
}

void* hipo_MPI_ORDER_C_CONST() {
#if !defined(DISABLE_MPI_ORDER_C) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ORDER_C);
#else
    return 0;
#endif
}

void* hipo_MPI_ORDER_FORTRAN_CONST() {
#if !defined(DISABLE_MPI_ORDER_FORTRAN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ORDER_FORTRAN);
#else
    return 0;
#endif
}

void* hipo_MPI_DISTRIBUTE_BLOCK_CONST() {
#if !defined(DISABLE_MPI_DISTRIBUTE_BLOCK) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DISTRIBUTE_BLOCK);
#else
    return 0;
#endif
}

void* hipo_MPI_DISTRIBUTE_CYCLIC_CONST() {
#if !defined(DISABLE_MPI_DISTRIBUTE_CYCLIC) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DISTRIBUTE_CYCLIC);
#else
    return 0;
#endif
}

void* hipo_MPI_DISTRIBUTE_NONE_CONST() {
#if !defined(DISABLE_MPI_DISTRIBUTE_NONE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DISTRIBUTE_NONE);
#else
    return 0;
#endif
}

void* hipo_MPI_DISTRIBUTE_DFLT_DARG_CONST() {
#if !defined(DISABLE_MPI_DISTRIBUTE_DFLT_DARG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DISTRIBUTE_DFLT_DARG);
#else
    return 0;
#endif
}

void* hipo_MPI_IN_PLACE_CONST() {
#if !defined(DISABLE_MPI_IN_PLACE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_IN_PLACE);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_NOCHECK_CONST() {
#if !defined(DISABLE_MPI_MODE_NOCHECK) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_NOCHECK);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_NOSTORE_CONST() {
#if !defined(DISABLE_MPI_MODE_NOSTORE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_NOSTORE);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_NOPUT_CONST() {
#if !defined(DISABLE_MPI_MODE_NOPUT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_NOPUT);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_NOPRECEDE_CONST() {
#if !defined(DISABLE_MPI_MODE_NOPRECEDE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_NOPRECEDE);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_NOSUCCEED_CONST() {
#if !defined(DISABLE_MPI_MODE_NOSUCCEED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_NOSUCCEED);
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Comm_c2f(hipo_MPI_Comm comm) {
#if !defined(DISABLE_MPI_Comm_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Fint ret = MPI_Comm_c2f(comm_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Comm hipo_MPI_Comm_f2c(hipo_MPI_Fint comm) {
#if !defined(DISABLE_MPI_Comm_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint comm_in;
    copyValue(comm_in, comm);
    MPI_Comm ret = MPI_Comm_f2c(comm_in);
    hipo_MPI_Comm hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Type_c2f(hipo_MPI_Datatype type) {
#if !defined(DISABLE_MPI_Type_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype type_in;
    copyValue(type_in, type);
    MPI_Fint ret = MPI_Type_c2f(type_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Datatype hipo_MPI_Type_f2c(hipo_MPI_Fint type) {
#if !defined(DISABLE_MPI_Type_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint type_in;
    copyValue(type_in, type);
    MPI_Datatype ret = MPI_Type_f2c(type_in);
    hipo_MPI_Datatype hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Group_c2f(hipo_MPI_Group group) {
#if !defined(DISABLE_MPI_Group_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Fint ret = MPI_Group_c2f(group_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Group hipo_MPI_Group_f2c(hipo_MPI_Fint group) {
#if !defined(DISABLE_MPI_Group_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint group_in;
    copyValue(group_in, group);
    MPI_Group ret = MPI_Group_f2c(group_in);
    hipo_MPI_Group hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Info hipo_MPI_Info_f2c(hipo_MPI_Fint info) {
#if !defined(DISABLE_MPI_Info_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint info_in;
    copyValue(info_in, info);
    MPI_Info ret = MPI_Info_f2c(info_in);
    hipo_MPI_Info hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Request hipo_MPI_Request_f2c(hipo_MPI_Fint request) {
#if !defined(DISABLE_MPI_Request_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint request_in;
    copyValue(request_in, request);
    MPI_Request ret = MPI_Request_f2c(request_in);
    hipo_MPI_Request hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Request_c2f(hipo_MPI_Request request) {
#if !defined(DISABLE_MPI_Request_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, request);
    MPI_Fint ret = MPI_Request_c2f(request_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Op_c2f(hipo_MPI_Op op) {
#if !defined(DISABLE_MPI_Op_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Fint ret = MPI_Op_c2f(op_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Op hipo_MPI_Op_f2c(hipo_MPI_Fint op) {
#if !defined(DISABLE_MPI_Op_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint op_in;
    copyValue(op_in, op);
    MPI_Op ret = MPI_Op_f2c(op_in);
    hipo_MPI_Op hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Errhandler_c2f(hipo_MPI_Errhandler errhandler) {
#if !defined(DISABLE_MPI_Errhandler_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, errhandler);
    MPI_Fint ret = MPI_Errhandler_c2f(errhandler_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Errhandler hipo_MPI_Errhandler_f2c(hipo_MPI_Fint errhandler) {
#if !defined(DISABLE_MPI_Errhandler_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint errhandler_in;
    copyValue(errhandler_in, errhandler);
    MPI_Errhandler ret = MPI_Errhandler_f2c(errhandler_in);
    hipo_MPI_Errhandler hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Fint hipo_MPI_Win_c2f(hipo_MPI_Win win) {
#if !defined(DISABLE_MPI_Win_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    MPI_Fint ret = MPI_Win_c2f(win_in);
    hipo_MPI_Fint hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Win hipo_MPI_Win_f2c(hipo_MPI_Fint win) {
#if !defined(DISABLE_MPI_Win_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint win_in;
    copyValue(win_in, win);
    MPI_Win ret = MPI_Win_f2c(win_in);
    hipo_MPI_Win hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Status* hipo_MPI_STATUS_IGNORE_CONST() {
#if !defined(DISABLE_MPI_STATUS_IGNORE) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Status* ret = MPI_STATUS_IGNORE;
    hipo_MPI_Status* hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

hipo_MPI_Status* hipo_MPI_STATUSES_IGNORE_CONST() {
#if !defined(DISABLE_MPI_STATUSES_IGNORE) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Status* ret = MPI_STATUSES_IGNORE;
    hipo_MPI_Status* hipo_ret;
    copyValue(hipo_ret, ret);
    return hipo_ret;
#else
    return 0;
#endif
}

void* hipo_MPI_ERRCODES_IGNORE_CONST() {
#if !defined(DISABLE_MPI_ERRCODES_IGNORE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERRCODES_IGNORE);
#else
    return 0;
#endif
}

void* hipo_MPI_ARGV_NULL_CONST() {
#if !defined(DISABLE_MPI_ARGV_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ARGV_NULL);
#else
    return 0;
#endif
}

void* hipo_MPI_ARGVS_NULL_CONST() {
#if !defined(DISABLE_MPI_ARGVS_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ARGVS_NULL);
#else
    return 0;
#endif
}

void* hipo_MPI_THREAD_SINGLE_CONST() {
#if !defined(DISABLE_MPI_THREAD_SINGLE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_THREAD_SINGLE);
#else
    return 0;
#endif
}

void* hipo_MPI_THREAD_FUNNELED_CONST() {
#if !defined(DISABLE_MPI_THREAD_FUNNELED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_THREAD_FUNNELED);
#else
    return 0;
#endif
}

void* hipo_MPI_THREAD_SERIALIZED_CONST() {
#if !defined(DISABLE_MPI_THREAD_SERIALIZED) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_THREAD_SERIALIZED);
#else
    return 0;
#endif
}

void* hipo_MPI_THREAD_MULTIPLE_CONST() {
#if !defined(DISABLE_MPI_THREAD_MULTIPLE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_THREAD_MULTIPLE);
#else
    return 0;
#endif
}

int hipo_MPI_SUCCESS_CONST() {
#if !defined(DISABLE_MPI_SUCCESS) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_SUCCESS);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_BUFFER_CONST() {
#if !defined(DISABLE_MPI_ERR_BUFFER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_BUFFER);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_COUNT_CONST() {
#if !defined(DISABLE_MPI_ERR_COUNT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_COUNT);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_TYPE_CONST() {
#if !defined(DISABLE_MPI_ERR_TYPE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_TYPE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_TAG_CONST() {
#if !defined(DISABLE_MPI_ERR_TAG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_TAG);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_COMM_CONST() {
#if !defined(DISABLE_MPI_ERR_COMM) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_COMM);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_RANK_CONST() {
#if !defined(DISABLE_MPI_ERR_RANK) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_RANK);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_ROOT_CONST() {
#if !defined(DISABLE_MPI_ERR_ROOT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_ROOT);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_TRUNCATE_CONST() {
#if !defined(DISABLE_MPI_ERR_TRUNCATE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_TRUNCATE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_GROUP_CONST() {
#if !defined(DISABLE_MPI_ERR_GROUP) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_GROUP);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_OP_CONST() {
#if !defined(DISABLE_MPI_ERR_OP) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_OP);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_REQUEST_CONST() {
#if !defined(DISABLE_MPI_ERR_REQUEST) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_REQUEST);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_TOPOLOGY_CONST() {
#if !defined(DISABLE_MPI_ERR_TOPOLOGY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_TOPOLOGY);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_DIMS_CONST() {
#if !defined(DISABLE_MPI_ERR_DIMS) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_DIMS);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_ARG_CONST() {
#if !defined(DISABLE_MPI_ERR_ARG) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_ARG);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_OTHER_CONST() {
#if !defined(DISABLE_MPI_ERR_OTHER) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_OTHER);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_UNKNOWN_CONST() {
#if !defined(DISABLE_MPI_ERR_UNKNOWN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_UNKNOWN);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_INTERN_CONST() {
#if !defined(DISABLE_MPI_ERR_INTERN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_INTERN);
#else
    return 0;
#endif
}

int hipo_MPI_ERR_IN_STATUS_CONST() {
#if !defined(DISABLE_MPI_ERR_IN_STATUS) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_ERR_IN_STATUS);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_PENDING_CONST() {
#if !defined(DISABLE_MPI_ERR_PENDING) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_PENDING);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_ACCESS_CONST() {
#if !defined(DISABLE_MPI_ERR_ACCESS) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_ACCESS);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_AMODE_CONST() {
#if !defined(DISABLE_MPI_ERR_AMODE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_AMODE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_BAD_FILE_CONST() {
#if !defined(DISABLE_MPI_ERR_BAD_FILE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_BAD_FILE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_CONVERSION_CONST() {
#if !defined(DISABLE_MPI_ERR_CONVERSION) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_CONVERSION);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_DUP_DATAREP_CONST() {
#if !defined(DISABLE_MPI_ERR_DUP_DATAREP) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_DUP_DATAREP);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_FILE_EXISTS_CONST() {
#if !defined(DISABLE_MPI_ERR_FILE_EXISTS) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_FILE_EXISTS);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_FILE_IN_USE_CONST() {
#if !defined(DISABLE_MPI_ERR_FILE_IN_USE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_FILE_IN_USE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_FILE_CONST() {
#if !defined(DISABLE_MPI_ERR_FILE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_FILE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_IO_CONST() {
#if !defined(DISABLE_MPI_ERR_IO) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_IO);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_NO_SPACE_CONST() {
#if !defined(DISABLE_MPI_ERR_NO_SPACE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_NO_SPACE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_NO_SUCH_FILE_CONST() {
#if !defined(DISABLE_MPI_ERR_NO_SUCH_FILE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_NO_SUCH_FILE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_READ_ONLY_CONST() {
#if !defined(DISABLE_MPI_ERR_READ_ONLY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_READ_ONLY);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_UNSUPPORTED_DATAREP_CONST() {
#if !defined(DISABLE_MPI_ERR_UNSUPPORTED_DATAREP) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_UNSUPPORTED_DATAREP);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_INFO_CONST() {
#if !defined(DISABLE_MPI_ERR_INFO) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_INFO);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_INFO_KEY_CONST() {
#if !defined(DISABLE_MPI_ERR_INFO_KEY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_INFO_KEY);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_INFO_VALUE_CONST() {
#if !defined(DISABLE_MPI_ERR_INFO_VALUE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_INFO_VALUE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_INFO_NOKEY_CONST() {
#if !defined(DISABLE_MPI_ERR_INFO_NOKEY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_INFO_NOKEY);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_NAME_CONST() {
#if !defined(DISABLE_MPI_ERR_NAME) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_NAME);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_NO_MEM_CONST() {
#if !defined(DISABLE_MPI_ERR_NO_MEM) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_NO_MEM);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_NOT_SAME_CONST() {
#if !defined(DISABLE_MPI_ERR_NOT_SAME) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_NOT_SAME);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_PORT_CONST() {
#if !defined(DISABLE_MPI_ERR_PORT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_PORT);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_QUOTA_CONST() {
#if !defined(DISABLE_MPI_ERR_QUOTA) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_QUOTA);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_SERVICE_CONST() {
#if !defined(DISABLE_MPI_ERR_SERVICE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_SERVICE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_SPAWN_CONST() {
#if !defined(DISABLE_MPI_ERR_SPAWN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_SPAWN);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_UNSUPPORTED_OPERATION_CONST() {
#if !defined(DISABLE_MPI_ERR_UNSUPPORTED_OPERATION) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_UNSUPPORTED_OPERATION);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_WIN_CONST() {
#if !defined(DISABLE_MPI_ERR_WIN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_WIN);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_BASE_CONST() {
#if !defined(DISABLE_MPI_ERR_BASE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_BASE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_LOCKTYPE_CONST() {
#if !defined(DISABLE_MPI_ERR_LOCKTYPE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_LOCKTYPE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_KEYVAL_CONST() {
#if !defined(DISABLE_MPI_ERR_KEYVAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_KEYVAL);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_RMA_CONFLICT_CONST() {
#if !defined(DISABLE_MPI_ERR_RMA_CONFLICT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_RMA_CONFLICT);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_RMA_SYNC_CONST() {
#if !defined(DISABLE_MPI_ERR_RMA_SYNC) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_RMA_SYNC);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_SIZE_CONST() {
#if !defined(DISABLE_MPI_ERR_SIZE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_SIZE);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_DISP_CONST() {
#if !defined(DISABLE_MPI_ERR_DISP) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_DISP);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_ASSERT_CONST() {
#if !defined(DISABLE_MPI_ERR_ASSERT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_ASSERT);
#else
    return 0;
#endif
}

void* hipo_MPI_ERR_LASTCODE_CONST() {
#if !defined(DISABLE_MPI_ERR_LASTCODE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_ERR_LASTCODE);
#else
    return 0;
#endif
}

void* hipo_MPI_CONVERSION_FN_NULL_CONST() {
#if !defined(DISABLE_MPI_CONVERSION_FN_NULL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_CONVERSION_FN_NULL);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_RDONLY_CONST() {
#if !defined(DISABLE_MPI_MODE_RDONLY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_RDONLY);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_RDWR_CONST() {
#if !defined(DISABLE_MPI_MODE_RDWR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_RDWR);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_WRONLY_CONST() {
#if !defined(DISABLE_MPI_MODE_WRONLY) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_WRONLY);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_CREATE_CONST() {
#if !defined(DISABLE_MPI_MODE_CREATE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_CREATE);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_EXCL_CONST() {
#if !defined(DISABLE_MPI_MODE_EXCL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_EXCL);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_DELETE_ON_CLOSE_CONST() {
#if !defined(DISABLE_MPI_MODE_DELETE_ON_CLOSE) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_DELETE_ON_CLOSE);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_UNIQUE_OPEN_CONST() {
#if !defined(DISABLE_MPI_MODE_UNIQUE_OPEN) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_UNIQUE_OPEN);
#else
    return 0;
#endif
}

int hipo_MPI_MODE_APPEND_CONST() {
#if !defined(DISABLE_MPI_MODE_APPEND) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_MODE_APPEND);
#else
    return 0;
#endif
}

void* hipo_MPI_MODE_SEQUENTIAL_CONST() {
#if !defined(DISABLE_MPI_MODE_SEQUENTIAL) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MODE_SEQUENTIAL);
#else
    return 0;
#endif
}

void* hipo_MPI_DISPLACEMENT_CURRENT_CONST() {
#if !defined(DISABLE_MPI_DISPLACEMENT_CURRENT) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_DISPLACEMENT_CURRENT);
#else
    return 0;
#endif
}

int hipo_MPI_SEEK_SET_CONST() {
#if !defined(DISABLE_MPI_SEEK_SET) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (int)(MPI_SEEK_SET);
#else
    return 0;
#endif
}

void* hipo_MPI_SEEK_CUR_CONST() {
#if !defined(DISABLE_MPI_SEEK_CUR) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_SEEK_CUR);
#else
    return 0;
#endif
}

void* hipo_MPI_SEEK_END_CONST() {
#if !defined(DISABLE_MPI_SEEK_END) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_SEEK_END);
#else
    return 0;
#endif
}

void* hipo_MPI_MAX_DATAREP_STRING_CONST() {
#if !defined(DISABLE_MPI_MAX_DATAREP_STRING) && !defined(HIPO_MPI_DUMMY_IMPL)
    return (void*)(MPI_MAX_DATAREP_STRING);
#else
    return 0;
#endif
}
int hipo_MPI_Status_c2f ( const hipo_MPI_Status * c_status , hipo_MPI_Fint * f_status )
{
#if !defined(DISABLE_MPI_Status_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status c_status_data;
    MPI_Status* c_status_in = MPI_STATUS_IGNORE;
    if (c_status != hipo_MPI_STATUS_IGNORE) {
        c_status_in = &c_status_data;
        copyValue(c_status_in, c_status);
    }
    MPI_Fint f_status_in;
    copyValue(f_status_in, *f_status);
    int ret = MPI_Status_c2f(c_status_in, &f_status_in);
    copyValue(*f_status, f_status_in);

    return ret;
#else
    printf("error: MPI_Status_c2f is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Status_f2c ( const hipo_MPI_Fint * f_status , hipo_MPI_Status * c_status )
{
#if !defined(DISABLE_MPI_Status_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    const MPI_Fint * f_status_in;
    copyValue(f_status_in, f_status);

    MPI_Status c_status_data;
    MPI_Status* c_status_in = MPI_STATUS_IGNORE;
    if (c_status != hipo_MPI_STATUS_IGNORE) {
        c_status_in = &c_status_data;
        copyValue(c_status_in, c_status);
    }
    int ret = MPI_Status_f2c(const_cast<MPI_Fint*>(f_status_in), c_status_in);

    if (c_status != hipo_MPI_STATUS_IGNORE) {
        copyValue(c_status, c_status_in);
    }

    return ret;
#else
    printf("error: MPI_Status_f2c is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_f90_integer ( int r , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_f90_integer) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_f90_integer(r, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_f90_integer is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_f90_real ( int p , int r , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_f90_real) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_f90_real(p, r, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_f90_real is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_f90_complex ( int p , int r , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_f90_complex) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_f90_complex(p, r, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_f90_complex is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Attr_delete ( hipo_MPI_Comm comm , int keyval )
{
#if !defined(DISABLE_MPI_Attr_delete) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Attr_delete(comm_in, keyval);

    return ret;
#else
    printf("error: MPI_Attr_delete is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Attr_get ( hipo_MPI_Comm comm , int keyval , void * attribute_val , int * flag )
{
#if !defined(DISABLE_MPI_Attr_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Attr_get(comm_in, keyval, attribute_val, flag);

    return ret;
#else
    printf("error: MPI_Attr_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Attr_put ( hipo_MPI_Comm comm , int keyval , void * attribute_val )
{
#if !defined(DISABLE_MPI_Attr_put) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Attr_put(comm_in, keyval, attribute_val);

    return ret;
#else
    printf("error: MPI_Attr_put is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_create_keyval ( hipo_MPI_Comm_copy_attr_function * comm_copy_attr_fn , hipo_MPI_Comm_delete_attr_function * comm_delete_attr_fn , int * comm_keyval , void * extra_state )
{
#if !defined(DISABLE_MPI_Comm_create_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm_copy_attr_function * comm_copy_attr_fn_in;
    copyValue(comm_copy_attr_fn_in, comm_copy_attr_fn);
    MPI_Comm_delete_attr_function * comm_delete_attr_fn_in;
    copyValue(comm_delete_attr_fn_in, comm_delete_attr_fn);
    int ret = MPI_Comm_create_keyval(comm_copy_attr_fn_in, comm_delete_attr_fn_in, comm_keyval, extra_state);

    return ret;
#else
    printf("error: MPI_Comm_create_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_delete_attr ( hipo_MPI_Comm comm , int comm_keyval )
{
#if !defined(DISABLE_MPI_Comm_delete_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_delete_attr(comm_in, comm_keyval);

    return ret;
#else
    printf("error: MPI_Comm_delete_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_free_keyval ( int * comm_keyval )
{
#if !defined(DISABLE_MPI_Comm_free_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Comm_free_keyval(comm_keyval);

    return ret;
#else
    printf("error: MPI_Comm_free_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_get_attr ( hipo_MPI_Comm comm , int comm_keyval , void * attribute_val , int * flag )
{
#if !defined(DISABLE_MPI_Comm_get_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_get_attr(comm_in, comm_keyval, attribute_val, flag);

    return ret;
#else
    printf("error: MPI_Comm_get_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_set_attr ( hipo_MPI_Comm comm , int comm_keyval , void * attribute_val )
{
#if !defined(DISABLE_MPI_Comm_set_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_set_attr(comm_in, comm_keyval, attribute_val);

    return ret;
#else
    printf("error: MPI_Comm_set_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Keyval_create ( hipo_MPI_Copy_function * copy_fn , hipo_MPI_Delete_function * delete_fn , int * keyval , void * extra_state )
{
#if !defined(DISABLE_MPI_Keyval_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Copy_function * copy_fn_in;
    copyValue(copy_fn_in, copy_fn);
    MPI_Delete_function * delete_fn_in;
    copyValue(delete_fn_in, delete_fn);
    int ret = MPI_Keyval_create(copy_fn_in, delete_fn_in, keyval, extra_state);

    return ret;
#else
    printf("error: MPI_Keyval_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Keyval_free ( int * keyval )
{
#if !defined(DISABLE_MPI_Keyval_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Keyval_free(keyval);

    return ret;
#else
    printf("error: MPI_Keyval_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_keyval ( hipo_MPI_Type_copy_attr_function * type_copy_attr_fn , hipo_MPI_Type_delete_attr_function * type_delete_attr_fn , int * type_keyval , void * extra_state )
{
#if !defined(DISABLE_MPI_Type_create_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Type_copy_attr_function * type_copy_attr_fn_in;
    copyValue(type_copy_attr_fn_in, type_copy_attr_fn);
    MPI_Type_delete_attr_function * type_delete_attr_fn_in;
    copyValue(type_delete_attr_fn_in, type_delete_attr_fn);
    int ret = MPI_Type_create_keyval(type_copy_attr_fn_in, type_delete_attr_fn_in, type_keyval, extra_state);

    return ret;
#else
    printf("error: MPI_Type_create_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_delete_attr ( hipo_MPI_Datatype datatype , int type_keyval )
{
#if !defined(DISABLE_MPI_Type_delete_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_delete_attr(datatype_in, type_keyval);

    return ret;
#else
    printf("error: MPI_Type_delete_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_free_keyval ( int * type_keyval )
{
#if !defined(DISABLE_MPI_Type_free_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Type_free_keyval(type_keyval);

    return ret;
#else
    printf("error: MPI_Type_free_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_attr ( hipo_MPI_Datatype datatype , int type_keyval , void * attribute_val , int * flag )
{
#if !defined(DISABLE_MPI_Type_get_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_get_attr(datatype_in, type_keyval, attribute_val, flag);

    return ret;
#else
    printf("error: MPI_Type_get_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_set_attr ( hipo_MPI_Datatype datatype , int type_keyval , void * attribute_val )
{
#if !defined(DISABLE_MPI_Type_set_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_set_attr(datatype_in, type_keyval, attribute_val);

    return ret;
#else
    printf("error: MPI_Type_set_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_create_keyval ( hipo_MPI_Win_copy_attr_function * win_copy_attr_fn , hipo_MPI_Win_delete_attr_function * win_delete_attr_fn , int * win_keyval , void * extra_state )
{
#if !defined(DISABLE_MPI_Win_create_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win_copy_attr_function * win_copy_attr_fn_in;
    copyValue(win_copy_attr_fn_in, win_copy_attr_fn);
    MPI_Win_delete_attr_function * win_delete_attr_fn_in;
    copyValue(win_delete_attr_fn_in, win_delete_attr_fn);
    int ret = MPI_Win_create_keyval(win_copy_attr_fn_in, win_delete_attr_fn_in, win_keyval, extra_state);

    return ret;
#else
    printf("error: MPI_Win_create_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_delete_attr ( hipo_MPI_Win win , int win_keyval )
{
#if !defined(DISABLE_MPI_Win_delete_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_delete_attr(win_in, win_keyval);

    return ret;
#else
    printf("error: MPI_Win_delete_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_free_keyval ( int * win_keyval )
{
#if !defined(DISABLE_MPI_Win_free_keyval) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Win_free_keyval(win_keyval);

    return ret;
#else
    printf("error: MPI_Win_free_keyval is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_get_attr ( hipo_MPI_Win win , int win_keyval , void * attribute_val , int * flag )
{
#if !defined(DISABLE_MPI_Win_get_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_get_attr(win_in, win_keyval, attribute_val, flag);

    return ret;
#else
    printf("error: MPI_Win_get_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_set_attr ( hipo_MPI_Win win , int win_keyval , void * attribute_val )
{
#if !defined(DISABLE_MPI_Win_set_attr) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_set_attr(win_in, win_keyval, attribute_val);

    return ret;
#else
    printf("error: MPI_Win_set_attr is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Allgather ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Allgather) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Allgather(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, recvcount, recvtype_in, comm_in);

    return ret;
#else
    printf("error: MPI_Allgather is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Allgatherv ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int displs [ ] , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Allgatherv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Allgatherv(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, const_cast<int*>(recvcounts), const_cast<int*>(displs), recvtype_in, comm_in);

    return ret;
#else
    printf("error: MPI_Allgatherv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Allreduce ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Allreduce) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Allreduce(const_cast<void*>(sendbuf), recvbuf, count, datatype_in, op_in, comm_in);

    return ret;
#else
    printf("error: MPI_Allreduce is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Alltoall ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Alltoall) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Alltoall(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, recvcount, recvtype_in, comm_in);

    return ret;
#else
    printf("error: MPI_Alltoall is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Alltoallv ( const void * sendbuf , const int sendcounts [ ] , const int sdispls [ ] , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int rdispls [ ] , hipo_MPI_Datatype recvtype , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Alltoallv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Alltoallv(const_cast<void*>(sendbuf), const_cast<int*>(sendcounts), const_cast<int*>(sdispls), sendtype_in, recvbuf, const_cast<int*>(recvcounts), const_cast<int*>(rdispls), recvtype_in, comm_in);

    return ret;
#else
    printf("error: MPI_Alltoallv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Alltoallw ( const void * sendbuf , const int sendcounts [ ] , const int sdispls [ ] , const hipo_MPI_Datatype sendtypes [ ] , void * recvbuf , const int recvcounts [ ] , const int rdispls [ ] , const hipo_MPI_Datatype recvtypes [ ] , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Alltoallw) && !defined(HIPO_MPI_DUMMY_IMPL)
    int nprocs;
    hipo_MPI_Comm_size(comm, &nprocs);

    MPI_Datatype sendtypes_in[nprocs];
    for (int i=0; i<nprocs; i++) {
        copyValue(sendtypes_in[i], sendtypes[i]);
    }

    MPI_Datatype recvtypes_in[nprocs];
    for (int i=0; i<nprocs; i++) {
        copyValue(recvtypes_in[i], recvtypes[i]);
    }
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Alltoallw(const_cast<void*>(sendbuf), const_cast<int*>(sendcounts), const_cast<int*>(sdispls), sendtypes_in, recvbuf, const_cast<int*>(recvcounts), const_cast<int*>(rdispls), recvtypes_in, comm_in);

    return ret;
#else
    printf("error: MPI_Alltoallw is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Barrier ( hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Barrier) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Barrier(comm_in);

    return ret;
#else
    printf("error: MPI_Barrier is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Bcast ( void * buffer , int count , hipo_MPI_Datatype datatype , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Bcast) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Bcast(buffer, count, datatype_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Bcast is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Exscan ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Exscan) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Exscan(const_cast<void*>(sendbuf), recvbuf, count, datatype_in, op_in, comm_in);

    return ret;
#else
    printf("error: MPI_Exscan is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Gather ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Gather) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Gather(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, recvcount, recvtype_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Gather is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Gatherv ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , const int recvcounts [ ] , const int displs [ ] , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Gatherv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Gatherv(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, const_cast<int*>(recvcounts), const_cast<int*>(displs), recvtype_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Gatherv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Reduce ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Reduce) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Reduce(const_cast<void*>(sendbuf), recvbuf, count, datatype_in, op_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Reduce is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Reduce_local ( const void * inbuf , void * inoutbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op )
{
#if !defined(DISABLE_MPI_Reduce_local) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    int ret = MPI_Reduce_local(const_cast<void*>(inbuf), inoutbuf, count, datatype_in, op_in);

    return ret;
#else
    printf("error: MPI_Reduce_local is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Reduce_scatter ( const void * sendbuf , void * recvbuf , const int recvcounts [ ] , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Reduce_scatter) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Reduce_scatter(const_cast<void*>(sendbuf), recvbuf, const_cast<int*>(recvcounts), datatype_in, op_in, comm_in);

    return ret;
#else
    printf("error: MPI_Reduce_scatter is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Scan ( const void * sendbuf , void * recvbuf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Op op , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Scan) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Scan(const_cast<void*>(sendbuf), recvbuf, count, datatype_in, op_in, comm_in);

    return ret;
#else
    printf("error: MPI_Scan is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Scatter ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Scatter) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Scatter(const_cast<void*>(sendbuf), sendcount, sendtype_in, recvbuf, recvcount, recvtype_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Scatter is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Scatterv ( const void * sendbuf , const int sendcounts [ ] , const int displs [ ] , hipo_MPI_Datatype sendtype , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int root , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Scatterv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Scatterv(const_cast<void*>(sendbuf), const_cast<int*>(sendcounts), const_cast<int*>(displs), sendtype_in, recvbuf, recvcount, recvtype_in, root, comm_in);

    return ret;
#else
    printf("error: MPI_Scatterv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_compare ( hipo_MPI_Comm comm1 , hipo_MPI_Comm comm2 , int * result )
{
#if !defined(DISABLE_MPI_Comm_compare) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm1_in;
    copyValue(comm1_in, comm1);
    MPI_Comm comm2_in;
    copyValue(comm2_in, comm2);
    int ret = MPI_Comm_compare(comm1_in, comm2_in, result);

    return ret;
#else
    printf("error: MPI_Comm_compare is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_create ( hipo_MPI_Comm comm , hipo_MPI_Group group , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Comm_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Comm_create(comm_in, group_in, &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Comm_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_dup ( hipo_MPI_Comm comm , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Comm_dup) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Comm_dup(comm_in, &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Comm_dup is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_free ( hipo_MPI_Comm * comm )
{
#if !defined(DISABLE_MPI_Comm_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, *comm);
    int ret = MPI_Comm_free(&comm_in);
    copyValue(*comm, comm_in);

    return ret;
#else
    printf("error: MPI_Comm_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_get_name ( hipo_MPI_Comm comm , char * comm_name , int * resultlen )
{
#if !defined(DISABLE_MPI_Comm_get_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_get_name(comm_in, comm_name, resultlen);

    return ret;
#else
    printf("error: MPI_Comm_get_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_group ( hipo_MPI_Comm comm , hipo_MPI_Group * group )
{
#if !defined(DISABLE_MPI_Comm_group) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Group group_in;
    copyValue(group_in, *group);
    int ret = MPI_Comm_group(comm_in, &group_in);
    copyValue(*group, group_in);

    return ret;
#else
    printf("error: MPI_Comm_group is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_rank ( hipo_MPI_Comm comm , int * rank )
{
#if !defined(DISABLE_MPI_Comm_rank) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_rank(comm_in, rank);

    return ret;
#else
    printf("error: MPI_Comm_rank is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_remote_group ( hipo_MPI_Comm comm , hipo_MPI_Group * group )
{
#if !defined(DISABLE_MPI_Comm_remote_group) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Group group_in;
    copyValue(group_in, *group);
    int ret = MPI_Comm_remote_group(comm_in, &group_in);
    copyValue(*group, group_in);

    return ret;
#else
    printf("error: MPI_Comm_remote_group is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_remote_size ( hipo_MPI_Comm comm , int * size )
{
#if !defined(DISABLE_MPI_Comm_remote_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_remote_size(comm_in, size);

    return ret;
#else
    printf("error: MPI_Comm_remote_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_set_name ( hipo_MPI_Comm comm , const char * comm_name )
{
#if !defined(DISABLE_MPI_Comm_set_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_set_name(comm_in, const_cast<char*>(comm_name));

    return ret;
#else
    printf("error: MPI_Comm_set_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_size ( hipo_MPI_Comm comm , int * size )
{
#if !defined(DISABLE_MPI_Comm_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_size(comm_in, size);

    return ret;
#else
    printf("error: MPI_Comm_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_split ( hipo_MPI_Comm comm , int color , int key , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Comm_split) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Comm_split(comm_in, color, key, &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Comm_split is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_test_inter ( hipo_MPI_Comm comm , int * flag )
{
#if !defined(DISABLE_MPI_Comm_test_inter) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_test_inter(comm_in, flag);

    return ret;
#else
    printf("error: MPI_Comm_test_inter is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Intercomm_create ( hipo_MPI_Comm local_comm , int local_leader , hipo_MPI_Comm peer_comm , int remote_leader , int tag , hipo_MPI_Comm * newintercomm )
{
#if !defined(DISABLE_MPI_Intercomm_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm local_comm_in;
    copyValue(local_comm_in, local_comm);
    MPI_Comm peer_comm_in;
    copyValue(peer_comm_in, peer_comm);
    MPI_Comm newintercomm_in;
    copyValue(newintercomm_in, *newintercomm);
    int ret = MPI_Intercomm_create(local_comm_in, local_leader, peer_comm_in, remote_leader, tag, &newintercomm_in);
    copyValue(*newintercomm, newintercomm_in);

    return ret;
#else
    printf("error: MPI_Intercomm_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Intercomm_merge ( hipo_MPI_Comm intercomm , int high , hipo_MPI_Comm * newintracomm )
{
#if !defined(DISABLE_MPI_Intercomm_merge) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm intercomm_in;
    copyValue(intercomm_in, intercomm);
    MPI_Comm newintracomm_in;
    copyValue(newintracomm_in, *newintracomm);
    int ret = MPI_Intercomm_merge(intercomm_in, high, &newintracomm_in);
    copyValue(*newintracomm, newintracomm_in);

    return ret;
#else
    printf("error: MPI_Intercomm_merge is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get_address ( const void * location , hipo_MPI_Aint * address )
{
#if !defined(DISABLE_MPI_Get_address) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Aint address_in;
    copyValue(address_in, *address);
    int ret = MPI_Get_address(const_cast<void*>(location), &address_in);
    copyValue(*address, address_in);

    return ret;
#else
    printf("error: MPI_Get_address is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get_count ( const hipo_MPI_Status * status , hipo_MPI_Datatype datatype , int * count )
{
#if !defined(DISABLE_MPI_Get_count) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Get_count(status_in, datatype_in, count);

    return ret;
#else
    printf("error: MPI_Get_count is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get_elements ( const hipo_MPI_Status * status , hipo_MPI_Datatype datatype , int * count )
{
#if !defined(DISABLE_MPI_Get_elements) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Get_elements(status_in, datatype_in, count);

    return ret;
#else
    printf("error: MPI_Get_elements is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Pack ( const void * inbuf , int incount , hipo_MPI_Datatype datatype , void * outbuf , int outsize , int * position , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Pack) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Pack(const_cast<void*>(inbuf), incount, datatype_in, outbuf, outsize, position, comm_in);

    return ret;
#else
    printf("error: MPI_Pack is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Pack_external ( const char * datarep , const void * inbuf , int incount , hipo_MPI_Datatype datatype , void * outbuf , hipo_MPI_Aint outsize , hipo_MPI_Aint * position )
{
#if !defined(DISABLE_MPI_Pack_external) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Aint outsize_in;
    copyValue(outsize_in, outsize);
    MPI_Aint position_in;
    copyValue(position_in, *position);
    int ret = MPI_Pack_external(const_cast<char*>(datarep), const_cast<void*>(inbuf), incount, datatype_in, outbuf, outsize_in, &position_in);
    copyValue(*position, position_in);

    return ret;
#else
    printf("error: MPI_Pack_external is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Pack_external_size ( const char * datarep , int incount , hipo_MPI_Datatype datatype , hipo_MPI_Aint * size )
{
#if !defined(DISABLE_MPI_Pack_external_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Aint size_in;
    copyValue(size_in, *size);
    int ret = MPI_Pack_external_size(const_cast<char*>(datarep), incount, datatype_in, &size_in);
    copyValue(*size, size_in);

    return ret;
#else
    printf("error: MPI_Pack_external_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Pack_size ( int incount , hipo_MPI_Datatype datatype , hipo_MPI_Comm comm , int * size )
{
#if !defined(DISABLE_MPI_Pack_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Pack_size(incount, datatype_in, comm_in, size);

    return ret;
#else
    printf("error: MPI_Pack_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Status_set_elements ( hipo_MPI_Status * status , hipo_MPI_Datatype datatype , int count )
{
#if !defined(DISABLE_MPI_Status_set_elements) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Status_set_elements(status_in, datatype_in, count);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Status_set_elements is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_commit ( hipo_MPI_Datatype * datatype )
{
#if !defined(DISABLE_MPI_Type_commit) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, *datatype);
    int ret = MPI_Type_commit(&datatype_in);
    copyValue(*datatype, datatype_in);

    return ret;
#else
    printf("error: MPI_Type_commit is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_contiguous ( int count , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_contiguous) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_contiguous(count, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_contiguous is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_darray ( int size , int rank , int ndims , const int array_of_gsizes [ ] , const int array_of_distribs [ ] , const int array_of_dargs [ ] , const int array_of_psizes [ ] , int order , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_darray) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_darray(size, rank, ndims, const_cast<int*>(array_of_gsizes), const_cast<int*>(array_of_distribs), const_cast<int*>(array_of_dargs), const_cast<int*>(array_of_psizes), order, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_darray is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_hindexed ( int count , const int array_of_blocklengths [ ] , const hipo_MPI_Aint array_of_displacements [ ] , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_hindexed) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Aint array_of_displacements_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_displacements_in[i], array_of_displacements[i]);
    }
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_hindexed(count, const_cast<int*>(array_of_blocklengths), array_of_displacements_in, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_hindexed is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_hvector ( int count , int blocklength , hipo_MPI_Aint stride , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_hvector) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Aint stride_in;
    copyValue(stride_in, stride);
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_hvector(count, blocklength, stride_in, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_hvector is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_indexed_block ( int count , int blocklength , const int array_of_displacements [ ] , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_indexed_block) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_indexed_block(count, blocklength, const_cast<int*>(array_of_displacements), oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_indexed_block is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_resized ( hipo_MPI_Datatype oldtype , hipo_MPI_Aint lb , hipo_MPI_Aint extent , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_resized) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Aint lb_in;
    copyValue(lb_in, lb);
    MPI_Aint extent_in;
    copyValue(extent_in, extent);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_resized(oldtype_in, lb_in, extent_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_resized is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_struct ( int count , const int array_of_blocklengths [ ] , const hipo_MPI_Aint array_of_displacements [ ] , const hipo_MPI_Datatype array_of_types [ ] , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_struct) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Aint array_of_displacements_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_displacements_in[i], array_of_displacements[i]);
    }

    MPI_Datatype array_of_types_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_types_in[i], array_of_types[i]);
    }
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_struct(count, const_cast<int*>(array_of_blocklengths), array_of_displacements_in, array_of_types_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_struct is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_create_subarray ( int ndims , const int array_of_sizes [ ] , const int array_of_subsizes [ ] , const int array_of_starts [ ] , int order , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_create_subarray) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_create_subarray(ndims, const_cast<int*>(array_of_sizes), const_cast<int*>(array_of_subsizes), const_cast<int*>(array_of_starts), order, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_create_subarray is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_dup ( hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_dup) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_dup(oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_dup is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_free ( hipo_MPI_Datatype * datatype )
{
#if !defined(DISABLE_MPI_Type_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, *datatype);
    int ret = MPI_Type_free(&datatype_in);
    copyValue(*datatype, datatype_in);

    return ret;
#else
    printf("error: MPI_Type_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_contents ( hipo_MPI_Datatype datatype , int max_integers , int max_addresses , int max_datatypes , int array_of_integers [ ] , hipo_MPI_Aint array_of_addresses [ ] , hipo_MPI_Datatype array_of_datatypes [ ] )
{
#if !defined(DISABLE_MPI_Type_get_contents) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Aint array_of_addresses_in[max_addresses];
    for (int i=0; i<max_addresses; i++) {
        copyValue(array_of_addresses_in[i], array_of_addresses[i]);
    }

    MPI_Datatype array_of_datatypes_in[max_datatypes];
    for (int i=0; i<max_datatypes; i++) {
        copyValue(array_of_datatypes_in[i], array_of_datatypes[i]);
    }
    int ret = MPI_Type_get_contents(datatype_in, max_integers, max_addresses, max_datatypes, array_of_integers, array_of_addresses_in, array_of_datatypes_in);

    for (int i=0; i<max_addresses; i++) {
        copyValue(array_of_addresses[i], array_of_addresses_in[i]);
    }

    for (int i=0; i<max_datatypes; i++) {
        copyValue(array_of_datatypes[i], array_of_datatypes_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Type_get_contents is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_envelope ( hipo_MPI_Datatype datatype , int * num_integers , int * num_addresses , int * num_datatypes , int * combiner )
{
#if !defined(DISABLE_MPI_Type_get_envelope) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_get_envelope(datatype_in, num_integers, num_addresses, num_datatypes, combiner);

    return ret;
#else
    printf("error: MPI_Type_get_envelope is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_extent ( hipo_MPI_Datatype datatype , hipo_MPI_Aint * lb , hipo_MPI_Aint * extent )
{
#if !defined(DISABLE_MPI_Type_get_extent) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Aint lb_in;
    copyValue(lb_in, *lb);
    MPI_Aint extent_in;
    copyValue(extent_in, *extent);
    int ret = MPI_Type_get_extent(datatype_in, &lb_in, &extent_in);
    copyValue(*lb, lb_in);
    copyValue(*extent, extent_in);

    return ret;
#else
    printf("error: MPI_Type_get_extent is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_name ( hipo_MPI_Datatype datatype , char * type_name , int * resultlen )
{
#if !defined(DISABLE_MPI_Type_get_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_get_name(datatype_in, type_name, resultlen);

    return ret;
#else
    printf("error: MPI_Type_get_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_get_true_extent ( hipo_MPI_Datatype datatype , hipo_MPI_Aint * true_lb , hipo_MPI_Aint * true_extent )
{
#if !defined(DISABLE_MPI_Type_get_true_extent) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Aint true_lb_in;
    copyValue(true_lb_in, *true_lb);
    MPI_Aint true_extent_in;
    copyValue(true_extent_in, *true_extent);
    int ret = MPI_Type_get_true_extent(datatype_in, &true_lb_in, &true_extent_in);
    copyValue(*true_lb, true_lb_in);
    copyValue(*true_extent, true_extent_in);

    return ret;
#else
    printf("error: MPI_Type_get_true_extent is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_indexed ( int count , const int array_of_blocklengths [ ] , const int array_of_displacements [ ] , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_indexed) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_indexed(count, const_cast<int*>(array_of_blocklengths), const_cast<int*>(array_of_displacements), oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_indexed is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_match_size ( int typeclass , int size , hipo_MPI_Datatype * datatype )
{
#if !defined(DISABLE_MPI_Type_match_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, *datatype);
    int ret = MPI_Type_match_size(typeclass, size, &datatype_in);
    copyValue(*datatype, datatype_in);

    return ret;
#else
    printf("error: MPI_Type_match_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_set_name ( hipo_MPI_Datatype datatype , const char * type_name )
{
#if !defined(DISABLE_MPI_Type_set_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_set_name(datatype_in, const_cast<char*>(type_name));

    return ret;
#else
    printf("error: MPI_Type_set_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_size ( hipo_MPI_Datatype datatype , int * size )
{
#if !defined(DISABLE_MPI_Type_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Type_size(datatype_in, size);

    return ret;
#else
    printf("error: MPI_Type_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Type_vector ( int count , int blocklength , int stride , hipo_MPI_Datatype oldtype , hipo_MPI_Datatype * newtype )
{
#if !defined(DISABLE_MPI_Type_vector) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype oldtype_in;
    copyValue(oldtype_in, oldtype);
    MPI_Datatype newtype_in;
    copyValue(newtype_in, *newtype);
    int ret = MPI_Type_vector(count, blocklength, stride, oldtype_in, &newtype_in);
    copyValue(*newtype, newtype_in);

    return ret;
#else
    printf("error: MPI_Type_vector is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Unpack ( const void * inbuf , int insize , int * position , void * outbuf , int outcount , hipo_MPI_Datatype datatype , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Unpack) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Unpack(const_cast<void*>(inbuf), insize, position, outbuf, outcount, datatype_in, comm_in);

    return ret;
#else
    printf("error: MPI_Unpack is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Unpack_external ( const char datarep [ ] , const void * inbuf , hipo_MPI_Aint insize , hipo_MPI_Aint * position , void * outbuf , int outcount , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_Unpack_external) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Aint insize_in;
    copyValue(insize_in, insize);
    MPI_Aint position_in;
    copyValue(position_in, *position);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_Unpack_external(const_cast<char*>(datarep), const_cast<void*>(inbuf), insize_in, &position_in, outbuf, outcount, datatype_in);
    copyValue(*position, position_in);

    return ret;
#else
    printf("error: MPI_Unpack_external is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Add_error_class ( int * errorclass )
{
#if !defined(DISABLE_MPI_Add_error_class) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Add_error_class(errorclass);

    return ret;
#else
    printf("error: MPI_Add_error_class is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Add_error_code ( int errorclass , int * errorcode )
{
#if !defined(DISABLE_MPI_Add_error_code) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Add_error_code(errorclass, errorcode);

    return ret;
#else
    printf("error: MPI_Add_error_code is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Add_error_string ( int errorcode , const char * string )
{
#if !defined(DISABLE_MPI_Add_error_string) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Add_error_string(errorcode, const_cast<char*>(string));

    return ret;
#else
    printf("error: MPI_Add_error_string is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_call_errhandler ( hipo_MPI_Comm comm , int errorcode )
{
#if !defined(DISABLE_MPI_Comm_call_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Comm_call_errhandler(comm_in, errorcode);

    return ret;
#else
    printf("error: MPI_Comm_call_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_create_errhandler ( hipo_MPI_Comm_errhandler_function * comm_errhandler_fn , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_Comm_create_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm_errhandler_function * comm_errhandler_fn_in;
    copyValue(comm_errhandler_fn_in, comm_errhandler_fn);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_Comm_create_errhandler(comm_errhandler_fn_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_Comm_create_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_get_errhandler ( hipo_MPI_Comm comm , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_Comm_get_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_Comm_get_errhandler(comm_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_Comm_get_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_set_errhandler ( hipo_MPI_Comm comm , hipo_MPI_Errhandler errhandler )
{
#if !defined(DISABLE_MPI_Comm_set_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, errhandler);
    int ret = MPI_Comm_set_errhandler(comm_in, errhandler_in);

    return ret;
#else
    printf("error: MPI_Comm_set_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Errhandler_free ( hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_Errhandler_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_Errhandler_free(&errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_Errhandler_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Error_class ( int errorcode , int * errorclass )
{
#if !defined(DISABLE_MPI_Error_class) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Error_class(errorcode, errorclass);

    return ret;
#else
    printf("error: MPI_Error_class is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Error_string ( int errorcode , char * string , int * resultlen )
{
#if !defined(DISABLE_MPI_Error_string) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Error_string(errorcode, string, resultlen);

    return ret;
#else
    printf("error: MPI_Error_string is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_call_errhandler ( hipo_MPI_File fh , int errorcode )
{
#if !defined(DISABLE_MPI_File_call_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    int ret = MPI_File_call_errhandler(fh_in, errorcode);

    return ret;
#else
    printf("error: MPI_File_call_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_create_errhandler ( hipo_MPI_File_errhandler_function * file_errhandler_fn , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_File_create_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File_errhandler_function * file_errhandler_fn_in;
    copyValue(file_errhandler_fn_in, file_errhandler_fn);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_File_create_errhandler(file_errhandler_fn_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_File_create_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_errhandler ( hipo_MPI_File file , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_File_get_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File file_in;
    copyValue(file_in, file);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_File_get_errhandler(file_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_File_get_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_set_errhandler ( hipo_MPI_File file , hipo_MPI_Errhandler errhandler )
{
#if !defined(DISABLE_MPI_File_set_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File file_in;
    copyValue(file_in, file);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, errhandler);
    int ret = MPI_File_set_errhandler(file_in, errhandler_in);

    return ret;
#else
    printf("error: MPI_File_set_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_call_errhandler ( hipo_MPI_Win win , int errorcode )
{
#if !defined(DISABLE_MPI_Win_call_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_call_errhandler(win_in, errorcode);

    return ret;
#else
    printf("error: MPI_Win_call_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_create_errhandler ( hipo_MPI_Win_errhandler_function * win_errhandler_fn , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_Win_create_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win_errhandler_function * win_errhandler_fn_in;
    copyValue(win_errhandler_fn_in, win_errhandler_fn);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_Win_create_errhandler(win_errhandler_fn_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_Win_create_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_get_errhandler ( hipo_MPI_Win win , hipo_MPI_Errhandler * errhandler )
{
#if !defined(DISABLE_MPI_Win_get_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, *errhandler);
    int ret = MPI_Win_get_errhandler(win_in, &errhandler_in);
    copyValue(*errhandler, errhandler_in);

    return ret;
#else
    printf("error: MPI_Win_get_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_set_errhandler ( hipo_MPI_Win win , hipo_MPI_Errhandler errhandler )
{
#if !defined(DISABLE_MPI_Win_set_errhandler) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    MPI_Errhandler errhandler_in;
    copyValue(errhandler_in, errhandler);
    int ret = MPI_Win_set_errhandler(win_in, errhandler_in);

    return ret;
#else
    printf("error: MPI_Win_set_errhandler is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_compare ( hipo_MPI_Group group1 , hipo_MPI_Group group2 , int * result )
{
#if !defined(DISABLE_MPI_Group_compare) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group1_in;
    copyValue(group1_in, group1);
    MPI_Group group2_in;
    copyValue(group2_in, group2);
    int ret = MPI_Group_compare(group1_in, group2_in, result);

    return ret;
#else
    printf("error: MPI_Group_compare is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_difference ( hipo_MPI_Group group1 , hipo_MPI_Group group2 , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_difference) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group1_in;
    copyValue(group1_in, group1);
    MPI_Group group2_in;
    copyValue(group2_in, group2);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_difference(group1_in, group2_in, &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_difference is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_excl ( hipo_MPI_Group group , int n , const int ranks [ ] , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_excl) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_excl(group_in, n, const_cast<int*>(ranks), &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_excl is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_free ( hipo_MPI_Group * group )
{
#if !defined(DISABLE_MPI_Group_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, *group);
    int ret = MPI_Group_free(&group_in);
    copyValue(*group, group_in);

    return ret;
#else
    printf("error: MPI_Group_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_incl ( hipo_MPI_Group group , int n , const int ranks [ ] , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_incl) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_incl(group_in, n, const_cast<int*>(ranks), &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_incl is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_intersection ( hipo_MPI_Group group1 , hipo_MPI_Group group2 , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_intersection) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group1_in;
    copyValue(group1_in, group1);
    MPI_Group group2_in;
    copyValue(group2_in, group2);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_intersection(group1_in, group2_in, &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_intersection is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_range_excl ( hipo_MPI_Group group , int n , int ranges [ ] [ 3 ] , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_range_excl) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_range_excl(group_in, n, ranges, &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_range_excl is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_range_incl ( hipo_MPI_Group group , int n , int ranges [ ] [ 3 ] , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_range_incl) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_range_incl(group_in, n, ranges, &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_range_incl is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_rank ( hipo_MPI_Group group , int * rank )
{
#if !defined(DISABLE_MPI_Group_rank) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    int ret = MPI_Group_rank(group_in, rank);

    return ret;
#else
    printf("error: MPI_Group_rank is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_size ( hipo_MPI_Group group , int * size )
{
#if !defined(DISABLE_MPI_Group_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    int ret = MPI_Group_size(group_in, size);

    return ret;
#else
    printf("error: MPI_Group_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_translate_ranks ( hipo_MPI_Group group1 , int n , const int ranks1 [ ] , hipo_MPI_Group group2 , int ranks2 [ ] )
{
#if !defined(DISABLE_MPI_Group_translate_ranks) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group1_in;
    copyValue(group1_in, group1);
    MPI_Group group2_in;
    copyValue(group2_in, group2);
    int ret = MPI_Group_translate_ranks(group1_in, n, const_cast<int*>(ranks1), group2_in, ranks2);

    return ret;
#else
    printf("error: MPI_Group_translate_ranks is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Group_union ( hipo_MPI_Group group1 , hipo_MPI_Group group2 , hipo_MPI_Group * newgroup )
{
#if !defined(DISABLE_MPI_Group_union) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group1_in;
    copyValue(group1_in, group1);
    MPI_Group group2_in;
    copyValue(group2_in, group2);
    MPI_Group newgroup_in;
    copyValue(newgroup_in, *newgroup);
    int ret = MPI_Group_union(group1_in, group2_in, &newgroup_in);
    copyValue(*newgroup, newgroup_in);

    return ret;
#else
    printf("error: MPI_Group_union is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_create ( hipo_MPI_Info * info )
{
#if !defined(DISABLE_MPI_Info_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, *info);
    int ret = MPI_Info_create(&info_in);
    copyValue(*info, info_in);

    return ret;
#else
    printf("error: MPI_Info_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_delete ( hipo_MPI_Info info , const char * key )
{
#if !defined(DISABLE_MPI_Info_delete) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_delete(info_in, const_cast<char*>(key));

    return ret;
#else
    printf("error: MPI_Info_delete is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_dup ( hipo_MPI_Info info , hipo_MPI_Info * newinfo )
{
#if !defined(DISABLE_MPI_Info_dup) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_Info newinfo_in;
    copyValue(newinfo_in, *newinfo);
    int ret = MPI_Info_dup(info_in, &newinfo_in);
    copyValue(*newinfo, newinfo_in);

    return ret;
#else
    printf("error: MPI_Info_dup is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_free ( hipo_MPI_Info * info )
{
#if !defined(DISABLE_MPI_Info_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, *info);
    int ret = MPI_Info_free(&info_in);
    copyValue(*info, info_in);

    return ret;
#else
    printf("error: MPI_Info_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_get ( hipo_MPI_Info info , const char * key , int valuelen , char * value , int * flag )
{
#if !defined(DISABLE_MPI_Info_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_get(info_in, const_cast<char*>(key), valuelen, value, flag);

    return ret;
#else
    printf("error: MPI_Info_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_get_nkeys ( hipo_MPI_Info info , int * nkeys )
{
#if !defined(DISABLE_MPI_Info_get_nkeys) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_get_nkeys(info_in, nkeys);

    return ret;
#else
    printf("error: MPI_Info_get_nkeys is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_get_nthkey ( hipo_MPI_Info info , int n , char * key )
{
#if !defined(DISABLE_MPI_Info_get_nthkey) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_get_nthkey(info_in, n, key);

    return ret;
#else
    printf("error: MPI_Info_get_nthkey is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_get_valuelen ( hipo_MPI_Info info , const char * key , int * valuelen , int * flag )
{
#if !defined(DISABLE_MPI_Info_get_valuelen) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_get_valuelen(info_in, const_cast<char*>(key), valuelen, flag);

    return ret;
#else
    printf("error: MPI_Info_get_valuelen is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Info_set ( hipo_MPI_Info info , const char * key , const char * value )
{
#if !defined(DISABLE_MPI_Info_set) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Info_set(info_in, const_cast<char*>(key), const_cast<char*>(value));

    return ret;
#else
    printf("error: MPI_Info_set is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Abort ( hipo_MPI_Comm comm , int errorcode )
{
#if !defined(DISABLE_MPI_Abort) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Abort(comm_in, errorcode);

    return ret;
#else
    printf("error: MPI_Abort is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Finalize ( void )
{
#if !defined(DISABLE_MPI_Finalize) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Finalize();

    return ret;
#else
    printf("error: MPI_Finalize is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Finalized ( int * flag )
{
#if !defined(DISABLE_MPI_Finalized) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Finalized(flag);

    return ret;
#else
    printf("error: MPI_Finalized is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Init ( int * argc , char * * * argv )
{
#if !defined(DISABLE_MPI_Init) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Init(argc, argv);

    return ret;
#else
    printf("error: MPI_Init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Init_thread ( int * argc , char * * * argv , int required , int * provided )
{
#if !defined(DISABLE_MPI_Init_thread) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Init_thread(argc, argv, required, provided);

    return ret;
#else
    printf("error: MPI_Init_thread is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Initialized ( int * flag )
{
#if !defined(DISABLE_MPI_Initialized) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Initialized(flag);

    return ret;
#else
    printf("error: MPI_Initialized is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Is_thread_main ( int * flag )
{
#if !defined(DISABLE_MPI_Is_thread_main) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Is_thread_main(flag);

    return ret;
#else
    printf("error: MPI_Is_thread_main is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Query_thread ( int * provided )
{
#if !defined(DISABLE_MPI_Query_thread) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Query_thread(provided);

    return ret;
#else
    printf("error: MPI_Query_thread is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get_processor_name ( char * name , int * resultlen )
{
#if !defined(DISABLE_MPI_Get_processor_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Get_processor_name(name, resultlen);

    return ret;
#else
    printf("error: MPI_Get_processor_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get_version ( int * version , int * subversion )
{
#if !defined(DISABLE_MPI_Get_version) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Get_version(version, subversion);

    return ret;
#else
    printf("error: MPI_Get_version is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Pcontrol ( const int level , ... )
{
#if !defined(DISABLE_MPI_Pcontrol) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Pcontrol(level);

    return ret;
#else
    printf("error: MPI_Pcontrol is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Op_commutative ( hipo_MPI_Op op , int * commute )
{
#if !defined(DISABLE_MPI_Op_commutative) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op op_in;
    copyValue(op_in, op);
    int ret = MPI_Op_commutative(op_in, commute);

    return ret;
#else
    printf("error: MPI_Op_commutative is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Op_create ( hipo_MPI_User_function * user_fn , int commute , hipo_MPI_Op * op )
{
#if !defined(DISABLE_MPI_Op_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_User_function * user_fn_in;
    copyValue(user_fn_in, user_fn);
    MPI_Op op_in;
    copyValue(op_in, *op);
    int ret = MPI_Op_create(user_fn_in, commute, &op_in);
    copyValue(*op, op_in);

    return ret;
#else
    printf("error: MPI_Op_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Op_free ( hipo_MPI_Op * op )
{
#if !defined(DISABLE_MPI_Op_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Op op_in;
    copyValue(op_in, *op);
    int ret = MPI_Op_free(&op_in);
    copyValue(*op, op_in);

    return ret;
#else
    printf("error: MPI_Op_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Bsend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Bsend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Bsend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in);

    return ret;
#else
    printf("error: MPI_Bsend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Bsend_init ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Bsend_init) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Bsend_init(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Bsend_init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Buffer_attach ( void * buffer , int size )
{
#if !defined(DISABLE_MPI_Buffer_attach) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Buffer_attach(buffer, size);

    return ret;
#else
    printf("error: MPI_Buffer_attach is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Buffer_detach ( void * buffer_addr , int * size )
{
#if !defined(DISABLE_MPI_Buffer_detach) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Buffer_detach(buffer_addr, size);

    return ret;
#else
    printf("error: MPI_Buffer_detach is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Ibsend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Ibsend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Ibsend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Ibsend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Iprobe ( int source , int tag , hipo_MPI_Comm comm , int * flag , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Iprobe) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Iprobe(source, tag, comm_in, flag, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Iprobe is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Irecv ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Irecv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Irecv(buf, count, datatype_in, source, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Irecv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Irsend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Irsend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Irsend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Irsend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Isend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Isend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Isend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Isend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Issend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Issend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Issend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Issend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Probe ( int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Probe) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Probe(source, tag, comm_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Probe is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Recv ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Recv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Recv(buf, count, datatype_in, source, tag, comm_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Recv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Recv_init ( void * buf , int count , hipo_MPI_Datatype datatype , int source , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Recv_init) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Recv_init(buf, count, datatype_in, source, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Recv_init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Rsend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Rsend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Rsend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in);

    return ret;
#else
    printf("error: MPI_Rsend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Rsend_init ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Rsend_init) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Rsend_init(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Rsend_init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Send ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Send) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Send(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in);

    return ret;
#else
    printf("error: MPI_Send is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Send_init ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Send_init) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Send_init(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Send_init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Sendrecv ( const void * sendbuf , int sendcount , hipo_MPI_Datatype sendtype , int dest , int sendtag , void * recvbuf , int recvcount , hipo_MPI_Datatype recvtype , int source , int recvtag , hipo_MPI_Comm comm , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Sendrecv) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype sendtype_in;
    copyValue(sendtype_in, sendtype);
    MPI_Datatype recvtype_in;
    copyValue(recvtype_in, recvtype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Sendrecv(const_cast<void*>(sendbuf), sendcount, sendtype_in, dest, sendtag, recvbuf, recvcount, recvtype_in, source, recvtag, comm_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Sendrecv is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Sendrecv_replace ( void * buf , int count , hipo_MPI_Datatype datatype , int dest , int sendtag , int source , int recvtag , hipo_MPI_Comm comm , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Sendrecv_replace) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Sendrecv_replace(buf, count, datatype_in, dest, sendtag, source, recvtag, comm_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Sendrecv_replace is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Ssend ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm )
{
#if !defined(DISABLE_MPI_Ssend) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Ssend(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in);

    return ret;
#else
    printf("error: MPI_Ssend is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Ssend_init ( const void * buf , int count , hipo_MPI_Datatype datatype , int dest , int tag , hipo_MPI_Comm comm , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Ssend_init) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Ssend_init(const_cast<void*>(buf), count, datatype_in, dest, tag, comm_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Ssend_init is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cancel ( hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Cancel) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Cancel(&request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Cancel is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Grequest_complete ( hipo_MPI_Request request )
{
#if !defined(DISABLE_MPI_Grequest_complete) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, request);
    int ret = MPI_Grequest_complete(request_in);

    return ret;
#else
    printf("error: MPI_Grequest_complete is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Grequest_start ( hipo_MPI_Grequest_query_function * query_fn , hipo_MPI_Grequest_free_function * free_fn , hipo_MPI_Grequest_cancel_function * cancel_fn , void * extra_state , hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Grequest_start) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Grequest_query_function * query_fn_in;
    copyValue(query_fn_in, query_fn);
    MPI_Grequest_free_function * free_fn_in;
    copyValue(free_fn_in, free_fn);
    MPI_Grequest_cancel_function * cancel_fn_in;
    copyValue(cancel_fn_in, cancel_fn);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Grequest_start(query_fn_in, free_fn_in, cancel_fn_in, extra_state, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Grequest_start is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Request_free ( hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Request_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Request_free(&request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Request_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Request_get_status ( hipo_MPI_Request request , int * flag , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Request_get_status) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, request);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Request_get_status(request_in, flag, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Request_get_status is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Start ( hipo_MPI_Request * request )
{
#if !defined(DISABLE_MPI_Start) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_Start(&request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_Start is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Startall ( int count , hipo_MPI_Request array_of_requests [ ] )
{
#if !defined(DISABLE_MPI_Startall) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }
    int ret = MPI_Startall(count, array_of_requests_in);

    for (int i=0; i<count; i++) {
        copyValue(array_of_requests[i], array_of_requests_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Startall is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Status_set_cancelled ( hipo_MPI_Status * status , int flag )
{
#if !defined(DISABLE_MPI_Status_set_cancelled) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Status_set_cancelled(status_in, flag);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Status_set_cancelled is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Test ( hipo_MPI_Request * request , int * flag , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Test) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, *request);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Test(&request_in, flag, status_in);
    copyValue(*request, request_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Test is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Test_cancelled ( const hipo_MPI_Status * status , int * flag )
{
#if !defined(DISABLE_MPI_Test_cancelled) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Test_cancelled(status_in, flag);

    return ret;
#else
    printf("error: MPI_Test_cancelled is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Testall ( int count , hipo_MPI_Request array_of_requests [ ] , int * flag , hipo_MPI_Status array_of_statuses [ ] )
{
#if !defined(DISABLE_MPI_Testall) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status array_of_statuses_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_statuses_in[i], array_of_statuses[i]);
    }
    int ret = MPI_Testall(count, array_of_requests_in, flag, array_of_statuses_in);

    for (int i=0; i<count; i++) {
        copyValue(array_of_requests[i], array_of_requests_in[i]);
    }

    for (int i=0; i<count; i++) {
        copyValue(array_of_statuses[i], array_of_statuses_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Testall is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Testany ( int count , hipo_MPI_Request array_of_requests [ ] , int * indx , int * flag , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Testany) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Testany(count, array_of_requests_in, indx, flag, status_in);

    for (int i=0; i<count; i++) {
        copyValue(array_of_requests[i], array_of_requests_in[i]);
    }

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Testany is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Testsome ( int incount , hipo_MPI_Request array_of_requests [ ] , int * outcount , int array_of_indices [ ] , hipo_MPI_Status array_of_statuses [ ] )
{
#if !defined(DISABLE_MPI_Testsome) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[incount];
    for (int i=0; i<incount; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status array_of_statuses_in[incount];
    for (int i=0; i<incount; i++) {
        copyValue(array_of_statuses_in[i], array_of_statuses[i]);
    }
    int ret = MPI_Testsome(incount, array_of_requests_in, outcount, array_of_indices, array_of_statuses_in);

    for (int i=0; i<incount; i++) {
        copyValue(array_of_requests[i], array_of_requests_in[i]);
    }

    for (int i=0; i<incount; i++) {
        copyValue(array_of_statuses[i], array_of_statuses_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Testsome is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Wait ( hipo_MPI_Request * request , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Wait) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Request request_in;
    copyValue(request_in, *request);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Wait(&request_in, status_in);
    copyValue(*request, request_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Wait is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Waitall ( int count , hipo_MPI_Request array_of_requests [ ] , hipo_MPI_Status array_of_statuses [ ] )
{
#if !defined(DISABLE_MPI_Waitall) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status array_of_statuses_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_statuses_in[i], array_of_statuses[i]);
    }
    int ret = MPI_Waitall(count, array_of_requests_in, array_of_statuses_in);

    for (int i=0; i<count; i++) {
        copyValue(array_of_statuses[i], array_of_statuses_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Waitall is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Waitany ( int count , hipo_MPI_Request array_of_requests [ ] , int * indx , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_Waitany) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_Waitany(count, array_of_requests_in, indx, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_Waitany is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Waitsome ( int incount , hipo_MPI_Request array_of_requests [ ] , int * outcount , int array_of_indices [ ] , hipo_MPI_Status array_of_statuses [ ] )
{
#if !defined(DISABLE_MPI_Waitsome) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Request array_of_requests_in[incount];
    for (int i=0; i<incount; i++) {
        copyValue(array_of_requests_in[i], array_of_requests[i]);
    }

    MPI_Status array_of_statuses_in[incount];
    for (int i=0; i<incount; i++) {
        copyValue(array_of_statuses_in[i], array_of_statuses[i]);
    }
    int ret = MPI_Waitsome(incount, array_of_requests_in, outcount, array_of_indices, array_of_statuses_in);

    for (int i=0; i<incount; i++) {
        copyValue(array_of_statuses[i], array_of_statuses_in[i]);
    }

    return ret;
#else
    printf("error: MPI_Waitsome is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Accumulate ( const void * origin_addr , int origin_count , hipo_MPI_Datatype origin_datatype , int target_rank , hipo_MPI_Aint target_disp , int target_count , hipo_MPI_Datatype target_datatype , hipo_MPI_Op op , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Accumulate) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype origin_datatype_in;
    copyValue(origin_datatype_in, origin_datatype);
    MPI_Aint target_disp_in;
    copyValue(target_disp_in, target_disp);
    MPI_Datatype target_datatype_in;
    copyValue(target_datatype_in, target_datatype);
    MPI_Op op_in;
    copyValue(op_in, op);
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Accumulate(const_cast<void*>(origin_addr), origin_count, origin_datatype_in, target_rank, target_disp_in, target_count, target_datatype_in, op_in, win_in);

    return ret;
#else
    printf("error: MPI_Accumulate is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Alloc_mem ( hipo_MPI_Aint size , hipo_MPI_Info info , void * baseptr )
{
#if !defined(DISABLE_MPI_Alloc_mem) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Aint size_in;
    copyValue(size_in, size);
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Alloc_mem(size_in, info_in, baseptr);

    return ret;
#else
    printf("error: MPI_Alloc_mem is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Free_mem ( void * base )
{
#if !defined(DISABLE_MPI_Free_mem) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Free_mem(base);

    return ret;
#else
    printf("error: MPI_Free_mem is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Get ( void * origin_addr , int origin_count , hipo_MPI_Datatype origin_datatype , int target_rank , hipo_MPI_Aint target_disp , int target_count , hipo_MPI_Datatype target_datatype , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype origin_datatype_in;
    copyValue(origin_datatype_in, origin_datatype);
    MPI_Aint target_disp_in;
    copyValue(target_disp_in, target_disp);
    MPI_Datatype target_datatype_in;
    copyValue(target_datatype_in, target_datatype);
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Get(origin_addr, origin_count, origin_datatype_in, target_rank, target_disp_in, target_count, target_datatype_in, win_in);

    return ret;
#else
    printf("error: MPI_Get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Put ( const void * origin_addr , int origin_count , hipo_MPI_Datatype origin_datatype , int target_rank , hipo_MPI_Aint target_disp , int target_count , hipo_MPI_Datatype target_datatype , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Put) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datatype origin_datatype_in;
    copyValue(origin_datatype_in, origin_datatype);
    MPI_Aint target_disp_in;
    copyValue(target_disp_in, target_disp);
    MPI_Datatype target_datatype_in;
    copyValue(target_datatype_in, target_datatype);
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Put(const_cast<void*>(origin_addr), origin_count, origin_datatype_in, target_rank, target_disp_in, target_count, target_datatype_in, win_in);

    return ret;
#else
    printf("error: MPI_Put is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_complete ( hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_complete) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_complete(win_in);

    return ret;
#else
    printf("error: MPI_Win_complete is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_create ( void * base , hipo_MPI_Aint size , int disp_unit , hipo_MPI_Info info , hipo_MPI_Comm comm , hipo_MPI_Win * win )
{
#if !defined(DISABLE_MPI_Win_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Aint size_in;
    copyValue(size_in, size);
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Win win_in;
    copyValue(win_in, *win);
    int ret = MPI_Win_create(base, size_in, disp_unit, info_in, comm_in, &win_in);
    copyValue(*win, win_in);

    return ret;
#else
    printf("error: MPI_Win_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_fence ( int assert , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_fence) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_fence(assert, win_in);

    return ret;
#else
    printf("error: MPI_Win_fence is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_free ( hipo_MPI_Win * win )
{
#if !defined(DISABLE_MPI_Win_free) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, *win);
    int ret = MPI_Win_free(&win_in);
    copyValue(*win, win_in);

    return ret;
#else
    printf("error: MPI_Win_free is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_get_group ( hipo_MPI_Win win , hipo_MPI_Group * group )
{
#if !defined(DISABLE_MPI_Win_get_group) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    MPI_Group group_in;
    copyValue(group_in, *group);
    int ret = MPI_Win_get_group(win_in, &group_in);
    copyValue(*group, group_in);

    return ret;
#else
    printf("error: MPI_Win_get_group is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_get_name ( hipo_MPI_Win win , char * win_name , int * resultlen )
{
#if !defined(DISABLE_MPI_Win_get_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_get_name(win_in, win_name, resultlen);

    return ret;
#else
    printf("error: MPI_Win_get_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_lock ( int lock_type , int rank , int assert , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_lock) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_lock(lock_type, rank, assert, win_in);

    return ret;
#else
    printf("error: MPI_Win_lock is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_post ( hipo_MPI_Group group , int assert , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_post) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_post(group_in, assert, win_in);

    return ret;
#else
    printf("error: MPI_Win_post is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_set_name ( hipo_MPI_Win win , const char * win_name )
{
#if !defined(DISABLE_MPI_Win_set_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_set_name(win_in, const_cast<char*>(win_name));

    return ret;
#else
    printf("error: MPI_Win_set_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_start ( hipo_MPI_Group group , int assert , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_start) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Group group_in;
    copyValue(group_in, group);
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_start(group_in, assert, win_in);

    return ret;
#else
    printf("error: MPI_Win_start is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_test ( hipo_MPI_Win win , int * flag )
{
#if !defined(DISABLE_MPI_Win_test) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_test(win_in, flag);

    return ret;
#else
    printf("error: MPI_Win_test is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_unlock ( int rank , hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_unlock) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_unlock(rank, win_in);

    return ret;
#else
    printf("error: MPI_Win_unlock is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Win_wait ( hipo_MPI_Win win )
{
#if !defined(DISABLE_MPI_Win_wait) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Win win_in;
    copyValue(win_in, win);
    int ret = MPI_Win_wait(win_in);

    return ret;
#else
    printf("error: MPI_Win_wait is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Close_port ( const char * port_name )
{
#if !defined(DISABLE_MPI_Close_port) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Close_port(const_cast<char*>(port_name));

    return ret;
#else
    printf("error: MPI_Close_port is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_accept ( const char * port_name , hipo_MPI_Info info , int root , hipo_MPI_Comm comm , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Comm_accept) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Comm_accept(const_cast<char*>(port_name), info_in, root, comm_in, &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Comm_accept is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_connect ( const char * port_name , hipo_MPI_Info info , int root , hipo_MPI_Comm comm , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Comm_connect) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Comm_connect(const_cast<char*>(port_name), info_in, root, comm_in, &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Comm_connect is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_disconnect ( hipo_MPI_Comm * comm )
{
#if !defined(DISABLE_MPI_Comm_disconnect) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, *comm);
    int ret = MPI_Comm_disconnect(&comm_in);
    copyValue(*comm, comm_in);

    return ret;
#else
    printf("error: MPI_Comm_disconnect is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_get_parent ( hipo_MPI_Comm * parent )
{
#if !defined(DISABLE_MPI_Comm_get_parent) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm parent_in;
    copyValue(parent_in, *parent);
    int ret = MPI_Comm_get_parent(&parent_in);
    copyValue(*parent, parent_in);

    return ret;
#else
    printf("error: MPI_Comm_get_parent is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_join ( int fd , hipo_MPI_Comm * intercomm )
{
#if !defined(DISABLE_MPI_Comm_join) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm intercomm_in;
    copyValue(intercomm_in, *intercomm);
    int ret = MPI_Comm_join(fd, &intercomm_in);
    copyValue(*intercomm, intercomm_in);

    return ret;
#else
    printf("error: MPI_Comm_join is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_spawn ( const char * command , char * argv [ ] , int maxprocs , hipo_MPI_Info info , int root , hipo_MPI_Comm comm , hipo_MPI_Comm * intercomm , int array_of_errcodes [ ] )
{
#if !defined(DISABLE_MPI_Comm_spawn) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm intercomm_in;
    copyValue(intercomm_in, *intercomm);
    int ret = MPI_Comm_spawn(const_cast<char*>(command), argv, maxprocs, info_in, root, comm_in, &intercomm_in, array_of_errcodes);
    copyValue(*intercomm, intercomm_in);

    return ret;
#else
    printf("error: MPI_Comm_spawn is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Comm_spawn_multiple ( int count , char * array_of_commands [ ] , char * * array_of_argv [ ] , const int array_of_maxprocs [ ] , const hipo_MPI_Info array_of_info [ ] , int root , hipo_MPI_Comm comm , hipo_MPI_Comm * intercomm , int array_of_errcodes [ ] )
{
#if !defined(DISABLE_MPI_Comm_spawn_multiple) && !defined(HIPO_MPI_DUMMY_IMPL)

    MPI_Info array_of_info_in[count];
    for (int i=0; i<count; i++) {
        copyValue(array_of_info_in[i], array_of_info[i]);
    }
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm intercomm_in;
    copyValue(intercomm_in, *intercomm);
    int ret = MPI_Comm_spawn_multiple(count, array_of_commands, array_of_argv, const_cast<int*>(array_of_maxprocs), array_of_info_in, root, comm_in, &intercomm_in, array_of_errcodes);
    copyValue(*intercomm, intercomm_in);

    return ret;
#else
    printf("error: MPI_Comm_spawn_multiple is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Lookup_name ( const char * service_name , hipo_MPI_Info info , char * port_name )
{
#if !defined(DISABLE_MPI_Lookup_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Lookup_name(const_cast<char*>(service_name), info_in, port_name);

    return ret;
#else
    printf("error: MPI_Lookup_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Open_port ( hipo_MPI_Info info , char * port_name )
{
#if !defined(DISABLE_MPI_Open_port) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Open_port(info_in, port_name);

    return ret;
#else
    printf("error: MPI_Open_port is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Publish_name ( const char * service_name , hipo_MPI_Info info , const char * port_name )
{
#if !defined(DISABLE_MPI_Publish_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Publish_name(const_cast<char*>(service_name), info_in, const_cast<char*>(port_name));

    return ret;
#else
    printf("error: MPI_Publish_name is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Unpublish_name ( const char * service_name , hipo_MPI_Info info , const char * port_name )
{
#if !defined(DISABLE_MPI_Unpublish_name) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_Unpublish_name(const_cast<char*>(service_name), info_in, const_cast<char*>(port_name));

    return ret;
#else
    printf("error: MPI_Unpublish_name is a dummy function\n");
    return 0;
#endif
}
double hipo_MPI_Wtick ( void )
{
#if !defined(DISABLE_MPI_Wtick) && !defined(HIPO_MPI_DUMMY_IMPL)
    double ret = MPI_Wtick();

    return ret;
#else
    printf("error: MPI_Wtick is a dummy function\n");
    return 0;
#endif
}
double hipo_MPI_Wtime ( void )
{
#if !defined(DISABLE_MPI_Wtime) && !defined(HIPO_MPI_DUMMY_IMPL)
    double ret = MPI_Wtime();

    return ret;
#else
    printf("error: MPI_Wtime is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_coords ( hipo_MPI_Comm comm , int rank , int maxdims , int coords [ ] )
{
#if !defined(DISABLE_MPI_Cart_coords) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cart_coords(comm_in, rank, maxdims, coords);

    return ret;
#else
    printf("error: MPI_Cart_coords is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_create ( hipo_MPI_Comm comm_old , int ndims , const int dims [ ] , const int periods [ ] , int reorder , hipo_MPI_Comm * comm_cart )
{
#if !defined(DISABLE_MPI_Cart_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_old_in;
    copyValue(comm_old_in, comm_old);
    MPI_Comm comm_cart_in;
    copyValue(comm_cart_in, *comm_cart);
    int ret = MPI_Cart_create(comm_old_in, ndims, const_cast<int*>(dims), const_cast<int*>(periods), reorder, &comm_cart_in);
    copyValue(*comm_cart, comm_cart_in);

    return ret;
#else
    printf("error: MPI_Cart_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_get ( hipo_MPI_Comm comm , int maxdims , int dims [ ] , int periods [ ] , int coords [ ] )
{
#if !defined(DISABLE_MPI_Cart_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cart_get(comm_in, maxdims, dims, periods, coords);

    return ret;
#else
    printf("error: MPI_Cart_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_map ( hipo_MPI_Comm comm , int ndims , const int dims [ ] , const int periods [ ] , int * newrank )
{
#if !defined(DISABLE_MPI_Cart_map) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cart_map(comm_in, ndims, const_cast<int*>(dims), const_cast<int*>(periods), newrank);

    return ret;
#else
    printf("error: MPI_Cart_map is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_rank ( hipo_MPI_Comm comm , const int coords [ ] , int * rank )
{
#if !defined(DISABLE_MPI_Cart_rank) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cart_rank(comm_in, const_cast<int*>(coords), rank);

    return ret;
#else
    printf("error: MPI_Cart_rank is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_shift ( hipo_MPI_Comm comm , int direction , int disp , int * rank_source , int * rank_dest )
{
#if !defined(DISABLE_MPI_Cart_shift) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cart_shift(comm_in, direction, disp, rank_source, rank_dest);

    return ret;
#else
    printf("error: MPI_Cart_shift is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cart_sub ( hipo_MPI_Comm comm , const int remain_dims [ ] , hipo_MPI_Comm * newcomm )
{
#if !defined(DISABLE_MPI_Cart_sub) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Comm newcomm_in;
    copyValue(newcomm_in, *newcomm);
    int ret = MPI_Cart_sub(comm_in, const_cast<int*>(remain_dims), &newcomm_in);
    copyValue(*newcomm, newcomm_in);

    return ret;
#else
    printf("error: MPI_Cart_sub is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Cartdim_get ( hipo_MPI_Comm comm , int * ndims )
{
#if !defined(DISABLE_MPI_Cartdim_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Cartdim_get(comm_in, ndims);

    return ret;
#else
    printf("error: MPI_Cartdim_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Dims_create ( int nnodes , int ndims , int dims [ ] )
{
#if !defined(DISABLE_MPI_Dims_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    int ret = MPI_Dims_create(nnodes, ndims, dims);

    return ret;
#else
    printf("error: MPI_Dims_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graph_create ( hipo_MPI_Comm comm_old , int nnodes , const int indx [ ] , const int edges [ ] , int reorder , hipo_MPI_Comm * comm_graph )
{
#if !defined(DISABLE_MPI_Graph_create) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_old_in;
    copyValue(comm_old_in, comm_old);
    MPI_Comm comm_graph_in;
    copyValue(comm_graph_in, *comm_graph);
    int ret = MPI_Graph_create(comm_old_in, nnodes, const_cast<int*>(indx), const_cast<int*>(edges), reorder, &comm_graph_in);
    copyValue(*comm_graph, comm_graph_in);

    return ret;
#else
    printf("error: MPI_Graph_create is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graph_get ( hipo_MPI_Comm comm , int maxindex , int maxedges , int indx [ ] , int edges [ ] )
{
#if !defined(DISABLE_MPI_Graph_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Graph_get(comm_in, maxindex, maxedges, indx, edges);

    return ret;
#else
    printf("error: MPI_Graph_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graph_map ( hipo_MPI_Comm comm , int nnodes , const int indx [ ] , const int edges [ ] , int * newrank )
{
#if !defined(DISABLE_MPI_Graph_map) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Graph_map(comm_in, nnodes, const_cast<int*>(indx), const_cast<int*>(edges), newrank);

    return ret;
#else
    printf("error: MPI_Graph_map is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graph_neighbors ( hipo_MPI_Comm comm , int rank , int maxneighbors , int neighbors [ ] )
{
#if !defined(DISABLE_MPI_Graph_neighbors) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Graph_neighbors(comm_in, rank, maxneighbors, neighbors);

    return ret;
#else
    printf("error: MPI_Graph_neighbors is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graph_neighbors_count ( hipo_MPI_Comm comm , int rank , int * nneighbors )
{
#if !defined(DISABLE_MPI_Graph_neighbors_count) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Graph_neighbors_count(comm_in, rank, nneighbors);

    return ret;
#else
    printf("error: MPI_Graph_neighbors_count is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Graphdims_get ( hipo_MPI_Comm comm , int * nnodes , int * nedges )
{
#if !defined(DISABLE_MPI_Graphdims_get) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Graphdims_get(comm_in, nnodes, nedges);

    return ret;
#else
    printf("error: MPI_Graphdims_get is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Topo_test ( hipo_MPI_Comm comm , int * status )
{
#if !defined(DISABLE_MPI_Topo_test) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    int ret = MPI_Topo_test(comm_in, status);

    return ret;
#else
    printf("error: MPI_Topo_test is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_open ( hipo_MPI_Comm comm , const char * filename , int amode , hipo_MPI_Info info , hipo_MPI_File * fh )
{
#if !defined(DISABLE_MPI_File_open) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Comm comm_in;
    copyValue(comm_in, comm);
    MPI_Info info_in;
    copyValue(info_in, info);
    MPI_File fh_in;
    copyValue(fh_in, *fh);
    int ret = MPI_File_open(comm_in, const_cast<char*>(filename), amode, info_in, &fh_in);
    copyValue(*fh, fh_in);

    return ret;
#else
    printf("error: MPI_File_open is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_close ( hipo_MPI_File * fh )
{
#if !defined(DISABLE_MPI_File_close) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, *fh);
    int ret = MPI_File_close(&fh_in);
    copyValue(*fh, fh_in);

    return ret;
#else
    printf("error: MPI_File_close is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_delete ( const char * filename , hipo_MPI_Info info )
{
#if !defined(DISABLE_MPI_File_delete) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_File_delete(const_cast<char*>(filename), info_in);

    return ret;
#else
    printf("error: MPI_File_delete is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_set_size ( hipo_MPI_File fh , hipo_MPI_Offset size )
{
#if !defined(DISABLE_MPI_File_set_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset size_in;
    copyValue(size_in, size);
    int ret = MPI_File_set_size(fh_in, size_in);

    return ret;
#else
    printf("error: MPI_File_set_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_preallocate ( hipo_MPI_File fh , hipo_MPI_Offset size )
{
#if !defined(DISABLE_MPI_File_preallocate) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset size_in;
    copyValue(size_in, size);
    int ret = MPI_File_preallocate(fh_in, size_in);

    return ret;
#else
    printf("error: MPI_File_preallocate is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_size ( hipo_MPI_File fh , hipo_MPI_Offset * size )
{
#if !defined(DISABLE_MPI_File_get_size) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset size_in;
    copyValue(size_in, *size);
    int ret = MPI_File_get_size(fh_in, &size_in);
    copyValue(*size, size_in);

    return ret;
#else
    printf("error: MPI_File_get_size is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_group ( hipo_MPI_File fh , hipo_MPI_Group * group )
{
#if !defined(DISABLE_MPI_File_get_group) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Group group_in;
    copyValue(group_in, *group);
    int ret = MPI_File_get_group(fh_in, &group_in);
    copyValue(*group, group_in);

    return ret;
#else
    printf("error: MPI_File_get_group is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_amode ( hipo_MPI_File fh , int * amode )
{
#if !defined(DISABLE_MPI_File_get_amode) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    int ret = MPI_File_get_amode(fh_in, amode);

    return ret;
#else
    printf("error: MPI_File_get_amode is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_set_info ( hipo_MPI_File fh , hipo_MPI_Info info )
{
#if !defined(DISABLE_MPI_File_set_info) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_File_set_info(fh_in, info_in);

    return ret;
#else
    printf("error: MPI_File_set_info is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_info ( hipo_MPI_File fh , hipo_MPI_Info * info_used )
{
#if !defined(DISABLE_MPI_File_get_info) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Info info_used_in;
    copyValue(info_used_in, *info_used);
    int ret = MPI_File_get_info(fh_in, &info_used_in);
    copyValue(*info_used, info_used_in);

    return ret;
#else
    printf("error: MPI_File_get_info is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_set_view ( hipo_MPI_File fh , hipo_MPI_Offset disp , hipo_MPI_Datatype etype , hipo_MPI_Datatype filetype , const char * datarep , hipo_MPI_Info info )
{
#if !defined(DISABLE_MPI_File_set_view) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset disp_in;
    copyValue(disp_in, disp);
    MPI_Datatype etype_in;
    copyValue(etype_in, etype);
    MPI_Datatype filetype_in;
    copyValue(filetype_in, filetype);
    MPI_Info info_in;
    copyValue(info_in, info);
    int ret = MPI_File_set_view(fh_in, disp_in, etype_in, filetype_in, const_cast<char*>(datarep), info_in);

    return ret;
#else
    printf("error: MPI_File_set_view is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_view ( hipo_MPI_File fh , hipo_MPI_Offset * disp , hipo_MPI_Datatype * etype , hipo_MPI_Datatype * filetype , char * datarep )
{
#if !defined(DISABLE_MPI_File_get_view) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset disp_in;
    copyValue(disp_in, *disp);
    MPI_Datatype etype_in;
    copyValue(etype_in, *etype);
    MPI_Datatype filetype_in;
    copyValue(filetype_in, *filetype);
    int ret = MPI_File_get_view(fh_in, &disp_in, &etype_in, &filetype_in, datarep);
    copyValue(*disp, disp_in);
    copyValue(*etype, etype_in);
    copyValue(*filetype, filetype_in);

    return ret;
#else
    printf("error: MPI_File_get_view is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_at ( hipo_MPI_File fh , hipo_MPI_Offset offset , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_at) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_at(fh_in, offset_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_at is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_at_all ( hipo_MPI_File fh , hipo_MPI_Offset offset , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_at_all) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_at_all(fh_in, offset_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_at_all is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_at ( hipo_MPI_File fh , hipo_MPI_Offset offset , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_at) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_at(fh_in, offset_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_at is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_at_all ( hipo_MPI_File fh , hipo_MPI_Offset offset , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_at_all) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_at_all(fh_in, offset_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_at_all is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iread_at ( hipo_MPI_File fh , hipo_MPI_Offset offset , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iread_at) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iread_at(fh_in, offset_in, buf, count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iread_at is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iwrite_at ( hipo_MPI_File fh , hipo_MPI_Offset offset , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iwrite_at) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iwrite_at(fh_in, offset_in, const_cast<void*>(buf), count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iwrite_at is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read(fh_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_all ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_all) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_all(fh_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_all is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write(fh_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_all ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_all) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_all(fh_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_all is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iread ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iread) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iread(fh_in, buf, count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iread is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iwrite ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iwrite) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iwrite(fh_in, const_cast<void*>(buf), count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iwrite is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_seek ( hipo_MPI_File fh , hipo_MPI_Offset offset , int whence )
{
#if !defined(DISABLE_MPI_File_seek) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    int ret = MPI_File_seek(fh_in, offset_in, whence);

    return ret;
#else
    printf("error: MPI_File_seek is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_position ( hipo_MPI_File fh , hipo_MPI_Offset * offset )
{
#if !defined(DISABLE_MPI_File_get_position) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, *offset);
    int ret = MPI_File_get_position(fh_in, &offset_in);
    copyValue(*offset, offset_in);

    return ret;
#else
    printf("error: MPI_File_get_position is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_byte_offset ( hipo_MPI_File fh , hipo_MPI_Offset offset , hipo_MPI_Offset * disp )
{
#if !defined(DISABLE_MPI_File_get_byte_offset) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Offset disp_in;
    copyValue(disp_in, *disp);
    int ret = MPI_File_get_byte_offset(fh_in, offset_in, &disp_in);
    copyValue(*disp, disp_in);

    return ret;
#else
    printf("error: MPI_File_get_byte_offset is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_shared ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_shared(fh_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_shared ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_shared(fh_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iread_shared ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iread_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iread_shared(fh_in, buf, count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iread_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_iwrite_shared ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPIO_Request * request )
{
#if !defined(DISABLE_MPI_File_iwrite_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Request request_in;
    copyValue(request_in, *request);
    int ret = MPI_File_iwrite_shared(fh_in, const_cast<void*>(buf), count, datatype_in, &request_in);
    copyValue(*request, request_in);

    return ret;
#else
    printf("error: MPI_File_iwrite_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_ordered ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_ordered) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_ordered(fh_in, buf, count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_ordered is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_ordered ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_ordered) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_ordered(fh_in, const_cast<void*>(buf), count, datatype_in, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_ordered is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_seek_shared ( hipo_MPI_File fh , hipo_MPI_Offset offset , int whence )
{
#if !defined(DISABLE_MPI_File_seek_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    int ret = MPI_File_seek_shared(fh_in, offset_in, whence);

    return ret;
#else
    printf("error: MPI_File_seek_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_position_shared ( hipo_MPI_File fh , hipo_MPI_Offset * offset )
{
#if !defined(DISABLE_MPI_File_get_position_shared) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, *offset);
    int ret = MPI_File_get_position_shared(fh_in, &offset_in);
    copyValue(*offset, offset_in);

    return ret;
#else
    printf("error: MPI_File_get_position_shared is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_at_all_begin ( hipo_MPI_File fh , hipo_MPI_Offset offset , void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_read_at_all_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_read_at_all_begin(fh_in, offset_in, buf, count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_read_at_all_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_at_all_end ( hipo_MPI_File fh , void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_at_all_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_at_all_end(fh_in, buf, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_at_all_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_at_all_begin ( hipo_MPI_File fh , hipo_MPI_Offset offset , const void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_write_at_all_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Offset offset_in;
    copyValue(offset_in, offset);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_write_at_all_begin(fh_in, offset_in, const_cast<void*>(buf), count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_write_at_all_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_at_all_end ( hipo_MPI_File fh , const void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_at_all_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_at_all_end(fh_in, const_cast<void*>(buf), status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_at_all_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_all_begin ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_read_all_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_read_all_begin(fh_in, buf, count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_read_all_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_all_end ( hipo_MPI_File fh , void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_all_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_all_end(fh_in, buf, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_all_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_all_begin ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_write_all_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_write_all_begin(fh_in, const_cast<void*>(buf), count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_write_all_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_all_end ( hipo_MPI_File fh , const void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_all_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_all_end(fh_in, const_cast<void*>(buf), status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_all_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_ordered_begin ( hipo_MPI_File fh , void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_read_ordered_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_read_ordered_begin(fh_in, buf, count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_read_ordered_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_read_ordered_end ( hipo_MPI_File fh , void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_read_ordered_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_read_ordered_end(fh_in, buf, status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_read_ordered_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_ordered_begin ( hipo_MPI_File fh , const void * buf , int count , hipo_MPI_Datatype datatype )
{
#if !defined(DISABLE_MPI_File_write_ordered_begin) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    int ret = MPI_File_write_ordered_begin(fh_in, const_cast<void*>(buf), count, datatype_in);

    return ret;
#else
    printf("error: MPI_File_write_ordered_begin is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_write_ordered_end ( hipo_MPI_File fh , const void * buf , hipo_MPI_Status * status )
{
#if !defined(DISABLE_MPI_File_write_ordered_end) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);

    MPI_Status status_data;
    MPI_Status* status_in = MPI_STATUS_IGNORE;
    if (status != hipo_MPI_STATUS_IGNORE) {
        status_in = &status_data;
        copyValue(status_in, status);
    }
    int ret = MPI_File_write_ordered_end(fh_in, const_cast<void*>(buf), status_in);

    if (status != hipo_MPI_STATUS_IGNORE) {
        copyValue(status, status_in);
    }

    return ret;
#else
    printf("error: MPI_File_write_ordered_end is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_type_extent ( hipo_MPI_File fh , hipo_MPI_Datatype datatype , hipo_MPI_Aint * extent )
{
#if !defined(DISABLE_MPI_File_get_type_extent) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    MPI_Datatype datatype_in;
    copyValue(datatype_in, datatype);
    MPI_Aint extent_in;
    copyValue(extent_in, *extent);
    int ret = MPI_File_get_type_extent(fh_in, datatype_in, &extent_in);
    copyValue(*extent, extent_in);

    return ret;
#else
    printf("error: MPI_File_get_type_extent is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_Register_datarep ( const char * datarep , hipo_MPI_Datarep_conversion_function * read_conversion_fn , hipo_MPI_Datarep_conversion_function * write_conversion_fn , hipo_MPI_Datarep_extent_function * dtype_file_extent_fn , void * extra_state )
{
#if !defined(DISABLE_MPI_Register_datarep) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Datarep_conversion_function * read_conversion_fn_in;
    copyValue(read_conversion_fn_in, read_conversion_fn);
    MPI_Datarep_conversion_function * write_conversion_fn_in;
    copyValue(write_conversion_fn_in, write_conversion_fn);
    MPI_Datarep_extent_function * dtype_file_extent_fn_in;
    copyValue(dtype_file_extent_fn_in, dtype_file_extent_fn);
    int ret = MPI_Register_datarep(const_cast<char*>(datarep), read_conversion_fn_in, write_conversion_fn_in, dtype_file_extent_fn_in, extra_state);

    return ret;
#else
    printf("error: MPI_Register_datarep is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_set_atomicity ( hipo_MPI_File fh , int flag )
{
#if !defined(DISABLE_MPI_File_set_atomicity) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    int ret = MPI_File_set_atomicity(fh_in, flag);

    return ret;
#else
    printf("error: MPI_File_set_atomicity is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_get_atomicity ( hipo_MPI_File fh , int * flag )
{
#if !defined(DISABLE_MPI_File_get_atomicity) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    int ret = MPI_File_get_atomicity(fh_in, flag);

    return ret;
#else
    printf("error: MPI_File_get_atomicity is a dummy function\n");
    return 0;
#endif
}
int hipo_MPI_File_sync ( hipo_MPI_File fh )
{
#if !defined(DISABLE_MPI_File_sync) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File fh_in;
    copyValue(fh_in, fh);
    int ret = MPI_File_sync(fh_in);

    return ret;
#else
    printf("error: MPI_File_sync is a dummy function\n");
    return 0;
#endif
}
hipo_MPI_File hipo_MPI_File_f2c ( hipo_MPI_Fint file )
{
#if !defined(DISABLE_MPI_File_f2c) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_Fint file_in;
    copyValue(file_in, file);
    MPI_File ret = MPI_File_f2c(file_in);

    hipo_MPI_File ret_out;
    copyValue(ret_out, ret);
    return ret_out;
#else
    printf("error: MPI_File_f2c is a dummy function\n");
    return 0;
#endif
}
hipo_MPI_Fint hipo_MPI_File_c2f ( hipo_MPI_File file )
{
#if !defined(DISABLE_MPI_File_c2f) && !defined(HIPO_MPI_DUMMY_IMPL)
    MPI_File file_in;
    copyValue(file_in, file);
    MPI_Fint ret = MPI_File_c2f(file_in);

    hipo_MPI_Fint ret_out;
    copyValue(ret_out, ret);
    return ret_out;
#else
    printf("error: MPI_File_c2f is a dummy function\n");
    return 0;
#endif
}
