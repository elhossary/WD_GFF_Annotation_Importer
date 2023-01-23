import sys
import pandas as pd
import pywikibot


class ItemImporter:
    def __init__(self, label, description, aliases_list, claims):
        self.label = label  # pass a string of english only name
        self.description = description  # pass a string of english only description
        self.aliases_list = aliases_list  # pass a list of aliases in english only
        self.claims = claims  # pass a list of dictionaries that contain claims

    def create_item(self):
        data = {"labels": {"en": self.label},
                "descriptions": {'en': self.description},
                "aliases": {"en": self.aliases_list}}
        site = pywikibot.Site("wikidata", "wikidata")
        new_item = pywikibot.ItemPage(site)
        new_item.editEntity(data, summary=u'Edited item: set labels, descriptions, aliases')
        print("New item created: " + new_item.getID())
        return new_item.getID()

    def get_target_type(self, property_id):
        target_types_df = pd.read_csv("Target_Types_Dictionary.csv", names=['property', 'target_type'])
        r_target_type = ""
        for index, row in target_types_df.iterrows():
            if row['property'] == property_id:
                r_target_type = row['target_type']
                break
        return r_target_type

    def items_connector(self, nodeA, property_id, nodeB, qual_prop, qual_trgt):  # a function that connects 2 items with property
        target_type = self.get_target_type(property_id)
        is_exit = ""
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()
        item = pywikibot.ItemPage(repo, nodeA)
        claim = pywikibot.Claim(repo, property_id)
        if target_type == "":
            print("Statement ignored: couldn't get the correct type of this property: " + property_id)
            print("Please add this property to file 'Target_Types_Dictionary.csv'")
            while is_exit != "Y" and is_exit != "y" and is_exit != "N" and is_exit != "n":
                is_exit = input("want to exit? (Y/N):")
        elif target_type == "WD_item":
            target = pywikibot.ItemPage(repo, nodeB)
            claim.setTarget(target)
            item.addClaim(claim, summary=u'Adding claim')
        elif target_type == "string":
            claim.setTarget(nodeB)
            item.addClaim(claim, summary=u'Adding claim')
        else:
            print("Fatal error, Check file 'Target_Types_Dictionary.csv'")
            is_exit = "Y"
        if is_exit == "Y" or is_exit == "y":
            sys.exit()
        if qual_prop is not None and qual_trgt is not None:
            if self.get_target_type(qual_prop) == "":
                print("Statement ignored: couldn't get the correct type of this property: " + property_id)
                print("Please add this property to file 'Target_Types_Dictionary.csv'")
            elif self.get_target_type(qual_prop) == "WD_item":
                qualifier = pywikibot.Claim(repo, qual_prop)
                target = pywikibot.ItemPage(repo, qual_trgt)
                qualifier.setTarget(target)
                claim.addQualifier(qualifier, summary=u'Adding a qualifier.')
            elif self.get_target_type(qual_prop) == "string":
                qualifier = pywikibot.Claim(repo, qual_prop)
                qualifier.setTarget(qual_trgt)
                claim.addQualifier(qualifier, summary=u'Adding a qualifier.')
            else:
                print("Fatal error, Check file 'Target_Types_Dictionary.csv'")

    def add_statements(self, item_id):
        cnt = 0
        for i in self.claims:
            try:
                if 'qualifier_property' in i and 'qualifier_target' in i:
                    self.items_connector(item_id, i['property'], i['target'], i['qualifier_property'], i['qualifier_target'])
                else:
                    self.items_connector(item_id, i['property'], i['target'], None, None)
                cnt = cnt + 1
            except OSError as err:
                print("OS error: {0}".format(err))
            except ValueError:
                print("Value Error in " + i['target'])
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        print(str(cnt) + ' statements')
    # calling the inner functions
    item_id = ""

