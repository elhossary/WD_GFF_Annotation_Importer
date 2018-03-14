from WDProteinRecord import *
from WDmRnaRecord import *
from WDncRnaRecord import *
from ItemImporter import *
from wikidataintegrator.wdi_core import WDItemEngine
import pandas as pd


class GFFRecordImporter:
    def __init__(self, Organism_QID, Organism_Name, Mapped_df, Excluded_Locus_Tag_list):
        self.Organism_QID = Organism_QID
        self.Organism_Name = Organism_Name
        self.Mapped_df = Mapped_df
        self.Excluded_Locus_Tag_list = Excluded_Locus_Tag_list

    def get_biotype(self, parent_rec, child_rec):
        parent_gbkey = ""
        child_gbkey = ""
        parent_biotype = ""
        child_ncrna_class = ""
        pseudo_flag = False
        bio_type = ""
        sub_types = []
        if 'gbkey' in parent_rec.qualifiers \
                and 'gbkey' in child_rec.qualifiers \
                and 'gene_biotype' in parent_rec.qualifiers:
            parent_gbkey = parent_rec.qualifiers['gbkey'][0]
            child_gbkey = child_rec.qualifiers['gbkey'][0]
            parent_biotype = parent_rec.qualifiers['gene_biotype'][0]
        else:
            print("Error getting the correct types of records, the file may not be supported")
            pass
        if 'ncrna_class' in child_rec.qualifiers:
            child_ncrna_class = child_rec.qualifiers['ncrna_class'][0]

        if parent_gbkey == "Gene":
            if 'pseudo' in parent_rec.qualifiers:
                if parent_rec.qualifiers['pseudo'][0] == 'true':
                    pseudo_flag = True
                else:
                    pseudo_flag = False
            elif 'pseudo' in parent_rec.qualifiers['gene_biotype'][0]:
                pseudo_flag = True
            else:
                pseudo_flag = False
            if 'protein_coding' == parent_biotype or 'CDS' == child_gbkey:
                bio_type = "protein"
                sub_types = ["protein"]
            elif 'RNA' in child_gbkey:
                if 'mRNA' == child_gbkey:
                    bio_type = "mRNA"
                    if parent_biotype == 'mRNA' or parent_biotype == 'mRNA_pseudogene':
                        sub_types = ['mRNA']
                    else:
                        print("Unknown sub type of mRNA")
                else:
                    bio_type = "ncRNA"
                    if 'rRNA' in child_gbkey:
                        if parent_biotype == 'rRNA' or parent_biotype == 'rRNA_pseudogene':
                            sub_types = ['rRNA']
                        else:
                            print("Unknown sub type of rRNA")
                    elif 'tRNA' in child_gbkey:
                        if parent_biotype == 'tRNA' or parent_biotype == 'tRNA_pseudogene':
                            sub_types = ['tRNA']
                        else:
                            print("Unknown sub type of tRNA")
                    elif 'tmRNA' in child_gbkey:
                        if parent_biotype == 'tmRNA' or parent_biotype == 'tmRNA_pseudogene':
                            sub_types = ['tmRNA']
                        else:
                            print("Unknown sub type of tmRNA")
                    elif 'ncRNA' in child_gbkey:
                        if parent_biotype == 'antisense_RNA' \
                                or child_ncrna_class == "antisense_RNA":
                            sub_types = ['antisense_RNA']
                        elif 'ncRNA' in parent_biotype \
                                and child_ncrna_class == 'other':
                            sub_types = ['unknown']
                        elif parent_biotype == 'SRP_RNA' \
                                and child_ncrna_class == 'SRP_RNA':
                            sub_types = ['SRP_RNA']
                        elif parent_biotype == 'RNase_P_RNA' \
                                and child_ncrna_class == 'RNase_P_RNA':
                            sub_types = ['RNase_P_RNA']
                    else:
                        print("Unsupported RNA type")
            else:
                print('error: cannot determine the bio type')
        else:
            print('error: cannot determine the bio type')
        if len(sub_types) == 0:
            print(child_rec.qualifiers)
        return bio_type, sub_types, pseudo_flag

    def get_QID_for_duplicated(self, locus_tag):
        item_QID = ""
        query_file = open('query_templates/FIND_ITEM_BY_LOCUS_TAG.rq', 'r')
        query_template = query_file.read()
        QUERY = query_template
        QUERY = QUERY.replace("#QID#", self.Organism_QID).replace("#LOCUS_TAG#", locus_tag)
        results = WDItemEngine.execute_sparql_query(QUERY)['results']['bindings']
        if len(results) == 0:
            print("Query returns no items for the specified Q-ID.")
        elif len(results) == 1:
            for result in results:
                item_QID = result['item']['value']
        else:
            for result in results:
                item_QID = result['item']['value']
                break
            print("Query returns more that Item for the same Q-ID.")
        query_file.close()
        return item_QID

    def check_existing_label(self, label_str):
        query_file = open('query_templates/CHECK_EXISTING_LABEL_QUERY.rq', 'r')
        query_template = query_file.read()
        QUERY = query_template
        QUERY = QUERY.replace("#QID#", self.Organism_QID).replace("#LABEL#", label_str)
        results = WDItemEngine.execute_sparql_query(QUERY)['results']['bindings']
        query_file.close()
        if len(results) == 0:
            return False
        else:
            return True

    def connect_fragmented_records(self, parent_child_return_QID):
        temp_locus = ""
        returned_QID_df = pd.DataFrame.from_records(parent_child_return_QID)
        if returned_QID_df.shape[0] > 0:
            returned_QID_df['IS_LOCUS_DUP'] = returned_QID_df['locus_tag'].duplicated(keep=False)
            ItemImporter_obj = ItemImporter("", "", [""], [""])
            for index, row in returned_QID_df.iterrows():
                if not row['IS_LOCUS_DUP']:
                    returned_QID_df.drop(row[index])
                else:
                    temp_locus = row['locus_tag']
                    for other_row in returned_QID_df.iterrows():
                        if other_row['locus_tag'] == temp_locus:
                            if row['PARENT_QID'] != other_row['PARENT_QID']:  # has part
                                ItemImporter_obj.items_connector(row['PARENT_QID'], 'P361', other_row['PARENT_QID'])
                            if row['CHILD_QID'] != other_row['CHILD_QID']:  # has part
                                ItemImporter_obj.items_connector(row['CHILD_QID'], 'P361', other_row['CHILD_QID'])
                    temp_locus = ""

    def send_for_import(self):

        parent_child_return_QID = []
        parent_QID = ""
        child_QID = ""
        rec_count = 0
        item_count = 0
        exclude_rec_count = 0
        self.Mapped_df['IS_DUPLICATED'] = self.Mapped_df['Parent_Record'].duplicated()
        for index, row in self.Mapped_df.iterrows():
            if row['Parent_Record'].qualifiers['locus_tag'][0] not in self.Excluded_Locus_Tag_list:
                rec_count += 1
                bio_type, sub_types, pseudo_flag = self.get_biotype(row['Parent_Record'], row['Record'])
                if bio_type == "ncRNA":
                    WDRecord_obj = WDncRnaRecord(row['GFF_ID'], row['Parent_Record'], row['Record'],
                                                 self.Organism_QID, self.Organism_Name)
                elif bio_type == "protein":
                    WDRecord_obj = WDProteinRecord(row['GFF_ID'], row['Parent_Record'], row['Record'],
                                                   self.Organism_QID, self.Organism_Name)
                elif bio_type == "mRNA":
                    WDRecord_obj = WDmRnaRecord(row['GFF_ID'], row['Parent_Record'], row['Record'],
                                                self.Organism_QID, self.Organism_Name)
                else:
                    print("unsupported bio type")
                    continue

                if row['IS_DUPLICATED']:
                    if self.check_existing_label(WDRecord_obj.get_WD_labels()[1]):
                        continue
                    parent_QID = self.get_QID_for_duplicated(row['Parent_Record'].qualifiers['locus_tag'][0])
                    if parent_QID == "":  # might cause a DUPLICATION, Just in case of miss-processing
                        parent_itemimporter_obj = ItemImporter(WDRecord_obj.get_WD_labels()[0],
                                                               WDRecord_obj.get_WD_desc(sub_types, pseudo_flag)[0],
                                                               WDRecord_obj.get_WD_aliases(),
                                                               WDRecord_obj.collect_WD_claims(sub_types, pseudo_flag)[0])
                        parent_QID = parent_itemimporter_obj.create_item()
                        parent_itemimporter_obj.add_statements(parent_QID)
                        item_count += 1

                    child_itemimporter_obj = ItemImporter(WDRecord_obj.get_WD_labels()[1],
                                                          WDRecord_obj.get_WD_desc(sub_types, pseudo_flag)[1],
                                                          WDRecord_obj.get_WD_aliases(),
                                                          WDRecord_obj.collect_WD_claims(sub_types, pseudo_flag)[1])

                    child_QID = child_itemimporter_obj.create_item()
                    item_count += 1
                    parent_child_return_QID.append({'PARENT_QID': parent_QID,
                                                    'CHILD_QID': child_QID,
                                                    'locus_tag': row['Parent_Record'].qualifiers['locus_tag'][0]})
                    child_itemimporter_obj.add_statements(child_QID)
                else:
                    parent_itemimporter_obj = ItemImporter(WDRecord_obj.get_WD_labels()[0],
                                                           WDRecord_obj.get_WD_desc(sub_types, pseudo_flag)[0],
                                                           WDRecord_obj.get_WD_aliases(),
                                                           WDRecord_obj.collect_WD_claims(sub_types, pseudo_flag)[0])
                    parent_QID = parent_itemimporter_obj.create_item()
                    parent_itemimporter_obj.add_statements(parent_QID)
                    item_count += 1
                    child_itemimporter_obj = ItemImporter(WDRecord_obj.get_WD_labels()[1],
                                                          WDRecord_obj.get_WD_desc(sub_types, pseudo_flag)[1],
                                                          WDRecord_obj.get_WD_aliases(),
                                                          WDRecord_obj.collect_WD_claims(sub_types, pseudo_flag)[1])
                    child_QID = child_itemimporter_obj.create_item()
                    item_count += 1
                    parent_child_return_QID.append({'PARENT_QID': parent_QID,
                                                    'CHILD_QID': child_QID,
                                                    'locus_tag': row['Parent_Record'].qualifiers['locus_tag'][0]})
                    child_itemimporter_obj.add_statements(child_QID)

                if parent_QID != "" and child_QID != "":
                    child_itemimporter_obj.items_connector(parent_QID, 'P688', child_QID, None, None)  # gene encodes product
                    child_itemimporter_obj.items_connector(child_QID, 'P702', parent_QID, None, None)  # product encoded by gene
                else:
                    print("Error: missing item Q-ID")

            else:
                exclude_rec_count += 1
        self.connect_fragmented_records(parent_child_return_QID)
        print("Import done successfully")
        print("WD items created: " + str(item_count))
        print("GFF records imported: " + str(rec_count))
        print("GFF records excluded: " + str(exclude_rec_count))
