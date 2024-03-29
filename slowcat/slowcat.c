//#!/usr/bin/tcc

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char**argv){
    int c;
      useconds_t stime=10000; // defaults to 100 Hz

        if (argc>1) { // Argument is interperted as Hz
              stime=1000000/atoi(argv[1]);
                }

          setvbuf(stdout,NULL,_IONBF,0);

            while ((c=fgetc(stdin)) != EOF){
                  fputc(c,stdout);
                      usleep(stime);
                        }

              return 0;
}
