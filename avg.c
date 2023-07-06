#include <immintrin.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <windows.h>
typedef unsigned __int8  uint8_t;
#define N  16
uint8_t avg1[32] = { 0 };//�����Բ�����32�����ݵ�ƽ��ֵ���������յõ���32��ƽ��ֵ
__m256i avg256_1;
__m256i avg256_2;
int avx2Avg(uint8_t arr[][N],int step)
{
    //�����Բ�����32�����ݵ�ƽ��ֵ���������յõ���32��ƽ��ֵ
    avg256_1 = _mm256_loadu_si256((__m256i*) & arr[step][0]);
    avg256_2 = _mm256_loadu_si256((__m256i*) & arr[step][8]);

    avg256_1 = _mm256_avg_epu8(avg256_1, avg256_2);//��ƽ��
    avg256_2 = _mm256_alignr_epi8(avg256_1, avg256_1, 4);

    avg256_1 = _mm256_avg_epu8(avg256_1, avg256_2);//��ƽ��
    avg256_2 = _mm256_alignr_epi8(avg256_1, avg256_1, 2);

    avg256_1 = _mm256_avg_epu8(avg256_1, avg256_2);//��ƽ��
    avg256_2 = _mm256_alignr_epi8(avg256_1, avg256_1, 1);

    avg256_1 = _mm256_avg_epu8(avg256_1, avg256_2);//��ƽ��


    _mm256_storeu_si256((__m256i*)avg1, avg256_1);
    return avg1[0] * 16 - 16;
}
int cAdd(uint8_t arr[])
{
    int result = 0;
    for (int i = 0; i < 16; i++)
    {
        result += arr[i];
    }
    return result;
}
//x86_64-w64-mingw32-gcc -m64 -shared -fPIC avg.c -o avg24.so -mavx -mavx2 -mfma -msse -msse2 -msse3