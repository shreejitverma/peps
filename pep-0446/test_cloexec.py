import os, fcntl, sys, errno

def get_cloexec(fd):
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        return bool(flags & fcntl.FD_CLOEXEC)
    except IOError as err:
        return '<invalid file descriptor>' if err.errno == errno.EBADF else str(err)

def set_cloexec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)

def main():
    f = open(__file__, "rb")
    fd = f.fileno()
    print(f"initial state: fd={fd}, cloexec={get_cloexec(fd)}")


    pid = os.fork()
    if not pid:
        set_cloexec(fd)
        print(f"child process after fork, set cloexec: cloexec={get_cloexec(fd)}")
        child_argv = [sys.executable, __file__, str(fd),
                      'child process after exec']
        os.execv(child_argv[0], child_argv)

    os.waitpid(pid, 0)
    print(f"parent process after fork: cloexec={get_cloexec(fd)}")
    child_argv = [sys.executable, __file__, str(fd),
                  'parent process after exec']
    os.execv(child_argv[0], child_argv)

def after_exec():
    fd = int(sys.argv[1])
    name = sys.argv[2]
    print(f"{name}: fd={fd}, cloexec={get_cloexec(fd)}")
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    else:
        after_exec()

