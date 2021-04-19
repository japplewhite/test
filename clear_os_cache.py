import sys
import time
import paramiko

from urlparse import urlparse

def clearOsCaches(endpoints):
    """ Clears the page cache, and the dentry and inode caches, for the specified hosts.

    Does this by ssh'ing to every host and writing to /proc/sys/vm/drop_caches on the host os. Each operation will be retried 5 times.

    Args:
        endpoints (string):
            The endpoints to clear, comma-separated.
    """
    
    #hosts = [urlparse(endpoint.strip()).hostname for endpoint in endpoints.split(',')]
    hosts = endpoints.split(",")
    
    
    
    print(hosts)
    for h in hosts:
        # stderr due to stdout causing problems in this context
        sys.stderr.write("Clearing OS caches for {}\n".format(h))

        # Try at least 5 times per host
        for i in range(5):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(h, username="admin", password="1234")

                sin, out, err = ssh.exec_command("echo bycast|sudo -S run-host-command 'sync; echo 3 > /proc/sys/vm/drop_caches'")
                # output likely won't be too large
                estr = err.read()
                if estr and estr != "[sudo] password for admin: ":
                    sys.stderr.write("Stderr output from exec_command: {}".format(estr))

                ssh.close()
                break
            except paramiko.AuthenticationException:
                sys.stderr.write("Could not authenticate when connecting to " % h)
            except Exception as e:
                sys.stderr.write("\nException {}: {}".format(str(type(e)), str(e)))
                time.sleep(3)
    print
    
if __name__ == "__main__":
    clearOsCaches(sys.argv[1])
