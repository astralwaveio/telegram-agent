class CityNotFoundError(Exception):
    def __init__(self):
        self.message = '地区名称未找到'
        super().__init__(self.message)

    pass


class CityAmbiguousError(Exception):
    def __init__(self, matches):
        self.matches = matches
        self.message = f'地区名称不唯一，请补充上级地区名。{self.matches}'
        super().__init__(self.message)
