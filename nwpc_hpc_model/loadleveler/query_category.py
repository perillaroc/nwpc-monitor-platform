import copy


class QueryCategory(object):
    def __init__(
            self,
            category_id=".valid_id",
            display_name="",
            label="",
            record_parser_class=None,
            record_parser_arguments=tuple(),
            value_saver_class=None,
            value_saver_arguments=tuple()
    ):
        self.id = category_id
        self.display_name = display_name
        self.label = label

        self.record_parser = None
        self.value_saver = None

        if record_parser_class is not None:
            self.record_parser = record_parser_class(*record_parser_arguments)

        if value_saver_class is not None:
            self.value_saver = value_saver_class(*value_saver_arguments)

    def __deepcopy__(self, memodict={}):
        new_object = QueryCategory()

        new_object.id = self.id
        new_object.display_name = self.display_name
        new_object.label = self.label

        if self.record_parser:
            new_object.record_parser = copy.deepcopy(self.record_parser)

        new_object.value_saver = self.value_saver
        return new_object


class QueryCategoryList(list):
    def contains_id(self, category_id):
        for a_category in self:
            if a_category.id == category_id:
                return True
        return False

    def index_from_id(self, category_id):
        for i in range(0, len(self)):
            if self[i].id == category_id:
                return i
        return -1

    def category_from_id(self, category_id):
        for a_category in self:
            if a_category.id == category_id:
                return a_category
        return None

    def contains_label(self, label):
        for a_category in self:
            if a_category.label == label:
                return True
        return False

    def index_from_label(self, label):
        for i in range(0, len(self)):
            if self[i].label == label:
                return i
        return -1

    def category_from_label(self, label):
        for a_category in self:
            if a_category.label == label:
                return a_category
        return None
