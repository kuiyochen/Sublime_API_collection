import sublime
import sublime_plugin
from sublime import Region

class Get_indexCommand(sublime_plugin.TextCommand):
    def run(self, edit, function, **kwargs):
        if function == "get_index_1_by_1":
            self.get_index_1_by_1(edit, **kwargs)
        if function == "get_list_at_each_cursor":
            for region in list(self.view.sel())[::-1]:
                # if region.empty():
                #     continue
                self.get_list_at_this_cursor(edit, region, **kwargs)

    def get_list_at_this_cursor(self, edit, region, default_end_number = 20, max_limit = 500):
        selection = self.view.substr(region)
        start_number, end_number = self.get_start_end_number(selection, default_end_number)
        if (start_number == None) or (end_number == None):
            return
        if end_number - start_number > max_limit:
            print("out of max limit!")
            print("start_number: {}".format(start_number))
            print("end_number: {}".format(end_number))
            return
        if end_number <= start_number:
            print("end_number <= start_number")
            print("start_number: {}".format(start_number))
            print("end_number: {}".format(end_number))
            return
        region_start, region_end = region.begin(), region.end()
        self.view.replace(edit, region, "")
        self.view.sel().subtract(region)
        output_str = ""
        for number in range(start_number, end_number + 1):
            output_str += "\n"
            output_str += "{}".format(number)
        region_end = self.view.insert(edit, region_start, output_str) + region_start

    def get_start_end_number(self, selection, default_end_number):
        start_number, end_number = 0, default_end_number
        selection_split = selection.split(' ', 1)
        if len(selection_split) == 1 and (not selection == ""):
            if not selection_split[0].isdigit():
                return None, None
            end_number = int(selection_split[0])
        if len(selection_split) >= 2:
            if not (selection_split[0].isdigit() and selection_split[1].isdigit()):
                return None, None
            start_number = int(selection_split[0])
            end_number = int(selection_split[1])
        return start_number, end_number

    def get_index_1_by_1(self, edit):
        start_number = 0
        difference = 1
        regions = list(self.view.sel())
        if len(regions) < 2:
            return
        selection = self.view.substr(regions[0])
        start_number, difference = self.get_start_difference_number(selection)
        if (start_number == None) or (difference == None):
            return
        end_number = start_number + difference * (len(regions) - 1)
        index = end_number
        for region in regions[::-1]:
            self.view.replace(edit, region, "{}".format(index))
            index -= difference

    def get_start_difference_number(self, selection):
        start_number, difference = 0, 1
        selection_split = selection.split(' ', 1)
        if len(selection_split) == 1 and (not selection == ""):
            if not selection_split[0].isdigit():
                return None, None
            start_number = int(selection_split[0])
        if len(selection_split) >= 2:
            if not (selection_split[0].isdigit() and selection_split[1].isdigit()):
                return None, None
            start_number = int(selection_split[0])
            difference = int(selection_split[1])
        return start_number, difference