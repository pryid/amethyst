#include "AmethystFileLog.h"

int gAmethystFileLogReady;
int gAmethystFileLogError;
char gAmethystFileLogPath[PATH_MAX];

int main(int argc, char **argv) {
    if (argc != 3) return 99;
    if (strcmp(argv[2], "closed-out") == 0 || strcmp(argv[2], "closed-both") == 0) close(1);
    if (strcmp(argv[2], "closed-err") == 0 || strcmp(argv[2], "closed-both") == 0) close(2);
    size_t capacity = strcmp(argv[2], "short-capacity") == 0 ? 4 : sizeof(gAmethystFileLogPath);
    int error = AmethystFileLogStart(argv[1], gAmethystFileLogPath, capacity);
    if (strcmp(argv[2], "failure") == 0 || strcmp(argv[2], "short-capacity") == 0) return error ? 0 : 97;
    if (error) return 98;

    printf("fixture-out\n");
    fprintf(stderr, "fixture-err\n");
    unsigned char binary[] = {0, 255, 10};
    fwrite(binary, 1, sizeof(binary), stdout);
    if (strcmp(argv[2], "twice") == 0) {
        printf("first-file-only\n");
        if (AmethystFileLogStart(argv[1], gAmethystFileLogPath, sizeof(gAmethystFileLogPath))) return 96;
        printf("second-file-only\n");
    }
    _exit(0); /* The file must contain the output without an exit/atexit flush. */
}
