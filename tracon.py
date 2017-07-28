import coloredlogs
import logging
from logging.handlers import TimedRotatingFileHandler, SysLogHandler
import os
import sys
from argparse import ArgumentParser
from time import sleep

class Monitor(object):
    def __init__(self):
        self.logger = logging.getLogger('p_mon')
        args = Monitor._process_args(sys.argv[1:])
        self.ip_to_ping = args.dest_ip
        self.p_timeout = args.ping_timeout
        self.is_online = Monitor._send_one_request(self.ip_to_ping,
                                                      self.p_timeout)

    @classmethod
    def _send_one_request(cls, ipaddr, time_out):
        response = os.system("ping -c 1 -W {to} {ia} > /dev/null 2>&1".\
                             format(to = time_out, ia = ipaddr))
        return True if response == 0 else False

    def main(self):
#        coloredlogs.install(level='DEBUG')
        if self.is_online: self.logger.debug("We are online!!!")
        stat_list =  [] # List for gathering packets statistic
        cnt_lp = 0

        print(stat_list)
        while True:
            sleep(1)
            self.logger.debug("Stat length: {0}".format(len(stat_list)))

            got_response = Monitor._send_one_request(self.ip_to_ping,
                                                     self.p_timeout)
            stat_list.insert(0,1) if got_response else stat_list.insert(0,0)

            if len(stat_list) < 30: continue # Need more data
            if len(stat_list) >= 301: stat_list.pop() # No need more data
            cnt_lp = [ l for l in stat_list[0:30] if l == 0 ]
            self.logger.debug("Lost Packets: {0}".format(len(cnt_lp)))

            if len(cnt_lp) >= ((float(len(stat_list[0:30]))/100)*50):
                self.logger.debug("Limit of lost packets reached")
                if not self.is_online:
                    self.logger.debug("Uplink is already Down, do nothing.")
                    continue
                if not 1 in stat_list[0:15]:
                    self.logger.warn("email/log explaining a lost ISP uplink")
                else:
                    self.logger.warn("email/log explaining "
                                      "bad channel quality")
                self.logger.warn("Stopping keepalived daemon...")
                self.logger.warn("Stopping VPN daemon...")
                self.is_online = False
            else:
                self.logger.debug("Lost packets are under the limit.")
                if self.is_online:
                    self.logger.debug("Uplink is already UP, do nothing.")
                    continue
                if not len(stat_list) >= 300:
                    self.logger.debug("Need more data for make a decision")
                    continue
                cnt_rp = [ r for r in stat_list[0:300] if r == 1 ]
                if len(cnt_rp) >= ((float(len(stat_list[0:300]))/100)*97):
                    self.logger.warn("Starting keepalived daemon...")
                    self.logger.warn("Starting VPN daemon...")
                    self.is_online = True
                else:
                    self.logger.debug("Rate of lost packets is still hight. Do"
                                      " nothing.")
                    continue


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
                                                     ' %(levelname)s %(message)s')))
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

