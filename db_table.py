from db_entry import DBEntry


class DBTable:
    def __init__(self, name, fields, create_string):
        self.name = name
        self.fields = fields
        self.create_string = create_string

    @staticmethod
    def create_db():
        create_string = ''
        name = input('Table name: ').strip()
        name = DBTable.to_camel_case(name, True)
        fields = DBTable.get_fields()
        create_string += f'CREATE TABLE {name} (\n'
        create_string += f'{DBTable.fields_to_string(fields)}'
        create_string += ');'
        return DBTable(name, fields, create_string)

    @staticmethod
    def to_camel_case(text, table_name = False):
        words = text.replace("-", " ").replace("_", " ")
        words = words.split()
        if not len(words):
            return text
        if table_name:
            first_word = words[0].capitalize()
        else:
            first_word = words[0].lower()
        return first_word + "".join(i.capitalize() for i in words[1:])

    @staticmethod
    def get_fields():
        fields = []
        print('Type \"end\" to continue with entered fields')
        while True:
            field = input('Add field: ')
            if field.strip().lower() == 'end':
                print()
                break
            else:
                data_type = input('Datatype: ')
                fields.append([DBTable.to_camel_case(field), data_type])
        return fields

    @staticmethod
    def fields_to_string(fields):
        fields_string = ''
        for i in range(len(fields)):
            fields_string += fields[i][0] + ' ' + fields[i][1] + ',\n'
            if i >= len(fields) - 1:
                fields_string += f'PRIMARY KEY(' + fields[0][0] + ')\n'
        return fields_string
