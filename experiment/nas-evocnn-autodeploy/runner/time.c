#include <stdio.h>
#include <sys/time.h> // for gettimeofday()
#include <string.h>   // for memset()

int main()
{
    int i = 10000000;
    struct timeval start, end;  // define 2 struct timeval variables

    //-------------------------
    gettimeofday(&start, NULL); // get the beginning time
    //-------------------------

    // test code
    while(i)
    {
        i--;
    }

    //-------------------------
    gettimeofday(&end, NULL);  // get the end time
    //-------------------------

    long long total_time = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec); // get the run time by microsecond
    printf("total time is %lld us\n", total_time);
    total_time /= 1000; // get the run time by millisecond
    printf("total time is %lld ms\n", total_time);
    return 0;
}