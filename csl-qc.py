# Python script for additional style validation
# Author: Rintze M. Zelle
# Version: 2011-07-28
# * Requires lxml library (http://lxml.de/)
# Checks
# - whether ".csl" files conform to naming scheme [a-z0-9] with optional single
#   hyphen delimiters
# - whether style ID (content of cs:id) matches the URI generated by the Zotero
#   Style Repository:
#   "http://www.zotero.org/styles/" + filename - extension
# - whether "self" link (value of "href" on cs:link with rel="self") matches the
#   Zotero Style Repository
# - for independent styles, whether "template" link (value of "href" on cs:link
#   with rel="template") points to the Zotero Style Repository style URI of an
#   independent style.
# - for dependent styles, whether "independent-parent" link (value of "href" on
#   cs:link with rel="template") points to the Zotero Style Repository style URI
#   of an independent style.
# - whether style filenames are unique (dependent styles are stored in their own
#   subdirectory)
# - for independent styles, whether the value of "citation-format" on
#   cs:category matches that of the independent parent style 
#
# Shows
# - number of dependent styles per independent style (if printDependentsCount is
#   set to True)

import os, glob, re
from lxml import etree

path = 'C:\Users\Rintze Zelle\Documents\git\styles\\'
printDependentsCount = True

def parseStyle(stylePath):
    style = etree.parse(stylePath)
    styleElement = style.getroot()
    metadata = {}
    try:
        metadata["id"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}id").text
        metadata["selfLink"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='self']").attrib.get("href")
    except:
        pass
    try:
        metadata["template"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='template']").attrib.get("href")
    except:
        pass
    try:
        metadata["independentParent"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}link[@rel='independent-parent']").attrib.get("href")
    except:
        pass
    try:
        metadata["citationFormat"] = styleElement.find(".//{http://purl.org/net/xbiblio/csl}category[@citation-format]").attrib.get("citation-format")
    except:
        pass
    return(metadata)

metadataList = []
metadata = {}
bad_fileName = {"errorMessage":"Non-conforming Filename (only lowercase roman letters [a-z], digits [0-9] and separating hyphens are allowed):"}
bad_fileName["styles"] = []
citationFormat_mismatch = {"errorMessage":"Citation format does not match that of independent parent (value 'citation-format' on cs:category[@rel=citation-format]):"}
citationFormat_mismatch["styles"] = []
duplicated_fileName = {"errorMessage":"Duplicate Filename (filename used by both an independent and dependent style):"}
duplicated_fileName["styles"] = []
fileName_id_mismatch = {"errorMessage":"Filename/ID Mismatch (filename does not match content cs:id):"}
fileName_id_mismatch["styles"] = []
fileName_selfLink_mismatch = {"errorMessage":"Filename/URI Mismatch (filename does not match value 'href' on cs:link[@rel=self]):"}
fileName_selfLink_mismatch["styles"] = []
missing_id = {"errorMessage":"Missing ID (content cs:id):"}
missing_id["styles"] = []
missing_selfLink = {"errorMessage":"Missing URI (value 'href' on cs:link[@rel=self]):"}
missing_selfLink["styles"] = []
missing_independentParent = {"errorMessage":"No Parent Specified (value 'href' on cs:link[@rel=independent-parent]):"}
missing_independentParent["styles"] = []
missing_template = {"errorMessage":"Template does not exist (no URI match for value 'href' on cs:link[@rel=template]):"}
missing_template["styles"] = []
orphan = {"errorMessage":"Parent does not exist (no URI match for value 'href' on cs:link[@rel=independent-parent]):"}
orphan["styles"] = []

styleErrors = [bad_fileName, duplicated_fileName, fileName_id_mismatch, fileName_selfLink_mismatch, missing_id, missing_selfLink, missing_independentParent, missing_template, orphan, citationFormat_mismatch]
for independentStyle in glob.glob( os.path.join(path, '*.csl') ):
    fileName = os.path.basename(independentStyle)

    if not(re.match("[a-z0-9](-?[a-z0-9]+)*(.csl)", fileName)):
        bad_fileName["styles"].append(fileName)
    
    metadata = parseStyle(independentStyle)
    metadata["fileName"] = fileName

    if(metadata.has_key("selfLink")):
        if not(("http://www.zotero.org/styles/"+fileName) == (metadata["selfLink"]+".csl")):
            fileName_selfLink_mismatch["styles"].append(fileName)
    else:
        missing_selfLink["styles"].append(fileName)
    if(metadata.has_key("id")):
        if not(("http://www.zotero.org/styles/"+fileName) == (metadata["id"]+".csl")):
            fileName_id_mismatch["styles"].append(fileName)
    else:
        missing_id["styles"].append(fileName)
    
    metadataList.append(metadata)

for queryMetadataDict in metadataList:
    match = True

    if(queryMetadataDict.has_key("template")):
        match = False
        for metadataDict in metadataList:
            if(metadataDict.has_key("selfLink") and (queryMetadataDict["template"] == metadataDict["selfLink"])):
                match = True
        if(match == False):
            missing_template["styles"].append(queryMetadataDict["fileName"])

metadataListDependents = []
metadataDependents = {}
for dependentStyle in glob.glob( os.path.join(path, "dependent", '*.csl') ):
    fileName = os.path.basename(dependentStyle)
    
    if not(re.match("[a-z0-9](-?[a-z0-9]+)*(.csl)", fileName)):
        bad_fileName["styles"].append("dependent" + os.sep + fileName)

    metadataDependents = parseStyle(dependentStyle)
    metadataDependents["fileName"] = fileName
    
    if(metadataDependents.has_key("selfLink")):
        if not(("http://www.zotero.org/styles/"+fileName) == (metadataDependents["selfLink"]+".csl")):
            fileName_selfLink_mismatch["styles"].append("dependent" + os.sep + fileName)
    if(metadataDependents.has_key("id")):
        if not(("http://www.zotero.org/styles/"+fileName) == (metadataDependents["id"]+".csl")):
            fileName_id_mismatch["styles"].append("dependent" + os.sep + fileName)
    else:
        missing_id["styles"].append("dependent" + os.sep + fileName)
    if not(metadataDependents.has_key("independentParent")):
        missing_independentParent["styles"].append("dependent" + os.sep + fileName)

    metadataListDependents.append(metadataDependents)

dependentsCount = {}
for queryMetadataDict in metadataListDependents:
    match = True
    
    if(queryMetadataDict.has_key("independentParent")):
        match = False
        for metadataDict in metadataList:
            if(metadataDict.has_key("selfLink") and (queryMetadataDict["independentParent"] == metadataDict["selfLink"])):
                match = True
                if metadataDict["fileName"] in dependentsCount:
                    dependentsCount[metadataDict["fileName"]] += 1
                else:
                    dependentsCount[metadataDict["fileName"]] = 1
                if(metadataDict.has_key("citationFormat") and queryMetadataDict.has_key("citationFormat") and not(queryMetadataDict["citationFormat"] == metadataDict["citationFormat"])):
                    citationFormat_mismatch["styles"].append("dependent" + os.sep + queryMetadataDict["fileName"])
            if(queryMetadataDict["fileName"] == metadataDict["fileName"]):
                duplicated_fileName["styles"].append(metadataDict["fileName"])
        if(match == False):
            orphan["styles"].append("dependent" + os.sep + queryMetadataDict["fileName"])

for styleError in styleErrors:
    if (len(styleError["styles"]) > 0):
        print(styleError["errorMessage"])
        for style in styleError["styles"]:
            print(style)
        print("----------")

if printDependentsCount:
    dependentsPopularitySort = sorted(dependentsCount, key=dependentsCount.get, reverse=True)
    print("Number of dependent styles per independent style:")
    for style in dependentsPopularitySort:
        print(style + ": %d" % (dependentsCount[style]))
