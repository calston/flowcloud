from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.web import server

from sflow import server


class Options(usage.Options):
    optParameters = [
        ["port", "p", 6343, "The port to listen on."],
    ]

class SflowServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "sflow"
    description = "Sflow - A sflow collector service"
    options = Options
    def makeService(self, options):
        return internet.UDPServer(
            int(options['port']),
            server.DatagramReceiver()
        )

serviceMaker = SflowServiceMaker()
