import os
from wikidataintegrator import wdi_login
from libs.GFFRecordsMapper import *
from BCBio import GFF
from libs.GFFRecordImporter import *
import sys
from getpass import getpass



def main():
    print("*********** Welcome to Wikidata GFF annotation importer tool v1.0 ***********")
    #  get GFF file path
    gff_path = os.path.abspath(input("Enter GFF file path: "))
    if not os.path.isfile(gff_path):
        print("Invalid path for a GFF file")
        exit(1)
    #  get the Q-ID
    #  confirm the usage of this Q-ID
    cond = False
    organism_name = ""
    QID = ""
    while not cond:
        QID = input("Enter the Q-ID of the Wikidata organism item: ")
        organism_name = get_wd_label(QID)
        if not organism_name:
            continue
        confirm = input("Are you sure that you want to connect the GFF records to '''" + organism_name + "'''? (Y/N):")
        if confirm == 'y' or confirm == 'Y':
            cond = True
        else:
            organism_name = ""
            cond = False
            exit_flag = input("Do you want to exit? (Y/N): ")
            if exit_flag == 'y' or exit_flag == 'Y':
                sys.exit()
    #  ask for login
    username = input("Enter your wikidata login username:  ")
    password = getpass(prompt="Enter your wikidata login password: ")
    login_instance = wdi_login.WDLogin(user=username, pwd=password)

    # retrieve the list of excluded records
    excluded_list = get_excluded_list(QID)
    print(str(len(excluded_list)) + " Genes are already in Wikidata")
    #  call the importer class
    gff_file = GFF.parse(open(gff_path, 'r'), target_lines=1)
    mapped_df = GFFRecordsMapper(gff_file).map_gene_data()
    importer_obj = GFFRecordImporter(QID, organism_name, mapped_df, excluded_list)
    importer_obj.send_for_import()


def get_wd_label(QID):
    query_file = open('query_templates/Label_Fetch_Query.rq', 'r')
    query_template = query_file.read()
    QUERY = query_template
    QUERY = QUERY.replace("#QID#", QID)
    results = WDItemEngine.execute_sparql_query(QUERY)['results']['bindings']
    item = ""
    if len(results) == 0:
        print("Query returns no items for the specified Q-ID.")
    elif len(results) == 1:
        for result in results:
            item = result['label']['value']
    else:
        print("Query returns more that Item for the same Q-ID.")
    query_file.close()
    return item


def get_excluded_list(QID):
    query_file = open('query_templates/EXCLUDED_LOCUS_TAG_QUERY.rq', 'r')
    query_template = query_file.read()
    QUERY = query_template
    QUERY = QUERY.replace("#QID#", QID)
    results = WDItemEngine.execute_sparql_query(QUERY)['results']['bindings']
    excluded_locus_tag_list = []
    if len(results) != 0:
        for result in results:
            excluded_locus_tag_list.append(result['NCBI_Locus_tag']['value'])
    else:
        print("Query returns nothing.")
    return excluded_locus_tag_list


if __name__ == '__main__':
    main()
