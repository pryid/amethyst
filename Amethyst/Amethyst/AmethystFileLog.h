#ifndef AMETHYST_FILE_LOG_H
#define AMETHYST_FILE_LOG_H
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

extern int gAmethystFileLogReady;
extern int gAmethystFileLogError;
extern char gAmethystFileLogPath[PATH_MAX];

/* Ordinary app-container stdio logging. No privileges or target APIs. */
static inline int AmethystFileLogStart(const char *documents, char *result, size_t capacity) {
    char directory[PATH_MAX], filename[PATH_MAX], stamp[32];
    struct stat info;
    struct tm utc;
    time_t now = time(NULL);
    int descriptor = -1, previousOut = -1, previousErr = -1;
    int redirectedOut = 0, redirectedErr = 0;
    int savedError = EIO;
    if (documents == NULL || documents[0] != '/' || result == NULL || capacity == 0) return EINVAL;
    result[0] = '\0';
    int n = snprintf(directory, sizeof(directory), "%s/AmethystLogs", documents);
    if (n < 0 || (size_t)n >= sizeof(directory)) return ENAMETOOLONG;
    if (mkdir(directory, 0700) != 0 && errno != EEXIST) return errno;
    if (lstat(directory, &info) != 0) return errno;
    if (!S_ISDIR(info.st_mode)) return ENOTDIR;
    if (gmtime_r(&now, &utc) == NULL || strftime(stamp, sizeof(stamp), "%Y%m%dT%H%M%SZ", &utc) == 0) return EINVAL;
    for (unsigned attempt = 0; attempt < 32; attempt++) {
        n = snprintf(filename, sizeof(filename), "%s/Amethyst-%s-%ld-%u.log", directory, stamp, (long)getpid(), attempt);
        if (n < 0 || (size_t)n >= sizeof(filename) || (size_t)n >= capacity) return ENAMETOOLONG;
        int flags = O_WRONLY | O_CREAT | O_EXCL | O_APPEND;
#ifdef O_CLOEXEC
        flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
        flags |= O_NOFOLLOW;
#endif
#ifdef O_SYNC
        flags |= O_SYNC;
#endif
        descriptor = open(filename, flags, 0600);
        if (descriptor >= 0) break;
        if (errno != EEXIST) return errno;
    }
    if (descriptor < 0) return EEXIST;
    if (descriptor <= STDERR_FILENO) {
        int moved = fcntl(descriptor, F_DUPFD, 3);
        int moveError = errno;
        close(descriptor);
        descriptor = moved;
        if (descriptor < 0) return moveError;
    }
    static const char marker[] = "[filelogger] READY v1\n";
    if (write(descriptor, marker, sizeof(marker)-1) != (ssize_t)(sizeof(marker)-1) || fsync(descriptor) != 0) goto failure;
    previousOut = fcntl(STDOUT_FILENO, F_DUPFD, 3);
    if (previousOut < 0 && errno != EBADF) goto failure;
    previousErr = fcntl(STDERR_FILENO, F_DUPFD, 3);
    if (previousErr < 0 && errno != EBADF) goto failure;
    if (previousOut >= 0 && fflush(stdout) != 0) goto failure;
    if (previousErr >= 0 && fflush(stderr) != 0) goto failure;
    if (dup2(descriptor, STDOUT_FILENO) < 0) goto failure;
    redirectedOut = 1;
    if (dup2(descriptor, STDERR_FILENO) < 0) goto failure;
    redirectedErr = 1;
    clearerr(stdout); clearerr(stderr);
    if (setvbuf(stdout, NULL, _IONBF, 0) != 0 || setvbuf(stderr, NULL, _IONBF, 0) != 0) goto failure;
    if (fputs("[filelogger] stdout capture ready\n", stdout) == EOF || fputs("[filelogger] stderr capture ready\n", stderr) == EOF || fsync(descriptor) != 0) goto failure;
    memcpy(result, filename, (size_t)n+1);
    if (previousOut >= 0) close(previousOut);
    if (previousErr >= 0) close(previousErr);
    close(descriptor);
    return 0;
failure:
    savedError = errno ? errno : EIO;
    if (previousOut >= 0) { (void)dup2(previousOut, STDOUT_FILENO); close(previousOut); }
    else if (redirectedOut) close(STDOUT_FILENO);
    if (previousErr >= 0) { (void)dup2(previousErr, STDERR_FILENO); close(previousErr); }
    else if (redirectedErr) close(STDERR_FILENO);
    close(descriptor);
    return savedError;
}
#endif
