import uuid
from urllib.parse import urlparse
from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep.transports import Transport

class MipVms:
    uri = None
    sessionId = None
    serverCommandService = None
    loginInfo = None
    
    def __init__(self, uri):
        self.uri = urlparse(uri)
        pass
    def login(self, userName, password):
        self.sessionId = uuid.uuid4()
        session = Session()
        session.auth = (userName, password)
        port = self.uri.port if self.uri.port != None else 80 if self.uri.scheme == 'http' else 443
        self.serverCommandService = Client(f"{self.uri.scheme}://{self.uri.hostname}:{port}/ManagementServer/ServerCommandService.svc?wsdl", transport=Transport(session=session))
        self.renew_token()
        pass
    def renew_token(self, token=''):
        self.loginInfo = self.serverCommandService.service.Login(instanceId=self.sessionId, currentToken=token)
        pass
    def get_recorderstatuservice2(self, uri):
        uri = urlparse(uri)
        return Client(f"{uri.scheme}://{uri.hostname}:{uri.port}/RecorderStatusService/RecorderStatusService2.asmx?wsdl")


vms = MipVms('https://myserver')
vms.login('username', 'password')

config = vms.serverCommandService.service.GetConfiguration(vms.loginInfo.Token)
for info in config.Recorders.RecorderInfo:
    statusService = vms.get_recorderstatuservice2(info.WebServerUri)
    deviceIds = []
    for camera in info.Cameras.CameraInfo:
        deviceIds.append(camera.DeviceId)
    status = statusService.service.GetCurrentDeviceStatus(token=vms.loginInfo.Token, deviceIds=deviceIds)
    len(status.CameraDeviceStatusArray)

