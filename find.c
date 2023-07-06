#include <emmintrin.h>
#include <immintrin.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
typedef unsigned __int8  uint8_t;
//typedef unsigned __int16 uint16_t;
//typedef unsigned __int32 uint32_t;
//typedef unsigned __int64 uint64_t;
//typedef __int32  int32_t;
//typedef __int16  int16_t;
typedef __int8   int8_t;
//typedef __int64  int64_t;
#ifdef WIN32
#include <windows.h>
#else
//#include <sys/time.h>
#endif
#define _mm256_storeu2_m128i(/* __m128i* */ hiaddr, /* __m128i* */ loaddr, \
                             /* __m256i */ a) \
    do { \
        __m256i _a = (a); /* reference a only once in macro body */ \
        _mm_storeu_si128((loaddr), _mm256_castsi256_si128(_a)); \
        _mm_storeu_si128((hiaddr), _mm256_extractf128_si256(_a, 0x1)); \
    } while (0)

#define _mm_cmpgt_epu8(v0, v1) \
         _mm_cmpgt_epi8(_mm_xor_si128(v0, _mm_set1_epi8(-128)), \
                        _mm_xor_si128(v1, _mm_set1_epi8(-128)))

uint8_t Multiple_find(uint8_t * vec)
{                              
    __m128i mask = _mm_setr_epi8(vec[15], vec[16], vec[16], vec[17], vec[17], vec[17], vec[17], vec[18], vec[18], vec[18], vec[18], vec[18], vec[18], vec[18], vec[18], -1);
    int8_t com[16] = { 0 };//存储比较结果
    __m128i com_b = _mm_loadu_si128((__m128i*) & vec[0]);
    _mm_storeu_si128((__m128i*)com, _mm_cmpgt_epu8(mask, com_b));//将比较的结果储存到内存中

   /*查找*/
    uint8_t i = 1;
    i = 2 * i - 1 - com[i - 1];
    i = 2 * i - 1 - com[i];
    i = 2 * i - 1 - com[i + 2];
    i = 2 * i - 1 - com[i + 6];
    return i - 1;
}

//x86_64-w64-mingw32-gcc -m64 -shared -fPIC find.c -o find10.so -mavx -mavx2 -mfma -msse -msse2 -msse3
