# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 15:16:57 2024

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod


class ModifierServiceInterface(metaclass=ABCMeta):
    """
    order is defined by self.__order_chain()
    """

    @abstractmethod
    def add_chain(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def remove_chain(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def set_modifier_values(self, val):
        raise NotImplementedError()


class ModifierService(ModifierServiceInterface):
    def __init__(self):
        self.__current_modifier = None
        # chain always should have start and end
        self.__start_modifier = StartModifier('StartModifier')
        # make a default modifier chain list
        self.__modifier_chain_list = [self.__start_modifier,
                                      EndModifier('EndModifier')]
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)
        self.print_chain()

    # This is actual method run by DataService and return modified data
    def apply_modifier(self, data, modifier_list=None):
        # start the chain of responsibility and get modded data
        modified_data = self.__start_modifier.apply_modifier(data,
                                                             modifier_list)
        return modified_data

    def add_chain(self, modifier_name):
        # get a modifier factory
        modifier_factory = ModifierService.check_modifier_type(modifier_name)
        # get a new modifier name
        if modifier_name[-1].isdigit():
            new_modifier_name = modifier_name
        else:
            new_modifier_name = self.__num_maker(modifier_name)
        # create a modifier with their name
        new_modifier = modifier_factory.create_modifier(new_modifier_name)
        # add to the chain object list
        self.__modifier_chain_list.append(new_modifier)
        # sort and add start chain
        self.__modifier_chain_list = ModifierService.sort_chain_list(
            self.__modifier_chain_list)
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)

    def remove_chain(self, modifier_name):
        # remove modifier_name object from the list
        self.__modifier_chain_list = [obj for obj in self.__modifier_chain_list
                                      if obj.modifier_name != modifier_name]
        # sort and add start chain
        self.__modifier_chain_list = ModifierService.sort_chain_list(
            self.__modifier_chain_list)
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)

    @staticmethod
    def check_modifier_type(modifier_name):
        if 'TimeWindow' in modifier_name:
            return TimeWindowFactory()
        elif 'Roi' in modifier_name:
            return RoiFactory()
        elif 'Average' in modifier_name:
            return AverageFactory()
        elif 'View' in modifier_name:
            return ViewFactory()
        elif 'BlComp' in modifier_name:
            return BlCompFactory()
        else:
            print(f"{modifier_name} Factory done not exist.")

    # To make a number for modifier.
    def __num_maker(self, modifier_name):
        modifier_name_list = [modifier.modifier_name for modifier in
                              self.__modifier_chain_list]
        # Count existing modifier name
        i = 0
        while True:
            current_name = f'{modifier_name}{i}'
            if not current_name in modifier_name_list:
                break
            i += 1
        new_name = modifier_name + str(i)
        return new_name

    # modifier list always should be done by this list order.
    @staticmethod
    def sort_chain_list(old_obj_list):
        new_order_word_list = [
            'StartModifier',
            'TimeWindow',
            'Roi',
            'Average',
            'View',
            'BlComp',
            'EndModifier'
        ]
        # order to new list
        sorted_obj_list = []
        for word in new_order_word_list:
            for modifier_obj in old_obj_list:
                # check word in modifier_name
                if modifier_obj.modifier_name.startswith(word):
                    sorted_obj_list.append(modifier_obj)
        return sorted_obj_list

    @staticmethod
    def make_modifier_chain(modifier_chain_list):
        def set_chain(index):
            if index < len(modifier_chain_list) - 1:
                # make chain with modifier in inner function
                modifier_chain_list[index].set_next(
                    modifier_chain_list[index + 1])
                # next object
                set_chain(index + 1)

        # if there is objects in the list
        if modifier_chain_list:
            # start from the first object
            set_chain(0)
            # return the chain
        return modifier_chain_list[0] if modifier_chain_list else None

    def get_chain_list(self):
        list = []
        for modifier in self.__modifier_chain_list:
            list.append(modifier.modifier_name)
        return list

    def print_chain(self):
        print("ModifierService: modifier_chain_list -> ", end="")
        current_modifier = self.__start_modifier
        while current_modifier:
            print(f"{current_modifier.modifier_name}.", end="")
            current_modifier = current_modifier.next_modifier
        print("")

    def set_modifier_values(self, *args, **kwargs):
        raise NotImplementedError()


""" abstract factory """


class ModifierFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_modifier(self,
                        modifier_name: dict):  # data_tag = controller_key dict
        raise NotImplementedError()


"""concrete factory"""


class TimeWindowFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return TimeWindow(modifier_name)


class RoiFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Roi(modifier_name)


class AverageFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Average(modifier_name)


class ViewFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return View(modifier_name)


class BlCompFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return BlComp(modifier_name)


""" super class """


class ModifierHandler(metaclass=ABCMeta):  # BaseHandler
    def __init__(self, modifier_name):
        self.__modifier_name = modifier_name
        self.__next_modifier = None
        self.observer = []

    def set_next(self, next_modifier):
        self.__next_modifier = next_modifier
        return next_modifier

    def modifier_request(self, data, modifier_list):
        if self.__next_modifier:
            return self.__next_modifier.apply_modifier(data, modifier_list)

    @property
    def modifier_name(self):
        return self.__modifier_name

    @property
    def next_modifier(self):
        return self.__next_modifier


"""concrete modifier"""


class StartModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data, modifier_list):
        return super().modifier_request(data, modifier_list)


class TimeWindow(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data, modifier_list):
        if self.modifier_name in modifier_list:
            print("mod run")
        return super().modifier_request(data, modifier_list)


class Roi(ModifierHandler):
    pass


class Average(ModifierHandler):
    pass


class View(ModifierHandler):
    pass


class BlComp(ModifierHandler):
    pass


class EndModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data, modifier_list):
        return data
