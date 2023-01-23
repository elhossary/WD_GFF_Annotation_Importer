class WDBioGffRecord:
    def __init__(self, GFF_ID, parent_rec, child_rec):
        self.GFF_ID = GFF_ID
        self.parent_rec = parent_rec
        self.child_rec = child_rec

    def get_parent_location(self):
        return int(self.parent_rec.location.start), int(self.parent_rec.location.end), \
               int(self.parent_rec.location.strand)

    def get_child_location(self):
        return int(self.child_rec.location.start), int(self.child_rec.location.end), \
               int(self.child_rec.location.strand)

    def get_parent_name(self):
        r_name = ""
        if 'Name' in self.parent_rec.qualifiers and 'gene' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers["gene"][0] == self.parent_rec.qualifiers["Name"][0]:
                r_name = self.parent_rec.qualifiers["gene"][0]
            else:
                r_name = self.parent_rec.qualifiers["gene"][0] + " " + self.parent_rec.qualifiers["Name"][0]
        elif 'Name' in self.parent_rec.qualifiers and 'gene' not in self.parent_rec.qualifiers:
            r_name = self.parent_rec.qualifiers["Name"][0]
        elif 'Name' not in self.parent_rec.qualifiers and 'gene' in self.parent_rec.qualifiers:
            r_name = self.parent_rec.qualifiers["gene"][0]
        else:
            print("error in naming an item")

        if 'part' in self.parent_rec.qualifiers:
            r_name += ' Part ' + self.parent_rec.qualifiers['part'][0]

        if 'product' in self.child_rec.qualifiers:
            r_name += ' encodes: ' + self.child_rec.qualifiers['product'][0]
        else:
            if 'Note' in self.child_rec.qualifiers:
                r_name += ' encodes: ' + self.child_rec.qualifiers['Note'][0]
            else:
                print(self.child_rec)

        if 'locus_tag' in self.parent_rec.qualifiers:
            r_name += ' ' + self.parent_rec.qualifiers['locus_tag'][0]



        if len(r_name) > 250:
            r_name.replace("encodes: ", ", ")
            if len(r_name) > 250:
                trim_len = len(r_name) - 250
                r_name = r_name[: -trim_len]
            print("Please manually check the label of this record on Wikidata: " + r_name
                  + ", Because it exceeds the limit of max characters")
        return r_name

    def get_child_name(self):
        r_name = ""
        if 'product' in self.child_rec.qualifiers:
            r_name = self.child_rec.qualifiers['product'][0]
        else:
            if 'Note' in self.child_rec.qualifiers:
                r_name = self.child_rec.qualifiers['Note'][0]
            else:
                print(self.child_rec)

        if 'part' in self.parent_rec.qualifiers:
            r_name += ' Part ' + self.parent_rec.qualifiers['part'][0]

        r_name += " encoded by: "

        if 'Name' in self.parent_rec.qualifiers and 'gene' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers["gene"][0] == self.parent_rec.qualifiers["Name"][0]:
                r_name += self.parent_rec.qualifiers["gene"][0]
            else:
                r_name += self.parent_rec.qualifiers["gene"][0] + " " + self.parent_rec.qualifiers["Name"][0]
        elif 'Name' in self.parent_rec.qualifiers and 'gene' not in self.parent_rec.qualifiers:
            r_name += self.parent_rec.qualifiers["Name"][0]
        elif 'Name' not in self.parent_rec.qualifiers and 'gene' in self.parent_rec.qualifiers:
            r_name += self.parent_rec.qualifiers["gene"][0]
        else:
            print("error in naming an item")

        if 'locus_tag' in self.parent_rec.qualifiers:
            r_name += ' ' + self.parent_rec.qualifiers['locus_tag'][0]
        if len(r_name) > 250:
            r_name.replace("encoded by: ", ", ")
            if len(r_name) > 250:
                trim_len = len(r_name) - 250
                r_name = r_name[: -trim_len]
            print("Please manually check the label of this record on Wikidata: " + r_name
                  + ", Because it exceeds the limit of max characters")
        return r_name

    def get_aliases(self):
        r_aliases = []
        if 'gene_synonym' in self.parent_rec.qualifiers:
            for i in self.parent_rec.qualifiers['gene_synonym']:
                if i not in r_aliases:
                    r_aliases.append(i)
        if 'gene' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers['gene'][0] not in r_aliases:
                r_aliases.append(self.parent_rec.qualifiers['gene'][0])
        if 'Name' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers['Name'][0] not in r_aliases:
                r_aliases.append(self.parent_rec.qualifiers['Name'][0])
        if 'locus_tag' in self.parent_rec.qualifiers:
            if self.parent_rec.qualifiers['locus_tag'][0] not in r_aliases:
                r_aliases.append(self.parent_rec.qualifiers['locus_tag'][0])
        return r_aliases

    def get_desc_adds(self):
        r_desc_adds = ""
        if 'Note' in self.child_rec.qualifiers:
            r_desc_adds += ', Note: ' + self.child_rec.qualifiers['Note'][0]
        if 'transl_except' in self.child_rec.qualifiers:
            r_desc_adds += ', translated except: ' + self.child_rec.qualifiers['transl_except'][0]
        if 'exception' in self.child_rec.qualifiers:
            r_desc_adds += ', exception: ' + self.child_rec.qualifiers['exception'][0]
        return r_desc_adds