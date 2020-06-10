# Import libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import string 
import json
import os
import shutil
import rdflib
from rdflib import Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import TurtleParser

from ckan.plugins import toolkit

import ckan.lib.helpers as helpers

import cgi

# Get the variable of context from toolkit
c = toolkit.c

# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# Main function used to update LiveSchema
def updateLiveSchema(data_dict):    
    # Get the list of catalogs and datasets to use to check the current state of LiveSchema
    catalogs = toolkit.get_action('organization_list')(data_dict={})
    datasets = toolkit.get_action('package_list')(data_dict={})

    # Get the catalogs to update from the form
    catalogsSelection = data_dict["catalogsSelection"]

    # Scrape the Finto Repository
    if not catalogsSelection or "finto" in catalogsSelection:
        print("finto")
        scrapeFinto(catalogs, datasets)

    # Scrape the RVS Repository
    """
    if not catalogsSelection or "rvs" in catalogsSelection:
        print("rvs")
        scrapeRVS(catalogs, datasets)
    """

    # Scrape the DERI Repository
    if not catalogsSelection or "deri" in catalogsSelection:
        print("deri")
        scrapeDERI(catalogs, datasets)
    
    # Scrape Knowdive
    if not catalogsSelection or "knowdive" in catalogsSelection:
        print("knowdive")
        scrapeKnowDive(catalogs, datasets)
        
    # Scrape the the Others excel file from the GitHub Repository
    if not catalogsSelection or "github" in catalogsSelection:
        print("github")
        scrapeGitHub(catalogs, datasets)

    # Scrape the LOV Repository
    if not catalogsSelection or "lov" in catalogsSelection:
        print("lov")
        scrapeLOV(catalogs, datasets)

    # Scrape the Users Repository
    if not catalogsSelection or "users" in catalogsSelection:
        print("users")
        scrapeUsers(catalogs)


# Script to scrape the Finto repository
def scrapeFinto(catalogs, datasets):
    # Get the list of available licenses from CKAN
    licenses = toolkit.get_action('license_list')(data_dict={})
    # Check if FINTO is present on LiveSchema
    cataFinto = ""
    if "finto" in catalogs:
        # If it is then get its relative information and datasets
        cataFinto = toolkit.get_action('organization_show')(
            data_dict={"id": "finto", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for Finto
        cataFinto = toolkit.get_action('organization_create')(
            data_dict={"name": "finto",
                "id": "finto",
                "state": "active",
                "title": "FINnish Thesaurus and Ontology service",
                "image_url": "https://eepos.finna.fi/themes/custom/images/Finto-logo_eng.png?_=1511945761",
                "extras": [{"key": "URL", "value": "http://finto.fi/en/"}],
                "description": "Finto is a Finnish thesaurus and ontology service, which enables both the publication and browsing of vocabularies. The service also offers interfaces for integrating the thesauri and ontologies into other applications and systems."})
    # Set the URL you want to webscrape from
    url = "http://finto.fi/"
    # Connect to the URL
    response = requests.get(url+"en/")
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # Select the categories of all the vocabularies
    categories = soup.findAll("div", {"class": "vocab-category"})
    # Iterate over each category
    for category in categories:
        # Get the of the tag from the title of category
        tagName = category("h2")[0].text
        # Iterate over each vocabulary in that category
        for vocab in category("a"):
            # Get the page of the vocabulary
            responseVoc = requests.get(url+vocab["href"])
            # Parse the page of the vocabulary
            soupVoc = BeautifulSoup(responseVoc.text, "html.parser")

            # Create the package as a dict
            package = dict(extras=list())

            # Iterate over each link of the vocabulary and save the link (TURTLE format preferred)
            for a in soupVoc("div", {"class":"download-links"})[0]("a"):
                if(a and a.text == "RDF/XML"):
                    link = a["href"]
                if(a and a.text == "TURTLE"):
                    link = a["href"]
            package["url"] = url + link

            # Iterate over each row of the metadata table to obtain title, description, last modified, language, homepage, uri, publisher, creator, license if available
            agents = list()
            for tr in soupVoc("table", {"class":"table"})[0].find_all("tr"):
                th = tr.find_all("th")  
                if th and th[0].text == "TITLE":
                    title = tr.find_all("td")[0].text
                    package["title"] = title
                if th and th[0].text == "DESCRIPTION":
                    description = tr.find_all("td")[0].text
                    package["notes"] = description
                if th and th[0].text == "LAST MODIFIED":
                    lastModified = tr.find_all("td")[0].text
                    package["extras"].append({"key": "issued", "value": lastModified})
                if th and th[0].text == "LANGUAGE":
                    language = tr.find_all("td")[0].text
                    language = ", ".join(language[1:-1].split("\n"))
                    package["extras"].append({"key": "language", "value": language})
                if th and th[0].text == "HOMEPAGE":
                    homepage = tr.find_all("td")[0].text
                    package["extras"].append({"key": "contact_uri", "value": homepage})
                if th and th[0].text == "URI":
                    uri = tr.find_all("td")[0].text
                    package["extras"].append({"key": "uri", "value": uri})
                if th and th[0].text == "PUBLISHER":
                    publisher = tr.find_all("td")[0].text
                    publisher = publisher.split("\n")
                    publisher = [publi for publi in publisher if publi] 
                    package["maintainer"] = ", ".join(publisher)
                    for publi in publisher:
                        agents.append(addAgent(publi, ""))
                if th and th[0].text == "CREATOR":
                    creator = tr.find_all("td")[0].text
                    creator = creator.split("\n")
                    creator = [crea for crea in creator if crea] 
                    package["author"] = ", ".join(creator)
                    for crea in creator:
                        agents.append(addAgent(crea, ""))
                if th and th[0].text == "LICENSE":
                    lic = tr.find_all("td")[0].text
                    package["license_id"] = lic
                    for license_ in licenses:
                        if(len(license_["url"])>7 and len(lic)>7 and (lic[6:-5] in license_["url"][6:-5] or license_["url"][6:-5] in lic[6:-5])):
                            package["license_id"] = license_["id"]

            # Fill the package information
            package["name"] = "finto_" + vocab["href"].split("/")[0].lower().replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
            package["owner_org"] = cataFinto["id"]
            package["version"] = "1"
            package["tags"] = [{"name": tagName}]
            package["groups"] = agents
            package["extras"].append({"key": "Reference Catalog URL", "value": url+vocab["href"]})

            # Check if the dataset has to be updated
            checkPackage(datasets, package)


# Script to scrape the RVS repository
def scrapeRVS(catalogs, datasets):
    # Check if RVS is present on LiveSchema
    cataRVS = ""
    if "rvs" in catalogs:
        # If it is then get its relative information and datasets
        cataRVS = toolkit.get_action('organization_show')(
            data_dict={"id": "rvs", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for RVS
        cataRVS = toolkit.get_action('organization_create')(
            data_dict={"name": "rvs",
                "id": "rvs",
                "state": "active",
                "title": "Research Vocabularies Australia",
                "image_url": "https://ardc.edu.au/wp-content/themes/ardc/img/ardc_logo.svg",
                "extras": [{"key": "URL", "value": "https://vocabs.ands.org.au/"}],
                "description": "Research Vocabularies Australia is the controlled vocabulary discovery service of the Australian Research Data Commons (ARDC). ARDC is supported by the Australian Government through the National Collaborative Research Infrastructure Strategy Program."})
    #[TODO]


# Script to scrape the DERI repository
def scrapeDERI(catalogs, datasets):
    # Check if DERI is present on LiveSchema
    cataDERI = ""
    if "deri" in catalogs:
        # If it is then get its relative information and datasets
        cataDERI = toolkit.get_action('organization_show')(
            data_dict={"id": "deri", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for DERI
        cataDERI = toolkit.get_action('organization_create')(
            data_dict={"name": "deri",
                "id": "deri",
                "state": "active",
                "title": "DERI Vocabularies",
                "image_url": "http://vocab.deri.ie/sites/default/files/logo.png",
                "extras": [{"key": "URL", "value": "http://vocab.deri.ie/"}],
                "description": "DERI Vocabularies is a URI space for RDF Schema vocabularies and OWL ontologies maintained at DERI, the Digital Enterprise Research Institute at NUI Galway, Ireland. The site is operated by DERI's Linked Data Research Centre."})

    # Set the URL you want to webscrape from
    url = "http://vocab.deri.ie/"

    # Set the starting and ending page to scrape, that updates dynamically
    page = 0
    end = 1

    # Scrape every page from the vocabs tab of LOV
    while page < end:
        # Connect to the URL
        response = requests.get(url+"node?page=" + str(page))
        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")
        # Update the page index
        page += 1
        # If it is not the last page then update the end index
        if(len(soup("li", {"class": "pager-next"})) > 0):
            end += 1
        # Iterate over the vocabularies
        for vocab in soup.findAll("div", {"class": "vocabulary-node"}):
            # Get the vocabulary page
            responseVoc = requests.get(url + vocab("a")[0]["href"][1:])
            # Parse HTML and save to BeautifulSoup object
            soup = BeautifulSoup(responseVoc.text, "html.parser")

            # search for the div containing all the information needed
            voc = soup("div", {"class":"SearchContainer"})            

            # Create the package as a dict
            package = dict(extras=list())

            # Get and save the title from the page to the package, if available
            title = soup("h2")
            if title:
                title = title[0].text
                package["title"] = title

            # Get and save the description from the page to the package, if available
            description = soup("div", {"id":"abstract"})
            if description:
                description = description[0].text[9:]
                package["notes"] = description

            # Get and save the namespace from the page to the package, if available
            namespace = soup("div", {"id":"namespace-value"})
            if namespace:
                namespace = namespace[0].text
                package["extras"].append({"key": "contact_uri", "value": namespace})
                package["extras"].append({"key": "uri", "value": namespace})

            # Get and save the lastModified from the page to the package, if available
            lastModified = soup("div", {"id":"last-update-value"})
            if lastModified:
                lastModified = lastModified[0].text
                package["extras"].append({"key": "issued", "value": lastModified})
            
            # Add the Agents to LiveSchema
            agents = list()
            authorList = list()
            for author in soup("div", {"id":"author-value"}):
                if(author.a.text):
                    agents.append(addAgent(author.a.text, author.a["href"]))
                    authorList.append(author.a.text)
            package["author"] = ", ".join(authorList)
            package["groups"] = agents

            # Fill the package with the remaining information needed
            package["url"] = url + vocab("a")[0]["href"][1:] + ".ttl"
            package["name"] = "deri_" + vocab("a")[0]["href"][1:].split("/")[0].lower().replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
            package["owner_org"] = cataDERI["id"]
            package["version"] = "1"
            package["extras"].append({"key": "Reference Catalog URL", "value": url + vocab("a")[0]["href"][1:]})
            package["license_id"] = "CC-BY-4.0"

            # Check if the dataset has to be updated
            checkPackage(datasets, package)
            

# Script to scrape KnowDive
def scrapeKnowDive(catalogs, datasets):
    # Check if the KnowDive is present on LiveSchema
    cataKnowDive = ""
    if "knowdive" in catalogs:
        # If it is then get its relative information and datasets
        cataKnowDive = toolkit.get_action('organization_show')(
            data_dict={"id": "knowdive", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for the KnowDive
        cataKnowDive = toolkit.get_action('organization_create')(
            data_dict={"name": "knowdive",
                "id": "knowdive",
                "title": "KnowDive Vocabularies",
                "state": "active",
                "image_url": "http://knowdive.disi.unitn.it/wp-content/uploads/cropped-logo_small.png",
                "description": "Vocabularies developed by the Knowdive Research group", 
                "extras": [{"key": "URL", "value": "http://knowdive.disi.unitn.it/"}]})
                

# Script to scrape the Others excel file from GitHub Repository
def scrapeGitHub(catalogs, datasets):
    # Check if the Others excel file from github is present on LiveSchema
    cataGitHub = ""
    if "github" in catalogs:
        # If it is then get its relative information and datasets
        cataGitHub = toolkit.get_action('organization_show')(
            data_dict={"id": "github", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for the Other excel file from github
        cataGitHub = toolkit.get_action('organization_create')(
            data_dict={"name": "github",
                "id": "github",
                "title": "GitHub Repository",
                "state": "active",
                "extras": [{"key": "URL", "value": "https://github.com/knowdive/resources/blob/master/otherVocabs.xlsx"}]})
                    
    # Get the other vocabularies from the Excel file from github
    vocabs = pd.read_excel("https://raw.githubusercontent.com/knowdive/resources/master/otherVocabs.xlsx")
    # Iterate for every vocabulary read from the Excel file
    for index, row in vocabs.iterrows():
        # Create the package as a dict
        package = dict(extras=list())
        # Add the metadata of the dataset
        package["url"] = row["Link"]
        package["name"] = "github_" + row["prefix"].lower().replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
        package["title"] = row["prefix"]
        package["notes"] = row["Title"]
        package["owner_org"] = cataGitHub["id"]
        package["version"] = row["VersionName"]
        package["extras"].append({"key": "issued", "value": row["VersionDate"]})
        package["extras"].append({"key": "language", "value": row["Languages"]})
        package["extras"].append({"key": "contact_uri", "value": row["URI"]})
        package["license_id"] = "CC-BY-4.0"
        # Check if the dataset has to be updated
        checkPackage(datasets, package)


# Script to scrape the LOV repository
def scrapeLOV(catalogs, datasets):
    # Check if LOV is present on LiveSchema
    cataLOV = ""
    if "lov" in catalogs:
        # If it is then get its relative information and datasets
        cataLOV = toolkit.get_action('organization_show')(
            data_dict={"id": "lov", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for LOV
        cataLOV = toolkit.get_action('organization_create')(
            data_dict={"name": "lov",
                "id": "lov",
                "state": "active",
                "title": "Linked Open Vocabulary",
                "image_url": "https://lov.linkeddata.es/img/icon-LOV.png",
                "extras": [{"key": "URL", "value": "https://lov.linkeddata.es/dataset/lov"}],
                "description": "LOV started in 2011, in the framework of a French research project (http://datalift.org). Its main initial objective was to help publishers and users of linked data and vocabularies to assess what was available for their needs, to reuse it as far as possible, and to insert their own vocabulary production seamlessly in the ecosystem."})
        
    # Set the URL you want to webscrape from
    url = "https://lov.linkeddata.es"
    # Set the starting and ending page to scrape, that updates dynamically
    page = 1
    end = 2

    # Scrape every page from the vocabs tab of LOV
    while page < end:
        # Get the #page with the vocabs list
        link = url+"/dataset/lov/vocabs?&page="+str(page)
        end = vocabList(cataLOV, datasets, link, url, end)
        # Iterate the next page if there were vocabs in this page, otherwise end the program here
        page += 1

# Get all the vocabulary of that page
def vocabList(cataLOV, datasets, link, url, end):
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # To download the whole data set, let's do a for loop through all a tags
    voc = soup("div", {"class":"SearchContainer"})
    # if there is at least a vocabulary on that page's list
    if(len(voc)>0):
        # To check the next page
        end += 1
        # Iterate for every vocabularies of that page's list
        for i in range(0, len(voc)):
            # Pause the code for a sec
            #time.sleep(.500) 
            #oldLink = link
            link = voc[i].a["href"]
            vocabMeta(cataLOV, datasets, url+link)
    return end

# Get all the info from the vocabulary page
def vocabMeta(cataLOV, datasets, link):
    # Pause the code for half a sec
    time.sleep(.5)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the title and prefix of the vocabulary 
    title = soup("h1")[0]
    prefix = title.span.extract().text.strip()
    title = title.text.strip()
    prefix = prefix.replace("(", "").replace(")", "").decode('utf-8').lower()
    prefix = ''.join([i for i in prefix if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
    # Create the package as a dict
    package = dict(extras=list())
    # Add the basic metadata of the dataset
    package["name"] = "lov_" + prefix
    package["title"] = title
    package["owner_org"] = cataLOV["id"]
    package["license_id"] = "CC-BY-4.0"
    package["extras"].append({"key": "Reference Catalog URL", "value": link})

    #Get the Metadata and Languages of the vocabulary page
    uri = "URI"
    namespace = "Namespace"
    homepage = "homepage"
    description = "Description"
    languages = list()
    agents = list()
    pub = 1
    for child in soup("tbody")[0].find_all("tr"):
        if child.td.text.strip() == "URI":
            uri = child.find_all("td")[1].text.strip() 
            # Check for Duplicates between Deri & LOV
            if "vocab.deri.ie" in uri:
                return
            package["extras"].append({"key": "uri", "value": uri})
        if child.td.text.strip() == "Namespace":
            namespace = child.find_all("td")[1].text.strip() 
            package["url"] = namespace
        if child.td.text.strip() == "homepage":
            homepage = child.find_all("td")[1].text.strip() 
            package["extras"].append({"key": "contact_uri", "value": homepage})
            # Check for Duplicates between Deri & LOV
            if "vocab.deri.ie" in uri:
                return
        if child.td.text.strip() == "Description":
            description = child.find_all("td")[1].text.strip() 
            package["notes"] = description
        # Get the Languages
        if child.td.text.strip() == "Language":
            language = child.find_all("td")[1]
            # Append the Languages with a space as separator
            for childL in language.find_all("a"):
                uriL = childL.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                languages.append(uriL)
            package["extras"].append({"key": "language", "value": ', '.join(languages)})
        # Get the Creators
        if child.td.text.strip() == "Creator":
            creator = child.find_all("td")[1]
            # Add the Creators to the dataset
            creatorList = list()
            for childCr in creator.find_all("a"):
                nameCr = childCr.find("div", {"class": "agentThumbName"}).text.strip()
                creatorList.append(nameCr)
                uriCr = childCr.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                # Create Agent, get dict, add to list
                agents.append(addAgent(nameCr, uriCr))
            package["author"] = ", ".join(creatorList)

        # Get the Contributors
        if child.td.text.strip() == "Contributor":
            contributor = child.find_all("td")[1]
            # Add the Contributors to the dataset
            contributorList = list()
            for childCo in contributor.find_all("a"):
                nameCo = childCo.find("div", {"class": "agentThumbName"}).text.strip()
                contributorList.append(nameCo)
                uriCo = childCo.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                # Create Agent, get dict, add to list
                agents.append(addAgent(nameCo, uriCo))
            package["maintainer"] = ", ".join(contributorList)

        # Get the Publishers
        if child.td.text.strip() == "Publisher":
            publisher = child.find_all("td")[1]
            # Add the Publishers  to the dataset
            for childP in publisher.find_all("a"):
                nameP = childP.find("div", {"class": "agentThumbName"}).text.strip()
                uriP = childP.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                # Create Agent, get dict, add to list
                agents.append(addAgent(nameP, uriP))

    package["groups"] = agents

    # Add the Tags of the vocabulary page to the excel file
    tag = soup("ul", {"class": "tagsVocab"})
    tags = list()
    if(tag):
        for child in tag[0].find_all("li"):
            tagName = child.text.strip().decode('utf-8').lower()
            tagName = ''.join([i for i in tagName if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
            tags.append({"name": tagName})
        package["tags"] = tags

    # Get all the versions and save them with all their relative informations
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        # Store every version with a line on the Excel File
        versions = json.loads(versions.group(0))["events"]
        for version in range(0, len(versions)):
            if("version" in package.keys()):
                del package["version"]
            package["extras"] = [i for i in package["extras"] if not ((i["key"] == "issued") or (i["key"] == "modified"))] 

            versionName = ""
            if("title" in versions[version].keys() and "start" in versions[version].keys() and "link" in versions[version].keys() and "link" in versions[version].keys()):
                versionName = versions[version]["title"].replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
                package["version"] = versionName
                versionLink = versions[version]["link"]
                package["url"] = versionLink
            if("start" in versions[version].keys()):
                versionStart = versions[version]["start"]
                package["extras"].append({"key": "issued", "value": versionStart})
            if("end" in versions[version].keys()):
                versionEnd = versions[version]["end"]
                package["extras"].append({"key": "modified", "value": versionEnd})

        # Check if the dataset has to be updated
        checkPackage(datasets, package)

    # Delete the package at every iteration 
    del package


# Script to update the Users
def scrapeUsers(catalogs):
    # Check if RVS is present on LiveSchema
    cataUsers = ""
    if "users" in catalogs:
        # If it is then get its relative information and datasets
        cataUsers = toolkit.get_action('organization_show')(
            data_dict={"id": "users", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for RVS
        cataUsers = toolkit.get_action('organization_create')(
            data_dict={"name": "users",
                "id": "users",
                "state": "active",
                "title": "User defined Datasets",
                "description": "Datasets which have been uploaded to LiveSchema using the proper Service"})


# Procedure to check the package to update for LiveSchema
def checkPackage(datasets, package):
    print(package["name"])

    # Check License, if it's non usable then return without creating the package
    nonUsableLicenses = ["http://unitsofmeasure.org/trac/wiki/TermsOfUse"]
    if(package["license_id"] in nonUsableLicenses):
        return

    # Boolean used to verify if the online resources need to be updated
    outResources = True
    # Index to check also if all the resources are correctly available
    i = 3

    # Create an empty package to be able to remove the resources from the real package
    CKANpackage = ""

    # Check if the package is already on LiveSchema
    if package["name"] in datasets:
        # Make sure not to reset already updated datasets
        outResources = False
        i = 0

        # If the package is on LiveSchema then get the online version
        CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": package["name"]})

        # Boolean used to verify if the online version is outdated
        a = False

        # Iterate over every combination of fields
        for CKANfield in CKANpackage.keys():
            for field in package.keys():
                # If the online version has different values on the fields (except the extras and tags) then update them and set it as outdated
                if(CKANfield == field and CKANpackage[CKANfield] != package[field] and field != "extras" and field != "tags"):
                    CKANpackage[CKANfield] = package[field]
                    a = True
                    break

        # If there are different numbers of extra fields
        if(len(CKANpackage["extras"])!= len(package["extras"])):
            # Then the online version is outdated
            a = True

        # Iterate over every combination of extra fields
        for CKANextra in CKANpackage["extras"]:
            for extra in package["extras"]:
                # If the online version has different values on the extra fields then update them and set it as outdated
                if(CKANextra["key"] == extra["key"] and CKANextra["value"] != extra["value"]):
                    CKANextra["value"] = extra["value"]
                    a = True
                    break

        # If there are different numbers of tags fields
        if("tags" in package.keys() and len(CKANpackage["tags"])!= len(package["tags"])):
            # Update the tags
            CKANpackage["tags"] =  package["tags"]
            # Set the online version as outdated
            a = True

        # If the online version is outdated
        if(a):
            # Update the online version of the package
            toolkit.get_action('package_update')(
                data_dict=CKANpackage)
            # Also if the package has a different url link
            if(CKANpackage["url"] != package["url"]):
                # Update its resources
                outResources = True

        # Get the new online version
        CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": package["name"]})
        # Check if all the resources are correctly available
        for resource in CKANpackage["resources"]:
            if (resource["format"] == "TTL" and resource["resource_type"] == "Serialized ttl") or \
                (resource["format"] == "RDF" and resource["resource_type"] == "Serialized rdf") or \
                (resource["format"] == "CSV" and resource["resource_type"] == "Parsed csv"):
                # Update the index if a valid resource is available
                i += 1
    else:
        # Create the package on LiveSchema
        CKANpackage = toolkit.get_action('package_create')(
                data_dict=package)

    if(outResources or i < 3):
        # Delete all the eventual current resources of the dataset
        for resource in CKANpackage["resources"]:
            toolkit.get_action("resource_delete")(data_dict={"id": resource["id"]})

        # Reset ttl resource
        TTL_Resource = toolkit.get_action("resource_create")(
            data_dict={"package_id":package["name"], "format": "temp", "name": package["name"]+".ttl", "resource_type": "Serialized ttl", "description": "Serialized ttl format of the dataset"})
                    
        # Reset rdf resource
        RDFResource = toolkit.get_action("resource_create")(
            data_dict={"package_id":package["name"], "format": "temp", "name": package["name"]+".rdf", "resource_type": "Serialized rdf", "description": "Serialized rdf format of the dataset"})
                    
        # Reset csv resource
        CSVResource = toolkit.get_action("resource_create")(
            data_dict={"package_id":package["name"], "format": "temp", "name": package["name"]+".csv", "resource_type": "Parsed csv", "description": "Parsed csv containing all the triples of the dataset"})

        # Set the dictionary of IDs
        id = {'ttl_id': TTL_Resource['id'], 'rdf_id': RDFResource['id'], 'csv_id': CSVResource['id']}

        # Update the resources of that package
        addResources(id, package)

    # After all get the new online version
    CKANpackage = toolkit.get_action('package_show')(
        data_dict={"id": package["name"]})
    # Check if there are resources available in that dataset
    if (CKANpackage["num_resources"] == 0):
        # If there are none, then delete the dataset
        CKANpackage = toolkit.get_action('dataset_purge')(
            data_dict={"id": package["name"], "force":"True"})


# Procedure to add the resources of the given package
def addResources(id, package):
    # Try to create the graph to analyze the vocabulary
    try:
        g = Graph()
        if package["url"][-1] == "#":
            package["url"] = package["url"][:-1]
        format_ = package["url"].split(".")[-1]
        if(format_ == "txt"):
            format_ = package["url"].split(".")[-2]
        format_ = format_.split("?")[0]
        result = g.parse(package["url"], format=guess_format(format_), publicID=package["name"])
    except Exception as e:
        # In case of an error during the graph's initiation, print the error and return an empty list
        print(str(e) + "\n")    

        # Remove the eventual temp resources left
        removeTemp(package["name"])
        return 

    path = "src/ckanext-liveschema_theme/ckanext/liveschema_theme/public/resources/"

    try:
        # Serialize the vocabulary in ttl
        g.serialize(destination=str(os.path.join(path, package["name"] + ".ttl")), format=guess_format('ttl'))
        # Add the serialized ttl file to LiveSchema
        upload = cgi.FieldStorage()
        upload.filename = package["name"] + ".ttl"
        upload.file = file(path + package["name"] + ".ttl")
        data = {
            "id": id["ttl_id"], 
            "format": "TTL",
            'url': package["name"] + ".ttl", #'will-be-overwritten-automatically',
            'upload': upload
        }
        toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)
        # Remove the temporary ttl file from the server
        os.remove(path + package["name"] + ".ttl")
    except Exception as e:
        # In case of an error during the graph's serialization, print the error
        print(str(e) + "\n")

    try:
        # Serialize the vocabulary in rdf
        g.serialize(destination=str(os.path.join(path, package["name"] + ".rdf")), format="pretty-xml")
        # Add the serialized rdf file to LiveSchema     
        upload = cgi.FieldStorage()
        upload.filename = package["name"] + ".rdf"
        upload.file = file(path + package["name"] + ".rdf")
        data = {
            "id": id["rdf_id"], 
            "format": "RDF",
            'url': package["name"] + ".rdf", #'will-be-overwritten-automatically',
            'upload': upload
        }
        toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)
        # Remove the temporary rdf file from the server
        os.remove(path + package["name"] + ".rdf")
    except Exception as e:
        # In case of an error during the graph's serialization, print the error
        print(str(e) + "\n")

    # Create the list for inserting every triple of the vocabulary
    list_ = list()
    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:
        # Compute the filtered statement of the Triples
        subjectTerm = subject.replace("/", "#").split("#")[-1]
        if(not len(subjectTerm) and len(subject.replace("/", "#").split("#")) > 1):
            subjectTerm = subject.replace("/", "#").split("#")[-2]
        predicateTerm = predicate.replace("/", "#").split("#")[-1]
        if(not len(predicateTerm) and len(predicate.replace("/", "#").split("#")) > 1):
            predicateTerm = predicate.replace("/", "#").split("#")[-2]
        objectTerm = object_.replace("/", "#").split("#")[-1]
        if(not len(objectTerm) and len(object_.replace("/", "#").split("#")) > 1):
            objectTerm = object_.replace("/", "#").split("#")[-2]
        if(package["name"] == "freebase"):
            subjectTerm = subjectTerm.split(".")[-1]
            if(not len(subjectTerm) and len(subjectTerm.split(".")) > 1):
                subjectTerm = subjectTerm.split(".")[-2]
            predicateTerm = predicateTerm.split(".")[-1]
            if(not len(objectTerm) and len(predicateTerm.split(".")) > 1):
                predicateTerm = predicateTerm.split(".")[-2]
            objectTerm = objectTerm.split(".")[-1]
            if(not len(objectTerm) and len(objectTerm.split(".")) > 1):
                objectTerm = objectTerm.split(".")[-2]

        # Save the statement to the List to be added to the DataFrame
        list_.insert(index,{"Subject": subject, "Predicate": predicate, "Object": object_, "SubjectTerm": subjectTerm, "PredicateTerm": predicateTerm, "ObjectTerm": objectTerm, "Domain": package["name"], "Domain Version": package["version"]})
        index += 1
    
    # Create the DataFrame to save the vocabs' information
    DTF = pd.DataFrame(list_, columns=["Subject", "Predicate", "Object", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version"])
    # Parse the DataFrame into the csv file
    DTF.to_csv(os.path.normpath(os.path.expanduser(path + package["name"] + ".csv")))

    # Upload the csv file to LiveSchema
    upload = cgi.FieldStorage()
    upload.filename = package["name"] + ".csv"
    upload.file = file(path + package["name"] + ".csv")
    data = {
        "id": id["csv_id"],
        "format": "CSV",
        'url': package["name"] + ".csv", #'will-be-overwritten-automatically',
        'upload': upload
    }
    toolkit.get_action('resource_patch')(context = {'ignore_auth': True}, data_dict=data)
    
    # Add file to DataStore using DataPusher
    import ckanext.datapusher.logic.action as dpaction
    dpaction.datapusher_submit(context = {'ignore_auth': True}, data_dict={'resource_id': str(id["csv_id"])})

    # Remove the temporary csv file from the server
    os.remove(path + package["name"] + ".csv")

    # Remove the eventual temp resources left
    removeTemp(package["name"])

# Remove the eventual temp resources left
def removeTemp(name):
    # Get the final version of the package
    CKANpackage = toolkit.get_action('package_show')(
            data_dict={"id": name})
    # Iterate over all the resources
    for resource in CKANpackage["resources"]:
        # Remove eventual temp resources left
        if resource["format"] == "temp" and (resource["resource_type"] == "Serialized ttl" or resource["resource_type"] == "Serialized rdf" or resource["resource_type"] == "Parsed csv"):
            toolkit.get_action("resource_delete")(context = {"ignore_auth": True}, data_dict={"id":resource["id"]})

# Add an Agent to LiveSchema
def addAgent(agentTitle, agentLink):
    # Format the agentName to CKAN specifics
    agentName = agentTitle.lower().replace(" ","-").replace(".","-").replace(";","-")
    agentName = "".join([i for i in agentName if (i in string.ascii_lowercase or i.isdigit() or i == "-")])
    # Get the list of the Agents alredy on LiveSchema 
    agents = toolkit.get_action('group_list')(data_dict={})
    # Check if the Agent has already been created
    if agentName in agents:
        # If it is then get its relative information and datasets
        agent = toolkit.get_action('group_show')(
            data_dict={"id": agentName, "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the agent
        agent = toolkit.get_action('group_create')(
            data_dict={"name": agentName,
                "id": agentName,
                "state": "active",
                "title": agentTitle,
                "extras": [{"key": "URI", "value": agentLink}]})
    # Return the id of the created agent
    return {"id": agentName}


# Add the dataset obtained by the Service
def uploadDataset(id, package, filePath, data):
    
    # Add the resources of the package
    addResources(id, package)

    # After all get the new online version
    CKANpackage = toolkit.get_action('package_show')(
        data_dict={"id": package["name"]})

    # Check if there are resources available in that dataset
    if (CKANpackage["num_resources"] == 0):
        # If there are none, then delete the dataset and return
        CKANpackage = toolkit.get_action('dataset_purge')(
            data_dict={"id": package["name"], "force":"True"})
        return

    # Remove the temporary file from the server and update the url in case of uploaded file
    if(filePath):
        os.remove(filePath)
        # Check if the TTL resource is correctly available 
        for resource in CKANpackage["resources"]:
            if (resource["format"] == "TTL" and resource["resource_type"] == "Serialized ttl"):
                # Update the url of the package with the one of the TTL resource
                CKANpackage["url"] = resource["url"]
                break
        # Update the online version of the package with the new url
        CKANpackage = toolkit.get_action('package_update')(
            data_dict=CKANpackage)

    # Add Agents
    agents = list()
    if("author" in data.keys()): 
        agents.append(addAgent(data["author"], data["author_uri"]))
        CKANpackage["maintainer"] = data["author"]
    if("maintainer" in data.keys()): 
        agents.append(addAgent(data["maintainer"], data["maintainer_uri"]))
        CKANpackage["maintainer"] = data["maintainer"]
    CKANpackage["groups"] = agents

    # Update the online version of the package with the new agents
    if(agents):
        CKANpackage = toolkit.get_action('package_update')(
            data_dict=CKANpackage)
    

