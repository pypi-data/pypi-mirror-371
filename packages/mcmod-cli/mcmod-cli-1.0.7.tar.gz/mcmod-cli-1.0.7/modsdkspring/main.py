# -*- coding: utf-8 -*-
import re
import sys
import os
import shutil
import json
import constants
import utils

# 获取当前包的根目录
packagePath = os.path.dirname(__file__)

def main():
    """
    控制台命令入口
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            print("Start initializing your Mod...")
            initMOD()
            print("Created successfully!")
        elif sys.argv[1] == 'import':
            print("Starting to create the __init__.py file.")
            initPy(sys.argv)
        else:
            print("Incorrect sub command.")
    else:
        print("Only mcmod was entered, please enter the sub command.")

def initMOD():
    """
    初始化 MOD 相关文件和文件夹（集成 Minecraft 项目结构）
    """
    # 只需要用户输入 Mod 名称，其他参数自动构造
    modName = raw_input("Please enter the Mod name (will be used as namespace and folder name):\n").strip()
    
    # 自动构造其他参数
    modDirName = modName  # 使用 mod 名称作为文件夹名称
    clientSystemName = modName + "ClientSystem"
    serverSystemName = modName + "ServerSystem"
    scriptsFolder = modName + "Scripts"
    
    # 生成UUIDs和随机文件夹名
    behaviorPackHeaderUuid = utils.generate_uuid()
    behaviorPackModuleUuid = utils.generate_uuid()
    resourcePackHeaderUuid = utils.generate_uuid()
    resourcePackModuleUuid = utils.generate_uuid()
    behaviorPackFolder = "behavior_pack_" + utils.generate_random_string(8)
    resourcePackFolder = "resource_pack_" + utils.generate_random_string(8)
    
    # 打印生成的信息
    print("Generated project information:")
    print("   Mod Name: {}".format(modName))
    print("   Client System: {}".format(clientSystemName))
    print("   Server System: {}".format(serverSystemName))
    print("   Scripts Folder: {}".format(scriptsFolder))
    print("   Behavior Pack: {}".format(behaviorPackFolder))
    print("   Resource Pack: {}".format(resourcePackFolder))
    print("Generated UUIDs:")
    print("   Behavior Pack Header: {}".format(behaviorPackHeaderUuid))
    print("   Behavior Pack Module: {}".format(behaviorPackModuleUuid))
    print("   Resource Pack Header: {}".format(resourcePackHeaderUuid))
    print("   Resource Pack Module: {}".format(resourcePackModuleUuid))
    
    # 得到项目的绝对路径
    modFullPath = os.path.join(os.getcwd(), modDirName)
    behaviorPackPath = os.path.join(modFullPath, behaviorPackFolder)
    resourcePackPath = os.path.join(modFullPath, resourcePackFolder)

    # 创建项目目录结构
    if not os.path.exists(modFullPath):
        os.makedirs(modFullPath)
    
    # 创建行为包目录结构
    os.makedirs(behaviorPackPath)
    os.makedirs(os.path.join(behaviorPackPath, "entities"))
    
    # 创建资源包目录结构  
    os.makedirs(resourcePackPath)
    os.makedirs(os.path.join(resourcePackPath, "textures"))
    
    # 创建 .gitkeep 文件
    with open(os.path.join(behaviorPackPath, "entities", ".gitkeep"), 'w') as f:
        f.write("")
    with open(os.path.join(resourcePackPath, "textures", ".gitkeep"), 'w') as f:
        f.write("")
    
    # 复制并处理行为包 manifest
    behaviorManifestTemplate = os.path.join(packagePath, constants.TEMPLATE_DIR_NAME, "manifest_behavior.txt")
    with open(behaviorManifestTemplate, 'r') as f:
        behaviorManifestContent = f.read()
    behaviorManifestContent = behaviorManifestContent.replace(constants.BEHAVIOR_PACK_HEADER_UUID, behaviorPackHeaderUuid)
    behaviorManifestContent = behaviorManifestContent.replace(constants.BEHAVIOR_PACK_MODULE_UUID, behaviorPackModuleUuid)
    with open(os.path.join(behaviorPackPath, "manifest.json"), 'w') as f:
        f.write(behaviorManifestContent)
    
    # 复制并处理资源包 manifest
    resourceManifestTemplate = os.path.join(packagePath, constants.TEMPLATE_DIR_NAME, "manifest_resource.txt")
    with open(resourceManifestTemplate, 'r') as f:
        resourceManifestContent = f.read()
    resourceManifestContent = resourceManifestContent.replace(constants.RESOURCE_PACK_HEADER_UUID, resourcePackHeaderUuid)
    resourceManifestContent = resourceManifestContent.replace(constants.RESOURCE_PACK_MODULE_UUID, resourcePackModuleUuid)
    with open(os.path.join(resourcePackPath, "manifest.json"), 'w') as f:
        f.write(resourceManifestContent)
    
    # 创建 world_behavior_packs.json 文件
    behaviorPacksConfig = [
        {
            "pack_id": behaviorPackHeaderUuid,
            "type": "Addon",
            "version": [0, 0, 1]
        }
    ]
    with open(os.path.join(modFullPath, "world_behavior_packs.json"), 'w') as f:
        f.write(json.dumps(behaviorPacksConfig, indent=4))
    
    # 创建 world_resource_packs.json 文件  
    resourcePacksConfig = [
        {
            "pack_id": resourcePackHeaderUuid,
            "type": "Addon", 
            "version": [0, 0, 1]
        }
    ]
    with open(os.path.join(modFullPath, "world_resource_packs.json"), 'w') as f:
        f.write(json.dumps(resourcePacksConfig, indent=4))
    
    # 在行为包中创建 MODSDKSpring 框架结构
    scriptsPath = os.path.join(behaviorPackPath, scriptsFolder)
    
    # 复制模板文件到脚本文件夹
    shutil.copytree(os.path.join(packagePath, constants.TEMPLATE_DIR_NAME), scriptsPath)
    
    # 复制 MODSDKSpring 框架到脚本文件夹的 plugins 目录
    pluginsPath = os.path.join(scriptsPath, constants.PLUGINS_DIR_NAME)
    if os.path.exists(os.path.join(packagePath, constants.PLUGINS_DIR_NAME)):
        if os.path.exists(pluginsPath):
            shutil.rmtree(pluginsPath)
        shutil.copytree(os.path.join(packagePath, constants.PLUGINS_DIR_NAME), pluginsPath)
    
    # 删除不需要的 manifest 模板文件
    manifestBehaviorFile = os.path.join(scriptsPath, "manifest_behavior.txt")
    if os.path.exists(manifestBehaviorFile):
        os.remove(manifestBehaviorFile)
    manifestResourceFile = os.path.join(scriptsPath, "manifest_resource.txt")
    if os.path.exists(manifestResourceFile):
        os.remove(manifestResourceFile)
    
    # 创建 ClientSystem 和 ServerSystem 子文件夹
    clientSystemDir = os.path.join(scriptsPath, "ClientSystem")
    serverSystemDir = os.path.join(scriptsPath, "ServerSystem")
    if not os.path.exists(clientSystemDir):
        os.makedirs(clientSystemDir)
    if not os.path.exists(serverSystemDir):
        os.makedirs(serverSystemDir)
    
    # 创建 __init__.py 文件
    with open(os.path.join(clientSystemDir, "__init__.py"), 'w') as f:
        f.write("")
    with open(os.path.join(serverSystemDir, "__init__.py"), 'w') as f:
        f.write("")
    
    # 替换模板文件中的占位符，并把所有 .txt 文件改为 .py
    for root, dirs, files in os.walk(scriptsPath):
        for file in files:
            if not file.endswith('.txt'):
                continue
            filePath = os.path.join(root, file)
            
            # 如果此文件不在 plugins 文件夹中，则进行文本替换
            if constants.PLUGINS_DIR_NAME not in root:
                with open(filePath, 'r') as f:
                    fstr = f.read()
                fstr = fstr.replace(constants.MOD_NAME, modName)
                fstr = fstr.replace(constants.MOD_DIR_NAME, modDirName)
                fstr = fstr.replace(constants.CLIENT_SYSTEM_NAME, clientSystemName)
                fstr = fstr.replace(constants.SERVER_SYSTEM_NAME, serverSystemName)
                fstr = fstr.replace(constants.SCRIPTS_FOLDER, scriptsFolder)
                with open(filePath, 'w') as f:
                    f.write(fstr)
            
            # 修改文件扩展名并处理特殊文件的位置
            fileName = file[:file.rfind('.')]
            
            # 特殊处理 ClientSystem 和 ServerSystem 文件
            if file == constants.CLIENT_SYSTEM_FILE_PATH:
                newFilePath = os.path.join(clientSystemDir, 'Main' + clientSystemName + '.py')
            elif file == constants.SERVER_SYSTEM_FILE_PATH:
                newFilePath = os.path.join(serverSystemDir, 'Main' + serverSystemName + '.py')
            else:
                newFilePath = os.path.join(root, fileName + '.py')
            
            os.rename(filePath, newFilePath)
    
    # 打印创建的项目结构
    print("\nProject structure created:")
    # print("   {}/".format(modDirName))
    # print("   ├── {}/".format(behaviorPackFolder))
    # print("   │   ├── manifest.json")
    # print("   │   ├── entities/")
    # print("   │   └── {}/".format(scriptsFolder))
    # print("   │       ├── components/")
    # print("   │       │   ├── client/")
    # print("   │       │   └── server/")
    # print("   │       ├── modCommon/")
    # print("   │       │   └── modConfig.py")
    # print("   │       ├── plugins/")
    # print("   │       ├── modMain.py")
    # print("   │       ├── {}.py".format(clientSystemName))
    # print("   │       └── {}.py".format(serverSystemName))
    # print("   └── {}/".format(resourcePackFolder))
    # print("       ├── manifest.json")
    # print("       └── textures/")

def initPy(args):
    """
    自动生成 __init__.py 文件，其中会自动 import 当前文件夹及其子文件夹中所有的类

    Args:
        args (list): 命令参数列表
    """
    # 要生成 __init__.py 文件的位置
    path = ""
    if len(args) == 2:
        # 取当前路径
        path = os.getcwd()
    elif len(args) == 4 and args[2] == '--path':
        # 取 --path 后的路径
        path = args[3]
    else:
        print("Usage: mcmod import --path \"path_to_directory\"")
        return
    
    pattern = r'class\s+([a-zA-Z][a-zA-Z0-9_]*)(\(.*\))?\s*:'
    pathRootDir = path[path.rfind(os.sep) + 1:]
    content = ""
    for root, dirs, files in os.walk(path):
        for file in files:
            # 过滤掉不是以 .py 结尾的文件，或者以 '_' 开头的文件
            if not file.endswith('.py') or file.startswith('_'):
                continue
            filePath = os.path.join(root, file)
            with open(filePath, 'r') as f:
                fstr = f.read()
            matches = re.findall(pattern, fstr)
            # 去掉扩展名 '.py'
            tempModulePath = filePath[:-3]
            # 去掉盘符
            tempModulePath = tempModulePath.split(":" + os.sep, 1)[1] if (":" + os.sep) in tempModulePath else tempModulePath
            # 去掉多余路径
            tempModulePath = tempModulePath[tempModulePath.find(pathRootDir + os.sep) + len(pathRootDir + os.sep):]
            # 将路径分隔符替换为 '.'
            tempModulePath = tempModulePath.replace(os.sep, '.')
            for className, superClassName in matches:
                content += ('from {} import {}\n'.format(tempModulePath, className))
    
    with open(os.path.join(path, '__init__.py'), 'w') as f:
        f.write(content)
    print("Successfully created the __init__.py file!")

