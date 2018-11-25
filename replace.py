import os

scraper_list = os.listdir(os.curdir)

input_path = os.curdir
output_path = os.path.join(os.curdir, 'replaced')

for i in scraper_list:
    if not i.endswith('.py'):
        continue
    if i == 'replace.py':
        continue
    with open(os.path.join(input_path, i)) as input:
        contents = input.read()
        contents = contents.replace('resources.lib.modules', 'providerModules.LambdaScrapers')
        contents = contents.replace('if debrid.status() is False: raise Exception()', '')
        contents = contents.replace('\n\n\n', '\n')
        with open(os.path.join(output_path, i), 'w') as output:
            output.write(contents)
            output.close()
        input.close()







