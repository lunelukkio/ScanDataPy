# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 13:42:38 2023

@author: lunelukkio@gmail.com
"""

class KeyManager:
    def __init__(self):
        self.filename_list = []
        self.attribute_list = []  # ['Data', 'Text']
        self.data_type_list = []  # ['FluoFramesCh1', 'FluoTraceCh1', 'ElecTraceCh1', 'Header', 'Default']
        self.origin_list = []  # ['File', 'Roi1']

        self.modifier_list = []  # ['TimeWindow3','Roi1','Average1','TagMaker0']

        self.ch_list = []
        self.roi_list = []
        self.bl_roi_list = []

    # set if tag is in the list the tag will be removed, if not tag will be added.
    def set_tag(self, tag_list_name, tag):  # e.g. (filename_dict, '30503A001.tsm')
        list_name = getattr(self, f"{tag_list_name}")  # get list
        if tag in list_name:
            list_name.remove(tag)
            print(f"KeyManager: removed {tag} from {list_name} ")
        else:
            list_name.append(tag)
            print(f"KeyManager: added {tag} to {list_name} ")
        # need this line because list_name is just like a copy.
        setattr(self, f"{tag_list_name}", list_name)

    # remove old tag and add new tag
    def replace_tag(
        self, list_name, old_tag, new_tag
    ):  # e.g. old_tag='Roi' new_tag='Roi1'
        # get list
        if hasattr(self, list_name):
            current_list = getattr(self, list_name)
            # delete old_tag from the list
            current_list = [item for item in current_list if old_tag not in item]
            current_list.append(new_tag)
            setattr(self, list_name, current_list)
            print(f"KeyManager: new_list of {list_name} = {current_list}")
        else:
            print(f"There is no {list_name} in the class")

    def get_list(self, list_name):
        if hasattr(self, list_name):
            return getattr(self, list_name)

    # get key dict combinations from whole dict.  convert variable names to 'dictionary keys'.
    # val = True: True combination, False: False combination, None: whole combination
    def get_dicts_from_tag_list(self) -> list:
        result = []
        # add ch to data_type_list
        datatype_list_with_ch = []
        for item in self.data_type_list:
            for ch in self.ch_list:
                datatype_list_with_ch.append(item + ch)

        all_dicts = [
            [
                self.filename_list,
                "Filename",
            ],  # the second name because a key of dictionary
            [self.attribute_list, "Attribute"],
            [datatype_list_with_ch, "DataType"],
            [self.origin_list, "Origin"],
        ]

        # internal function
        def recursive_combinations(current_combination, remaining_lists):
            if not remaining_lists:  # if there is no remaining_dicts,
                # after the last dict, the result has dict combinations
                result.append(current_combination)  # add a dict to the list
                return
            # take the first from the remaining dicts
            current_list, field_name = remaining_lists[0]
            # check key is the same as status
            for tag in current_list:
                # shallow copy for non effect of original data
                new_combination = current_combination.copy()
                new_combination[field_name] = tag
                # delete the current remaining object
                recursive_combinations(new_combination, remaining_lists[1:])

        # start from this line
        recursive_combinations({}, all_dicts)

        return result

    def print_infor(self):
        print("===================== Key Manager =========================")
        print(f"filename_list        = {self.filename_list}")
        print(f"attribute_list       = {self.attribute_list}")
        print(f"data_type_list       = {self.data_type_list}")
        print(f"origin_list          = {self.origin_list}")
        print("")
        print(f"modifier_list        = {self.modifier_list}")
        print(f"ch_list              = {self.ch_list}")
        print(f"roi_list    = {self.roi_list}")
        print(f"bl_roi_list    = {self.bl_roi_list}")

        print("===========================================================")

    def reset(self):
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, list):
                setattr(self, attr_name, [])
                print(f"{attr_name} has been reset to an empty list")

class KeyTools:
    """key modify"""

    # extract dict from original.  e.g. extract_list=['Filename', 'Ch', 'Origin'] original_dict={'Filename': '20408B002.tsm', 'ControllerName': 'ROI1', 'Ch': 'Ch1'}
    @staticmethod
    def extract_key(original_dict, extract_list):
        return {key: original_dict[key] for key in extract_list if key in original_dict}

        # delete tail numbers

    @staticmethod
    def remove_tail_numbers(input_string):
        result = re.sub(r"\d+$", "", input_string)
        return result

    @staticmethod
    def take_ch_from_str(input_string):
        pattern = r"Ch\d+"
        match = re.search(pattern, input_string)
        if match:
            matched_part = match.group()  # matched part
            start = match.start()  # matched first cha
            end = match.end()  # matched end cha
            before_match = input_string[:start]  # before matched
            after_match = input_string[end:]  # after matched  # noqa: F841
            return matched_part, before_match
        # if no match return None
        return None