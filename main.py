from yodas import Menu, Yoda
import json
import deepl as dl
import os


def getConfig():
    # source JSON Path is where the source JSON files are found needs to have the /
    # generated JSON path is where the new JSON files are stored needs to have the /
    # deepL key is the deepL key
    return Yoda("config.json", keys=["sourceJSONPath", "generatedJSONPath", "deepLKey"])


def getJSONs(path):
    return [file for file in os.listdir(path) if file.endswith(".json")]


def selectJSON(config):
    path = config["sourceJSONPath"]
    jsons = getJSONs(path)
    jsons.insert(0, exit)
    filePath = path + Menu(jsons, title="Select a source JSON file").select()
    with open(filePath, "r") as json_string:
        return json.load(json_string)


def selectDeepLanguage(translator, target=False):
    if target:
        title = "Select a target language"
        command = translator.get_target_languages
    else:
        title = "Select a source language"
        command = translator.get_source_languages
    menu = Menu([], execute=False, title=title)
    for lang in command():
        menu.append({lang.name: lang})
    return menu.select()


def getUsage(translator):
    usage = translator.get_usage()
    if usage.character.limit_exceeded:
        print("Character limit exceeded.")
    else:
        count = usage.character.count
        limit = usage.character.limit
        percent = round(100 * (count / limit), 1)
        print("Character usage: {0} of {1}\t{2}% Used".format(count, limit, percent))


def translateFile(config, translator):
    source = selectDeepLanguage(translator).code
    target = selectDeepLanguage(translator, target=True).code
    jsonDict = selectJSON(config)
    newJSONdict = {}

    keys = list(jsonDict.keys())
    keysLength = len(keys)
    for key in jsonDict:
        print("{0}/{1}".format(keys.index(key) + 1, keysLength))
        result = translator.translate_text(jsonDict[key], source_lang=source, target_lang=target)
        newJSONdict[key] = result.text

    file = open("{0}{1}.json".format(config["generatedJSONPath"], target.lower()), "w")
    json.dump(newJSONdict, file, indent=4, ensure_ascii=False)
    print("Done!\n")


def main():
    config = getConfig().contents()
    try:
        os.mkdir(config["generatedJSONPath"])
    except FileExistsError:
        pass
    translator = dl.Translator(config["deepLKey"])
    menu = Menu([exit, getUsage, translateFile], execute=False, title="Main Menu")
    while True:
        item = menu.select()
        if item == getUsage:
            getUsage(translator)
        elif item == translateFile:
            translateFile(config, translator)
        else:
            item()


if __name__ == '__main__':
    main()
