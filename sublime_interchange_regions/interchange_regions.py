import sublime
import sublime_plugin
from sublime import Region

class Interchange_regionsCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        regions = list(self.view.sel())
        if len(regions) % 2 == 0:
            i = len(regions) - 1
            while i > 0:
                front = self.view.substr(regions[i - 1])
                back = self.view.substr(regions[i])
                self.view.replace(edit, regions[i], front)
                self.view.replace(edit, regions[i - 1], back)
                i -= 2
