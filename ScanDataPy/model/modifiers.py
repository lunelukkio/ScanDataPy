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
        # chain always should have start and end
        self.modifier_chain = [StartModifier('start_modifier'), EndModifier('EndModifier')]

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
        # add to the chain list
        self.modifier_chain.append(new_modifier)
        # sort and add start chain
        ModifierService.order_chain(self.modifier_chain)

    def remove_chain(self, modifier_name):
        # remove modifier_name object from the list
        self.modifier_chain = [obj for obj in self.modifier_chain if obj.modifier_name != modifier_name]

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
        modifier_name_list = [modifier_name for modifier_name in self.modifier_chain.modifier_name]
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
    def order_chain(old_list):
        new_order = [
            'StartModifier',
            'TimeWindow',
            'Roi',
            'Average',
            'View',
            'BlComp',
            'EndModifier'
        ]
        # order to new list
        sorted_list = sorted(old_list, key=lambda obj: (
            new_order.index(next((order for order in new_order if obj.modifier_name.startswith(order)), ''))
            , obj.name))



    def set_modifier_values(self, val):
        raise NotImplementedError()


""" abstract factory """
class ModifierFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_modifier(self, modifier_name: dict):  # key_dict = controller_key dict
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
        self.modifier_name = modifier_name
        self.__next_modifier = None
        self.observer = []

    def set_next(self, next_modifier):
        self.__next_modifier = next_modifier
        return next_modifier
    
    def modifier_request(self,modifier_name, data):
        if self.__next_modifier:
            return self.__next_modifier.apply_modifier(modifier_name, data)

"""concrete modifier"""

class StartModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
    def apply_modifier(self, modifier_name, data):
        return super().modifier_request(modifier_name, data)

class TimeWindow(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, modifier_list, data):
        if self.modifier_name in modifier_list:
            print("mod run")
            return super().modifier_request(modifier_list, data)
        else:
            return super().modifier_request(modifier_list, data)


class Roi(ModifierHandler):
    raise NotImplementedError()


class Average(ModifierHandler):
    raise NotImplementedError()


class View(ModifierHandler):
    raise NotImplementedError()


class BlComp(ModifierHandler):
    raise NotImplementedError()


class EndModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
    def modifier_request(self,modifier_name, data):
        return data
