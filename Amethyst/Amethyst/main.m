#import <UIKit/UIKit.h>
#import "AppDelegate.h"
#include "AmethystFileLog.h"
#include <sys/utsname.h>

int gAmethystFileLogReady = 0;
int gAmethystFileLogError = 0;
char gAmethystFileLogPath[PATH_MAX] = {0};

int main(int argc, char * argv[]) {
    NSString * appDelegateClassName;
    @autoreleasepool {
        NSString *documents = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
        [[NSFileManager defaultManager] createDirectoryAtPath:documents withIntermediateDirectories:YES attributes:nil error:nil];
        gAmethystFileLogError = AmethystFileLogStart([documents fileSystemRepresentation], gAmethystFileLogPath, sizeof(gAmethystFileLogPath));
        gAmethystFileLogReady = (gAmethystFileLogError == 0);
        if (gAmethystFileLogReady) {
            struct utsname device = {0};
            uname(&device);
            NSDictionary *info = [[NSBundle mainBundle] infoDictionary];
            fprintf(stderr, "[app] Amethyst %s (%s), device=%s, os=%s, uptime=%.3fs\n",
                    [info[@"CFBundleShortVersionString"] UTF8String],
                    [info[@"CFBundleVersion"] UTF8String], device.machine,
                    [[[NSProcessInfo processInfo] operatingSystemVersionString] UTF8String],
                    [[NSProcessInfo processInfo] systemUptime]);
        }
        appDelegateClassName = NSStringFromClass([AppDelegate class]);
    }
    return UIApplicationMain(argc, argv, nil, appDelegateClassName);
}
