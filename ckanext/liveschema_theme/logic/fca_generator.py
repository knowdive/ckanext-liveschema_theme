# Import libraries
import pandas as pd
import os
import requests

import ckan.plugins.toolkit as toolkit

import ckan.lib.helpers as helpers

# List of stopWords
stopWords = ['able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after', 'afterwards', 'again', 'against', 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'amongst', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', 'around', 'aside', 'ask', 'asking', 'associated', 'available', 'away', 'awfully', 'became', 'because', 'become', 'becomes','becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'came', 'can', 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', 'course', 'currently', 'definitely', 'described', 'despite', 'did', 'different', 'does', 'doing', 'done','down', 'downwards', 'during', 'each', 'edu', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'exactly', 'example', 'except', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets', 'getting', 'given', 'gives', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', 'happens', 'hardly', 'has', 'have', 'having', 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'ignored', 'immediate', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 'instead', 'into', 'inward', 'its', 'itself', 'just', 'keep', 'keeps', 'kept', 'know','known', 'knows', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'mainly', 'many', 'may', 'maybe', 'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'myself','name', 'namely', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'obviously', 'off', 'often', 'okay', 'old', 'once', 'one', 'ones', 'only', 'onto', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall','own', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'que', 'quite', 'rather', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she', 'should', 'since', 'six', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 'take', 'taken', 'tell', 'tends', 'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein','theres', 'thereupon', 'these', 'they', 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'upon', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'value', 'various', 'very', 'via', 'viz', 'want', 'wants', 'was', 'way', 'welcome', 'well', 'went', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'wonder', 'would', 'yes', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'zero']

# Function that generate the FCA Matrix
def generateFCA(data_dict):
    # Create the dataframe from the CSV file
    triples = pd.read_csv(data_dict["dataset_link"])

    # Sort the DataFrame
    triples = triples.sort_values("Object")

    # Create the DataFrame used to create the FCA matrix  
    matrix = pd.DataFrame(columns=["Type", "TypeTerm", "Properties", "PropertiesTerms", "PropertiesTokens"])

    # Create the strings used to store multiple values in the same row, using " - " as separator
    obj = ""
    prop = ""
    propTerms = ""
    propTokens = ""
    # Dictionary used to store the triple
    dict_ = dict()

    # Iterate over every triples row
    for index, row in triples.iterrows():
        # Check if the triple has to be saved, if there is a predicate selection then checks if that predicate has to be saved
        bool_ = False
        # If there is no predicate selection then save every triple
        strPredicates = data_dict["strPredicates"]
        if(len(strPredicates.split()) == 0):
            bool_ = True
        # If there is a predicate selection then check if that predicate has to be saved
        else:
            for pred in strPredicates.split():
                if(pred == str(row["PredicateTerm"]) or pred == str(row["Predicate"])):
                    bool_ = True
                    break
        # Check if the triple has to be saved
        if(bool_ == True):
            # If the object value on the row has changed(first row or a new object)
            if(row["Object"] != obj):
                # If the name of the object is not null
                if(len(obj)):
                    # Add to the dictionary the latest values of the row
                    dict_["Properties"] = prop[2:] 
                    dict_["PropertiesTerms"] = propTerms[3:] 
                    dict_["PropertiesTokens"] = propTokens[3:] 
                    # Store the row in the matrix
                    matrix = matrix.append(dict_, ignore_index=True)
                # Reset the name of the new object
                obj = row["Object"]
                # Reset the other values of the row
                prop = ""
                propTerms = ""
                propTokens = ""
                # Store in the dictionary the fixed values of the row
                dict_ = {"Type": " " + row["Object"], "TypeTerm": row["ObjectTerm"]}
            
            # Add the info on the row to the strings containing multiple values
            prop = prop + " - " + row["Subject"]
            propTerms = propTerms + " - " + row["SubjectTerm"]
            
            # Tokenize on capitalLetters the SubjectTerm obtaining the simple words of its composition as strings separated by " "
            pTok = tokenTerm(row["SubjectTerm"])
            # Add the info of the tokens to the string containing multiple values
            propTokens = propTokens + " - " + pTok

    # Update the last row with the latest info
    dict_["Properties"] = prop[2:] 
    dict_["PropertiesTerms"] = propTerms[3:] 
    dict_["PropertiesTokens"] = propTokens[3:] 
    # Store the last row in the matrix
    matrix = matrix.append(dict_, ignore_index=True)

    # Set used to avoid the creation of the same column more than once
    tokSet = set()
    # Iterate over every row of the matrix
    for index, row in matrix.iterrows():
        # Create a list of tokens from that row's PropertiesTokens' cell
        toks = [x for x in row["PropertiesTokens"].replace("- ", "").split(" ") if x]
        # For every token in toks
        for tok in toks:
            # Check if that token is already a column
            setInd = len(tokSet)
            tokSet.add(tok)
            # If the token is new
            if(setInd < len(tokSet)):
                # Create a column of 0 for that token
                matrix[tok] = 0
            # Update the value of the cell in the row of the matrix with tok as column(obtaining the number of token for that row)
            matrix.at[index, tok] = matrix.at[index, tok] + 1
    
    # Return the DataFrame for RapidMiner usage
    # Parse the FCA matrix into the csv file
    matrix.to_csv(os.path.normpath(os.path.expanduser("ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_FCA.csv")))

    # Get the link of LiveSchema
    CKAN = helpers.get_site_protocol_and_host()
    CKAN_URL = CKAN[0]+"://" + CKAN[1]

    # Set the admin key of LiveSchema
    CKAN_KEY = "0587249a-c6e6-4b75-914a-075d88b16932"

    dataset = toolkit.get_action('package_show')(
        data_dict={"id": data_dict["dataset_name"]})

    # Iterate over every resource of the dataset
    for res in dataset["resources"]:
        # Check if they have the relative FCA matrix file
        if(res["format"] == "CSV" and res["name"] == dataset["name"]+"_FCA.csv"):
            # Delete the current FCA matrix
            dataset = toolkit.get_action('resource_delete')(
                data_dict={"id": res["id"]})
            break

    # Add the description of the FCA Matrix specifying the (eventual) set of predicates for the filtering process
    description = "FCA Matrix containing the information of"
    if(len(data_dict["strPredicates"].split()) == 0):
        description = description + " all the triples"
    else:
        strPredicates = ", ".join(data_dict.get("strPredicates", " ").split())
        description = description + " the filtered triples, which have the following predicates: " + strPredicates

    # Upload the csv file to LiveSchema
    requests.post(CKAN_URL+"/api/3/action/resource_create",
                data={"package_id": data_dict["dataset_name"], "format": "csv", "name": data_dict["dataset_name"]+"_FCA.csv", "description": description},
                headers={"X-CKAN-API-Key": CKAN_KEY},
                files=[("upload", file("ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_FCA.csv"))])

    # Remove the temporary csv file from the server
    os.remove("ckanext/liveschema_theme/public/" + data_dict["dataset_name"]+"_FCA.csv")

# Function that tokenize on capitalLetters the SubjectTerm, obtaining the simple words of its composition as strings separated by " "
def tokenTerm(term):
    # Get the lenght of the string to tokenize
    lenght = len(term)
    # Create the index used to scan the string
    index = 0
    # Create a list with the characters which compose the term
    termL = list(term)
    # Iterate over every character of the list
    for t in termL:
        # If the character is capitalized
        if(termL[index]).isupper():
            # Scan over the remaining right part of the term, excluding the character already visited
            for index_ in range(index+1, lenght):
                # If the next character is not a capital letter
                if((termL[index_].islower())):
                    # Make sure the previous character is a capitalLetter
                    termL[index_-1] = termL[index_-1].upper()
                    # End the iteration
                    break
                # Otherwise if the next character is a capitalLetter
                elif(termL[index_].isupper()):
                    # Modify it to obtain a non capital letter(in order not to exclude words composed only in capitalLetters)
                    termL[index_] = termL[index_].lower()
        # Update the index
        index += 1

    # Create a term from the correcterd list of characters obtained
    term = "".join(termL)

    # Create the returning string of tokens
    pTok = ""

    # Scan over the term in inverse order to tokenize the term
    for index in range(lenght-1, -1, -1):
        # If a character is a capitalLetter, a digit, or the first one(last one chronologically)
        if(term[index].isupper() or term[index].isdigit() or index == 0):
            # If the subTerm is >2, and its total lower is not present on the list of stopWords
            if((lenght-index)>2 and (term[index:lenght].lower() not in stopWords)):
                # Add the subTerm to the string of tokens 
                pTok = pTok + " " + term[index:lenght].lower()
            # Update the index of the last character
            lenght = index

    # Return the string of tokens
    return pTok