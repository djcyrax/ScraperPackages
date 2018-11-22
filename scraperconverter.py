# -*- coding: utf-8 -*-
# LambdaScrapers -> Seren scraper package generator.
# Must be run from within a "script.module.lambdascrapers" folder:
#
# eg:
# (open command prompt)
# cd script.module.lambdascrapers
# python GenerateLambdaSeren.py
# All Credit goes to reddit user NOT_doko-desuka for making this script!


import os
import re
import json
import zipfile
from io import BytesIO
from datetime import datetime

# Uncomment the block below in the future, when Seren comes with the zlib module
# and is able to decompress packages.
useCompression = False
'''try:
    # zlib module is optional, see if it's available.
    import zlib
    useCompression = True
except ImportError:
    # zlib module is not available, don't compress any files, just store them in the archive.
    useCompression = False'''


CURRENT_TIME = datetime.now()

# Package info.

PACKAGE_NAME = 'LambdaScrapers_Unofficial' # Also used as folder name.
PACKAGE_VERSION = '0.3_%s' % CURRENT_TIME.strftime('%Y-%b-%d')
PACKAGE_AUTHOR = 'Someone'

serenModulesFolder = 'providerModules'
serenProvidersFolder = 'providers'

lambdaFolderPath = os.path.join(os.path.dirname(__file__), 'lib', 'lambdascrapers')

importPattern = re.compile(r'(from\s*?)(((resources\s*?\.\s*?lib)|(lambdascrapers))\s*?\.?\s*?modules)')
importReplace = r'\1' + serenModulesFolder + '.' + PACKAGE_NAME

memoryBuffer = BytesIO()

with zipfile.ZipFile(memoryBuffer, 'w', zipfile.ZIP_DEFLATED if useCompression else zipfile.ZIP_STORED) as packageZIP:
    
    # 1) Pack the meta file.
    packageZIP.writestr(
        'meta.json', json.dumps({'name': PACKAGE_NAME, 'version': PACKAGE_VERSION, 'author': PACKAGE_AUTHOR})
    )

    # 2) Pack the provider modules.
    modulesPath = os.path.join(lambdaFolderPath, 'modules')
    for dirPath, dirNames, fileNames in os.walk(modulesPath):
        subFolder = dirPath.replace(modulesPath, '').strip(os.sep)
        zipModulesPath = os.path.join(serenModulesFolder, PACKAGE_NAME, subFolder)
        if (subFolder == '' or subFolder == 'cfscrape'):
            for fileName in fileNames:
                # On each script, replace references to 'lambdascrapers.modules' with a new path.
                moduleFile = open(os.path.join(dirPath, fileName), 'r', encoding='utf-8')
                script = moduleFile.read()
                moduleFile.close()
                script = re.sub(importPattern, importReplace, script)
                packageZIP.writestr(os.path.join(zipModulesPath, fileName), script)
        else:
            for fileName in fileNames:
                packageZIP.write(os.path.join(dirPath, fileName), os.path.join(zipModulesPath, fileName))
                

    # 3) Pack the provider scripts.
    # - Only the language folders are stored right now. The _DebridOnly folder is ignored.
    # - Any references to 'resources.lib.modules' in the scripts are changed to use 'providerModules' from above.
    languageFoldersPath = os.path.join(lambdaFolderPath, 'sources_ lambdascrapers')
    languageInitContent = '''def get_hosters(): import os; return (f[:-3] for f in os.listdir(os.path.join(os.path.dirname(__file__), 'hosters')) if f.endswith('.py') and 'init' not in f)\ndef get_torrent(): return ()'''
    zipProvidersPath = os.path.join(serenProvidersFolder, PACKAGE_NAME)
    for languageFolder in os.listdir(languageFoldersPath):
        if '.py' not in languageFolder and 'debrid' not in languageFolder.lower():
            # Make an __init__.py with some specific code on each language folder (Seren requirement).
            packageZIP.writestr(os.path.join(zipProvidersPath, languageFolder, '__init__.py'), languageInitContent)
            packageZIP.writestr(os.path.join(zipProvidersPath, languageFolder, 'hosters', '__init__.py'), '')
            
            languageFolderPath = os.path.join(languageFoldersPath, languageFolder)
            for entry in os.listdir(languageFolderPath):
                if entry.endswith('.py'):
                    providerFile = open(os.path.join(languageFolderPath, entry), 'r', encoding='utf-8')
                    script = providerFile.read()
                    providerFile.close()
                    # Replace references to 'resources.lib.modules' on each script with the new path.
                    script = re.sub(importPattern, importReplace, script)
                    packageZIP.writestr(os.path.join(zipProvidersPath, languageFolder, 'hosters', entry), script)
    packageZIP.writestr(os.path.join(zipProvidersPath, '__init__.py'), '')
            
# Write the final zip file outside of the 'with' context above, so the operations are complete.
outputPath = os.path.join(
    os.path.dirname(__file__), '%s_for_Seren_%s.zip' % (PACKAGE_NAME, CURRENT_TIME.strftime('%Y-%m-%d'))
)
with open(outputPath, 'wb') as output:
    memoryBuffer.seek(0)
    output.write(memoryBuffer.getvalue())

# Done. There should be a new '(PACKAGE_NAME)_for_Seren_(date).zip' in the same folder as this script.