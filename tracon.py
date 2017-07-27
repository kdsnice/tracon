import coloredlogs
import logging
from logging.handlers import TimedRotatingFileHandler, SysLogHandler
import os
import sys
from argparse import ArgumentParser

class Monitor(object):
    def __init__(self):
        self.logger = logging.getLogger('p_mon')
        args = Monitor._process_args(sys.argv[1:])
        self.ip_to_ping = args.dest_ip
        self.p_timeout = args.ping_timeout
        self.is_online = Monitor._send_one_request(self.ip_to_ping,
                                                      self.p_timeout)
        self.stat_list = []

    @classmethod
    def _send_one_request(cls, ipaddr, time_out):
        response = os.system("ping -c 1 -W {to} {ia} > /dev/null 2>&1".\
                             format(to = time_out, ia = ipaddr))
        return True if response == 0 else False

    def main(self):
        coloredlogs.install(level='DEBUG')
        if self.is_online: self.logger.debug("We are online!!!")

    @classmethod
    def _process_args(cls, argv):
        arg_parser = ArgumentParser(description="Track Connection")
        arg_parser.add_argument('--dest-ip', required=True,
                                help="Destination IPv4 to ping")
        arg_parser.add_argument('--ping-timeout', required=False,
                                default=1,
                                help="Time to wait for a response, in seconds."
                                + " See -W option in Man for Ping")
        args = arg_parser.parse_args(argv)
        return args

def setup_logging():
    coloredlogs.install(level='INFO') 

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = TimedRotatingFileHandler(filename='log_tracon.log', when='midnight', utc=True)
    file_handler.setFormatter(logging.Formatter(fmt=('%(asctime)s %(name)s[%(process)d]'
                                                     ' %(levelname)s\n%(message)s\n')))
#    file_handler.setFormatter(logging.Formatter(fmt=('%(asctime)s %(hostname)s %(name)s[%(process)d]'
#                                                     ' %(levelname)s\n%(message)s\n')))
    root_logger.addHandler(file_handler)

    syslog_handler = SysLogHandler('/dev/log')
    syslog_handler.setFormatter(logging.Formatter(fmt='%(name)s[%(process)d]'
                                                  ' tracon-%(levelname)s %(message)s\n'))
    root_logger.addHandler(syslog_handler)

if __name__ == '__main__':
    setup_logging()
    Monitor().main()

