from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web import server

from netflow import server


class Options(usage.Options):
    optParameters = [
        ["port", "p", 9999, "The port to listen on."],
    ]

class NetflowServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "netflow"
    description = "Netflow - A netflow collector service"
    options = Options
    def makeService(self, options):
        return internet.UDPServer(
            int(options['port']),
            server.DatagramReceiver()
        )

serviceMaker = NetflowServiceMaker()
