# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from [SCRIPTS_FOLDER].plugins.MODSDKSpring.core.ListenEvent import ListenEvent
ServerSystem = serverApi.GetServerSystemCls()
compFactory = serverApi.GetEngineCompFactory()

@ListenEvent.InitServer
class [SERVER_SYSTEM_NAME](ServerSystem):

    def __init__(self, namespace, systemName):
        pass
