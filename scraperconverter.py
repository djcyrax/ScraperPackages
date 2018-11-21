# -- coding utf-8 --
# LambdaScrapers - Seren scraper package generator.
# Must be run from within a script.module.lambdascrapers folder
#
# eg
# cd script.module.lambdascrapers
# python GenerateLambdaSeren.py


import os
import re
import json
import zipfile
from io import BytesIO
from datetime import datetime

# Uncomment the block below in the future, when Seren comes with the zlib module
# and is able to decompress packages.
useCompression = False
'''try
    # zlib module is optional, see if it's available.
    import zlib
    useCompression = True
except ImportError
    # zlib module is not available, don't compress any files, just store them in the archive.
    useCompression = False'''


CURRENT_TIME = datetime.now()

# Package info.

PACKAGE_NAME = 'LambdaScrapers' # Also used as folder name.
PACKAGE_VERSION = '0.2 %s' % CURRENT_TIME.strftime('%d %b %Y')
PACKAGE_AUTHOR = 'Someone'

lambdaFolder = os.path.join(os.getcwd(), 'lib', 'lambdascrapers')
serenModulesFolder = 'providerModules'
serenProvidersFolder = 'providers'
scriptsFolder = os.path.join(serenProvidersFolder, PACKAGE_NAME)

importPattern = re.compile(r'(froms)(((resourcess.slib)(lambdascrapers))s.smodules)')
importReplace = r'1' + serenModulesFolder + '.' + PACKAGE_NAME

memoryBuffer = BytesIO()
with zipfile.ZipFile(memoryBuffer, 'w', zipfile.ZIP_DEFLATED if useCompression else zipfile.ZIP_STORED) as packageZIP
    # 1) Pack the meta file.
    packageZIP.writestr(
        'meta.json', json.dumps({'name' PACKAGE_NAME, 'version' PACKAGE_VERSION, 'author' PACKAGE_AUTHOR})
    )

    # 2) Pack the provider modules.
    modulesPath = os.path.join(lambdaFolder, 'modules')
    for dirPath, dirNames, fileNames in os.walk(modulesPath)
        zipFolderPath = os.path.join(serenModulesFolder, PACKAGE_NAME, dirPath.replace(modulesPath, '').strip(os.sep))
        for fileName in fileNames
            moduleFile = open(os.path.join(dirPath, fileName), 'r', encoding='utf-8')
            script = moduleFile.read()
            moduleFile.close()
            # Replace references to 'lambdascrapers.modules' with the new path.
            script = re.sub(importPattern, importReplace, script)
            packageZIP.writestr(os.path.join(zipFolderPath, fileName), script)

    # 3) Pack the provider scripts.
    # - Only the language folders are stored right now. The _DebridOnly folder is ignored.
    # - Any references to 'resources.lib.modules' in the scripts are changed to use 'providerModules' from above.
    languageFoldersPath = os.path.join(lambdaFolder, 'sources_ lambdascrapers')
    for languageFolder in os.listdir(languageFoldersPath)
        if '.py' not in languageFolder and 'debrid' not in languageFolder.lower()
            languageFolderPath = os.path.join(languageFoldersPath, languageFolder)
            for entry in os.listdir(languageFolderPath)
                if entry.endswith('.py')
                    providerFile = open(os.path.join(languageFolderPath, entry), 'r', encoding='utf-8')
                    script = providerFile.read()
                    providerFile.close()
                    # Replace references to 'resources.lib.modules' with the new path.
                    script = re.sub(importPattern, importReplace, script)
                    packageZIP.writestr(os.path.join(scriptsFolder, languageFolder, entry), script)

# Write the final zip file outside of the 'with' context above, so the operations are complete.
outputPath = os.path.join(os.getcwd(), '%s_for_Seren_%s.zip' % (PACKAGE_NAME, CURRENT_TIME.strftime('%Y-%m-%d')))
with open(outputPath, 'wb') as output
    memoryBuffer.seek(0)
    output.write(memoryBuffer.getvalue())

# Done. There should be a new '(PACKAGE_NAME)_for_Seren_(date).zip' in the same folder as this script.