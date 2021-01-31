import zipfile, requests, json, os, sqlite3, pickle, hoshino, datetime, traceback
from hoshino import aiorequests

try:
    config = hoshino.config.destiny2.destiny2_config
except:
    hoshino.logger.error('Destiny2无配置文件!请仔细阅读README')

DEFAULT_LANGUAGE = config.DEFAULT_LANGUAGE
LOAD_LANGUAGES = config.LOAD_LANGUAGES
HEADERS = config.HEADERS
PROXIES = config.PROXIES
MANIFEST_FILE_DIR = config.MANIFEST_FILE_DIR
USELESS_STATS = config.USELESS_STATS
hashes = config.MANIFEST_HASHES

def get_manifest(language=DEFAULT_LANGUAGE):
    url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    resp = requests.get(url, timeout=5, headers=HEADERS, proxies=PROXIES).json()
    manifest_url = 'https://www.bungie.net' + resp['Response']['mobileWorldContentPaths'][language]
    r = requests.get(manifest_url, timeout=5, headers=HEADERS, proxies=PROXIES)
    with open(MANIFEST_FILE_DIR + language + "/manifest", "wb") as zip:
        zip.write(r.content)
    hoshino.logger.info("Download Complete!")

    with zipfile.ZipFile(MANIFEST_FILE_DIR + language + "/manifest") as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0],MANIFEST_FILE_DIR + language + "/manifest.content")
    hoshino.logger.info('Unzipped!')

def build_dict(hash_dict, language=DEFAULT_LANGUAGE):
    # connect to the manifest
    con = sqlite3.connect(MANIFEST_FILE_DIR + language + '/manifest.content')
    hoshino.logger.info('Connected')
    # create a cursor object
    cur = con.cursor()

    all_data = {}
    # for every table name in the dictionary
    for table_name in hash_dict.keys():
        # get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        hoshino.logger.info('Generating '+table_name+' dictionary....')

        # this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        # create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        # create a dictionary with the hashes as keys
        # and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        for item in item_jsons:
            item_dict[item[hash]] = item

        # add that dictionary to our all_data using the name of the table
        # as a key.
        all_data[table_name] = item_dict
    hoshino.logger.info('Dictionary Generated!')
    return all_data

def init_manifest(language=DEFAULT_LANGUAGE):
    # check if pickle exists, if not create one.
    manifest_unzip_file = get_manifest_unzip_path(language)
    if not os.path.isfile(manifest_unzip_file):
        for i in os.listdir(manifest_unzip_file):
            try:
                path_file = os.path.join(manifest_unzip_file, i)
                os.remove(path_file)
            except:
                continue
        get_manifest(language)
        manifest = build_dict(hashes, language)
        with open(MANIFEST_FILE_DIR + language + '/manifest.pickle', 'wb') as data:
            pickle.dump(manifest, data)
            hoshino.logger.info("'manifest.pickle' created!\nDONE!")
    else:
        hoshino.logger.info('Pickle Exists')
    with open(MANIFEST_FILE_DIR + language + '/manifest.pickle', 'rb') as data:
        manifest = pickle.load(data)
    return manifest

async def update_manifest(language=LOAD_LANGUAGES):
    url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    resp = await aiorequests.get(url, headers = HEADERS, proxies=PROXIES, timeout=5)
    json_data = await resp.json()
    if type(language) == list:
        for lang in language:
            try:
                manifest_url = 'https://www.bungie.net' + json_data['Response']['mobileWorldContentPaths'][lang]
                r = await aiorequests.get(manifest_url, timeout=5, headers=HEADERS, proxies=PROXIES)
                content = await r.content
                path = MANIFEST_FILE_DIR + lang
                for i in os.listdir(path):
                    try:
                        path_file = os.path.join(path, i)
                        os.remove(path_file)
                    except:
                        continue
                manifest_zip_file = get_manifest_zip_path(lang)
                manifest_unzip_file = get_manifest_unzip_path(lang)
                manifest_pickle_file = get_manifest_pickle_path(lang)
                with open(manifest_zip_file , "wb") as zip:
                    zip.write(content)
                hoshino.logger.info(f"{lang} Manifest Download Complete!")
                with zipfile.ZipFile(manifest_zip_file) as zip:
                    name = zip.namelist()
                    zip.extractall()
                os.rename(name[0],manifest_unzip_file)
                hoshino.logger.info(f'{lang} Manifest Unzipped!')
                manifest = build_dict(hashes, language=lang)
                with open(manifest_pickle_file, 'wb') as data:
                    pickle.dump(manifest, data)
                    hoshino.logger.info(f"{lang} 'manifest.pickle' created!")
            except Exception as e:
                print(e)
                hoshino.logger.error(f'{lang} Manifest Update Error')
                continue
    elif type(language) == str:
        try:
            manifest_url = 'https://www.bungie.net' + json_data['Response']['mobileWorldContentPaths'][language]
            r = await aiorequests.get(manifest_url, timeout=5, headers=HEADERS, proxies=PROXIES)
            content = await r.content
            path = MANIFEST_FILE_DIR + language
            for i in os.listdir(path):
                try:
                    path_file = os.path.join(path, i)
                    os.remove(path_file)
                except:
                    continue
            manifest_zip_file = get_manifest_zip_path(language)
            manifest_unzip_file = get_manifest_unzip_path(language)
            manifest_pickle_file = get_manifest_pickle_path(language)
            with open(manifest_zip_file , "wb") as zip:
                zip.write(content)
            hoshino.logger.info(f"{language} Manifest Download Complete!")
            with zipfile.ZipFile(manifest_zip_file) as zip:
                name = zip.namelist()
                zip.extractall()
            os.rename(name[0],manifest_unzip_file)
            hoshino.logger.info(f'{language} Manifest Unzipped!')
            manifest = build_dict(hashes, language=lang)
            with open(manifest_pickle_file, 'wb') as data:
                pickle.dump(manifest, data)
                hoshino.logger.info(f"{language} 'manifest.pickle' created!")
        except:
            hoshino.logger.error(f'{language} Manifest Update Error')

def get_manifest_zip_path(language=DEFAULT_LANGUAGE):
    path = os.path.join(MANIFEST_FILE_DIR , language , 'manifest')
    return path

def get_manifest_unzip_path(language=DEFAULT_LANGUAGE):
    path = os.path.join(MANIFEST_FILE_DIR , language , 'manifest.content')
    return path

def get_manifest_pickle_path(language=DEFAULT_LANGUAGE):
    path = os.path.join(MANIFEST_FILE_DIR , language , 'manifest.pickle')
    return path