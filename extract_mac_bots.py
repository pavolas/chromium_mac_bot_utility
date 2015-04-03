import argparse
import json
import sys


master_keywords_to_ignore = [
  "bling",
  "mobile",
  "master.client",
  "master.internal.client",
]

# These masters will likely have to be updated in the future.
masters_to_ignore = [
  "master.chromium.gpu.fyi",
  "master.chromium.webrtc",
  "master.tryserver.libyuv",
  "master.chromium.webrtc.fyi",
  "master.tryserver.webrtc",
  "master.tryserver.nacl",
  "master.chromium.memory.fyi",
  "master.tryserver.chromium.perf",
  "master.internal.tryserver.webrtc",
  "master.chrome.perf_internal.try",
  "master.chromium.chromedriver",
  "master.tryserver.v8",
  "master.chromium.webkit",
  "master.client.goma",
  "master.chromium.swarm",
]

# These masters are intentionally kept on old revisions.
masters_to_intentionally_ignore = [
  "master.chrome.reserved",
  "master.chromium.reserved",
  "master.tryserver.reserved",
]

builder_keywords_to_ignore = [
  "ios",
]

def ExtractDictionaryFromJSONFile(file_path):
  f = open(file_path)
  contents = f.read()
  dict = json.loads(contents)
  f.close()
  return dict

def IsBotOSMac(bot):
  if "os" not in bot:
    return False
  os = bot["os"]
  return os == "mac"

def IsMasterBlacklisted(mastername):
  for keyword in master_keywords_to_ignore:
    if keyword in mastername:
      return True
  if mastername in masters_to_ignore:
    return True
  if mastername in masters_to_intentionally_ignore:
    return True
  return False

def IsBuilderBlacklisted(buildername):
  for keyword in builder_keywords_to_ignore:
    if keyword in buildername.lower():
      return True
  return False

def ExtractRelevantBots():
  """
  Finds mac bots whose masters are not blacklisted. Returns a dictionary of
  mastername : list of bots.
  """
  bots = ExtractDictionaryFromJSONFile('botmap.json')


  # Maps mastername : array of bots.
  bot_dictionary = {}
  for bot in bots:
    if not IsBotOSMac(bot):
      continue
    mastername = bot["mastername"]
    if IsMasterBlacklisted(mastername):
      continue

    if mastername not in bot_dictionary:
      bot_dictionary[mastername] = []

    bot_dictionary[mastername].append(bot)
  return bot_dictionary

def ExtractMasterToBuilders():
  """
  Returns a dictionary of mastername : { dictionary of builder name : list of hostnames }

  Note: builder names are not unique - they are namespaced within a given
  master.
  """
  builder_dicts = ExtractDictionaryFromJSONFile('buildermap.json')
  master_map = {}
  for builder_dict in builder_dicts:
    mastername = builder_dict["mastername"]
    if mastername not in master_map:
      master_map[mastername] = {}
    builder_name = builder_dict["builder"]
    hostnames = builder_dict["hostname"]
    master_map[mastername][builder_name] = hostnames
  return master_map

def ListMasters():
  bot_dictionary = ExtractRelevantBots()
  for mastername in bot_dictionary:
    print mastername

def BuildersForMaster(mastername):
  """
  Returns a sorted list of builders for each master.
  """
  bot_dictionary = ExtractRelevantBots()
  builders_to_update = set()
  for bot in bot_dictionary[mastername]:
    builders = bot['builder']
    for builder in builders:
      if IsBuilderBlacklisted(builder):
        continue
      builders_to_update.add(builder)
  builders_to_update = sorted(builders_to_update)
  return builders_to_update

def ListBuilders(mastername):
  for builder in BuildersForMaster(mastername):
    print builder

def ListVms(mastername):
  relevant_builders = BuildersForMaster(mastername)
  master_map = ExtractMasterToBuilders()
  builder_map = master_map[mastername]
  for builder in relevant_builders:
    print builder
    print builder_map[builder]
    print '---------------'
  #hostnames = set()
  #for builder in builders:
  #  for hostname in builder_map[builder]:
  #    hostnames.add(hostname)
  #hostnames = sorted(hostnames)
  #for hostname in hostnames:
  #  print hostname


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utility for working with infra mac bots.')
  parser.add_argument('--list_masters', help='lists relevant masters', action='store_true')
  parser.add_argument('--list_builders', help='lists builders for master')
  parser.add_argument('--list_vms', help='lists vms for builders for master')
  args = parser.parse_args()

  if args.list_masters:
    ListMasters()
    sys.exit(0)
  if args.list_builders:
    ListBuilders(args.list_builders)
    sys.exit(0)
  if args.list_vms:
    ListVms(args.list_vms)
    sys.exit(0)

  print args
