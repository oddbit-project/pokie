from pokie.http import PokieAuthView


class ProtectedView(PokieAuthView):
    def get(self):
        return self.success()
