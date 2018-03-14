from WDBioGffRecord import *


class WDncRnaRecord(WDBioGffRecord):
    def __init__(self, GFF_ID, parent, child, QID, Organism_Name):
        super().__init__(GFF_ID, parent, child)
        self.QID = QID
        self.Organism_Name = Organism_Name

    # --------------------------WD ITEM HEADER--------------------------
    def get_WD_labels(self):
        return super().get_parent_name(), super().get_child_name()

    def get_WD_desc(self, sub_types, pseudo_flag):
        trim_len = 0
        parent_desc = ""
        child_desc = ""
        added_sub_types = ""
        for sub_type in sub_types:
            added_sub_type = "'" + sub_type.replace('_', ' ') + "' "
            if pseudo_flag:
                parent_desc = 'Microbial gene (pseudogene) encodes a non-coding RNA ' + added_sub_type + 'found in ' \
                              + self.Organism_Name + super().get_desc_adds()
                child_desc = 'Microbial a non-coding RNA ' + added_sub_type + 'encoded by a pseudogene found in ' \
                             + self.Organism_Name \
                             + super().get_desc_adds()
            else:
                parent_desc = 'Microbial gene encodes a non-coding RNA ' + added_sub_type + 'found in ' \
                              + self.Organism_Name + super().get_desc_adds()
                child_desc = 'Microbial non-coding RNA ' + added_sub_type + 'found in ' \
                             + self.Organism_Name + super().get_desc_adds()
        if len(parent_desc) > 250:
            trim_len = len(parent_desc) - 250
            parent_desc = parent_desc[: -trim_len]
            print("Please manually check the description of this record on Wikidata: " + self.get_WD_labels()[0]
                  + ", Because it exceeds the limit of max characters")
        if len(child_desc) > 250:
            trim_len = len(child_desc) - 250
            child_desc = child_desc[: -trim_len]
            print("Please manually check the description of this record on Wikidata: " + self.get_WD_labels()[1]
                  + ", Because it exceeds the limit of max characters")
        return parent_desc, child_desc

    def get_WD_aliases(self):
        return super().get_aliases()

    # --------------------------WD ITEM CLAIMS--------------------------

    def make_WD_definitions(self, sub_types, pseudo_flag):
        r_list_parent = []
        r_list_child = []
        r_list_parent.append({'property': 'P703', 'target': self.QID})  # found in taxon
        r_list_parent.append({'property': 'P31', 'target': 'Q7187'})  # instance of gene
        r_list_parent.append({'property': 'P279', 'target': 'Q7187'})  # subclass of gene
        if pseudo_flag:
            r_list_parent.append({'property': 'P279', 'target': 'Q277338'})  # subclass of pseudogene
    # -----------------------------------------------------------------------------------------------------------------
        r_list_child.append({'property': 'P703', 'target': self.QID})  # found in taxon
        r_list_child.append({'property': 'P31', 'target': 'Q11053'})  # instance of RNA
        r_list_child.append({'property': 'P31', 'target': 'Q427087'})  # instance of Non-coding RNA
        flg = True
        for sub_type in sub_types:
            if sub_type == 'rRNA':
                r_list_child.append({'property': 'P279', 'target': 'Q215980'})  # subclass of rRNA
            if sub_type == 'tRNA':
                r_list_child.append({'property': 'P279', 'target': 'Q201448'})  # subclass of transfer RNA
            if sub_type == 'tmRNA':
                r_list_child.append({'property': 'P279', 'target': 'Q285904'})  # subclass of Transfer-messenger RNA
            if sub_type == 'antisense_RNA':
                r_list_child.append({'property': 'P279', 'target': 'Q423832'})  # subclass of Antisense RNA
            if sub_type == 'unknown':
                r_list_child.append({'property': 'P279', 'target': 'Q24238356'})  # subclass of unknown
            if sub_type == 'SRP_RNA':
                r_list_child.append({'property': 'P279', 'target': 'Q424665'}) # subclass of signal recognition particle
            if sub_type == 'RNase_P_RNA':
                r_list_child.append({'property': 'P279', 'target': 'Q1012651'})  # subclass of RNase P
        return r_list_parent, r_list_child

    def make_WD_loc(self):
        r_list_parent = []
        r_list_child = []
        if 'source' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers['source'][0] == 'RefSeq':
                r_list_parent.append(
                    {'property': 'P644', 'target': str(self.get_parent_location()[0]), 'qualifier_property': 'P2249',
                     'qualifier_target': str(self.GFF_ID)})
                r_list_parent.append(
                    {'property': 'P645', 'target': str(self.get_parent_location()[1]), 'qualifier_property': 'P2249',
                     'qualifier_target': str(self.GFF_ID)})
                # elif self.parent_rec.qualifiers['source'][0] == '':
                if self.get_parent_location()[2] == 1:
                    r_list_parent.append({'property': 'P2548', 'target': 'Q22809680', 'qualifier_property': 'P2249',
                                          'qualifier_target': str(self.GFF_ID)})
                elif self.get_parent_location()[2] == -1:
                    r_list_parent.append({'property': 'P2548', 'target': 'Q22809711', 'qualifier_property': 'P2249',
                                          'qualifier_target': str(self.GFF_ID)})
                else:
                    print("Fatal error in getting the strand orientation for the parent")
            else:
                r_list_parent.append({'property': 'P644', 'target': str(self.get_parent_location()[0])})
                r_list_parent.append({'property': 'P645', 'target': str(self.get_parent_location()[1])})
                if self.get_parent_location()[2] == 1:
                    r_list_parent.append({'property': 'P2548', 'target': 'Q22809680'})
                elif self.get_parent_location()[2] == -1:
                    r_list_parent.append({'property': 'P2548', 'target': 'Q22809711'})
                else:
                    print("Fatal error in getting the strand orientation for the parent")
        else:
            r_list_parent.append({'property': 'P644', 'target': str(self.get_parent_location()[0])})
            r_list_parent.append({'property': 'P645', 'target': str(self.get_parent_location()[1])})
            if self.get_parent_location()[2] == 1:
                r_list_parent.append({'property': 'P2548', 'target': 'Q22809680'})
            elif self.get_parent_location()[2] == -1:
                r_list_parent.append({'property': 'P2548', 'target': 'Q22809711'})
            else:
                print("Fatal error in getting the strand orientation for the parent")

        if 'source' in self.child_rec.qualifiers:
            if self.child_rec.qualifiers['source'][0] == 'RefSeq':
                r_list_child.append(
                    {'property': 'P644', 'target': str(self.get_child_location()[0]), 'qualifier_property': 'P2249',
                     'qualifier_target': str(self.GFF_ID)})
                r_list_child.append(
                    {'property': 'P645', 'target': str(self.get_child_location()[1]), 'qualifier_property': 'P2249',
                     'qualifier_target': str(self.GFF_ID)})
                # elif self.child_rec.qualifiers['source'][0] == '':
                if self.get_child_location()[2] == 1:
                    r_list_child.append({'property': 'P2548', 'target': 'Q22809680', 'qualifier_property': 'P2249',
                                         'qualifier_target': str(self.GFF_ID)})
                elif self.get_child_location()[2] == -1:
                    r_list_child.append({'property': 'P2548', 'target': 'Q22809711', 'qualifier_property': 'P2249',
                                         'qualifier_target': str(self.GFF_ID)})
                else:
                    print("Fatal error in getting the strand orientation for the child")
            else:
                r_list_child.append({'property': 'P644', 'target': str(self.get_child_location()[0])})
                r_list_child.append({'property': 'P645', 'target': str(self.get_child_location()[1])})
                if self.get_child_location()[2] == 1:
                    r_list_child.append({'property': 'P2548', 'target': 'Q22809680'})
                elif self.get_child_location()[2] == -1:
                    r_list_child.append({'property': 'P2548', 'target': 'Q22809711'})
                else:
                    print("Fatal error in getting the strand orientation for the child")
        else:
            r_list_child.append({'property': 'P644', 'target': str(self.get_child_location()[0])})
            r_list_child.append({'property': 'P645', 'target': str(self.get_child_location()[1])})
            if self.get_child_location()[2] == 1:
                r_list_child.append({'property': 'P2548', 'target': 'Q22809680'})
            elif self.get_child_location()[2] == -1:
                r_list_child.append({'property': 'P2548', 'target': 'Q22809711'})
            else:
                print("Fatal error in getting the strand orientation for the child")
        return r_list_parent, r_list_child

    def make_WD_identifiers(self):
        r_list_parent = []
        r_list_child = []
        if 'locus_tag' in self.parent_rec.qualifiers:
            r_list_parent.append({'property': 'P2393', 'target': self.parent_rec.qualifiers['locus_tag'][0]})
        if 'Dbxref' in self.parent_rec.qualifiers:
            for db_id in self.parent_rec.qualifiers['Dbxref']:
                if 'GeneID' in db_id:
                    r_list_parent.append({'property': 'P351', 'target': db_id.split(':', 1)[-1]})
                # elif 'EcoGene' in db_id:
                #     r_list_parent.append({'property': '', 'target': db_id.split(':', 1)[-1]})
                else:
                    print("Unsupported type of identifiers " + db_id)
        # -------------------------------------------------------------------------------------------------------------
        if 'Dbxref' in self.child_rec.qualifiers:
            for db_id in self.child_rec.qualifiers['Dbxref']:
                if 'GeneID' in db_id:
                    r_list_child.append({'property': 'P351', 'target': db_id.split(':', 1)[-1]})
                elif 'Genbank' in db_id:
                    r_list_child.append({'property': 'P637', 'target': db_id.split(':', 1)[-1]})
                elif 'UniProtKB/Swiss-Prot' in db_id:
                    r_list_child.append({'property': 'P352', 'target': db_id.split(':', 1)[-1]})
                # elif 'ASAP' in db_id:
                #     r_list_child.append({'property': '', 'target': db_id.split(':', 1)[-1]})
                # elif 'EcoGene' in db_id:
                #     r_list_parent.append({'property': '', 'target': db_id.split(':', 1)[-1]})
                else:
                    print("Unsupported type of identifiers " + db_id)
        return r_list_parent, r_list_child

    # --------------------------Collection--------------------------

    def collect_WD_claims(self, sub_types, pseudo_flag):
        r_list_parent = []
        r_list_child = []
        r_list_parent.extend(self.make_WD_definitions(sub_types, pseudo_flag)[0])
        r_list_child.extend(self.make_WD_definitions(sub_types, pseudo_flag)[1])
        r_list_parent.extend(self.make_WD_loc()[0])
        r_list_child.extend(self.make_WD_loc()[1])
        r_list_parent.extend(self.make_WD_identifiers()[0])
        r_list_child.extend(self.make_WD_identifiers()[1])
        return r_list_parent, r_list_child

