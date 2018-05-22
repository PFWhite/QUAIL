from itertools import chain, repeat

from quail.utils.file_manipulation_mixin import FileManipulationMixin as file_util

class Instrumentor(file_util):
    def __init__(self, metadata_root):
        self.metadata = self.load_metadata(metadata_root)
        self.instruments = list(set([item['form_name'] for item in self.metadata]))
        self.unique_field = self.metadata[0]

        self.checkboxes = [field for field in self.metadata if field['field_type'] == 'checkbox']
        self.dropdowns = [field for field in self.metadata if field['field_type'] == 'dropdown']
        self.radios = [field for field in self.metadata if field['field_type'] == 'radio']
        self.redcap_generated_fields = self.get_redcap_fields()

    def get_redcap_fields(self):
        instruments = set([f['form_name'] for f in self.metadata])
        fields = []
        for instrument in instruments:
            fields.append(self.make_field(self.unique_field['field_name'], instrument))
            fields.append(self.make_field('redcap_event_name', instrument))
            fields.append(self.make_field('%s_complete' % instrument, instrument))
        return fields

    def make_field(self, field_name, instrument):
        return {
            'field_name': field_name,
            'form_name': instrument,
            'field_type': 'redcap_generated_field'
        }

    def load_metadata(self, metadata_root):
        for root, dirs, files in self.walk(metadata_root):
            for filename in files:
                if filename == 'metadata.json':
                    return self.read(self.join([root, filename]), 'json')

    def fieldnames_for_instrument(self, instrument_name):
        fields = [field for field in self.metadata
                  if field['form_name'] == instrument_name
                  and field['field_name'] != self.unique_field['field_name']]
        normal = [field for field in fields if field not in self.checkboxes]

        checkboxes = [field for field in self.checkboxes if field['form_name'] == instrument_name]
        parsed_select_choices = chain(*[self.parse_select_choices(field) for field in checkboxes])

        field_names = list(chain(
            [field['field_name'] for field in normal],
            [export_name for export_name, value, display in parsed_select_choices]
        ))
        texttype = repeat('TEXT')
        field_names.insert(1, '{}_complete'.format(instrument_name))
        # the instrument which contains the unique field will already define these
        # and use them as primary keys
        if instrument_name != self.unique_field['form_name']:
            field_names.insert(0, self.unique_field['field_name'])
            field_names.insert(0, 'redcap_event_name')

        return zip(field_names, texttype)

    def fields_for_instrument(self, instrument_name):
        return self.fieldnames_for_instrument(instrument_name)

    def parse_select_choices(self, field):
        choices = field['select_choices_or_calculations'].split('|')
        field_name = field['field_name']
        parsed = []
        for choice in choices:
            value = choice.split(',')[0].strip().replace("\'","\'\'")
            display = ','.join(choice.split(',')[1:]).strip().replace("\'","\'\'")
            export_name = field_name.strip() + '___' + value.strip().replace("\'","\'\'")
            parsed.append(( export_name, value, display ))
        return parsed

    def get_subject_fk(self):
        return {
            'field': self.unique_field['field_name'],
            'other_table': self.unique_field['form_name'],
            'other_key': self.unique_field['field_name'],
            'fk_sub_clause': ''
        }

    def get_field(self, field_name):
        """
        It is important to remember that there are redcap fields that are not
        in the metadata. These are the redcap_event name, and the FORMNAME_complete
        fields. These will never be found because they are special fields.
        Also there are the fields that have three underscores. these are the checkbox fields
        """
        matches = [field for field in self.metadata if field['field_name'] == field_name]
        if len(matches) == 1:
            return matches[0]
        elif field_name in [f['field_name'] for f in self.redcap_generated_fields]:
            return [f for f in self.redcap_generated_fields if f['field_name'] == field_name][0]
        elif '___' in field_name:
            return [f for f in self.metadata if f['field_name'] == field_name.split('___')[0]][0]
        else:
            raise Exception('too many matching fields for {} matches: {}'.format(field_name, len(matches)))

    def is_lookup_field(self, field_name):
        # checks to see if the field_name corresponds to a field type that
        # needs a lookup, these are checkbox, dropdown, and radio
        if (field_name == 'redcap_event_name'):
            return False
        field = self.get_field(field_name)
        lookups = [
            'checkbox', 'dropdown', 'radio'
        ]
        return field['field_type'] in lookups

    def make_lookup_foreign_keys(self, field_name, field_type):
        # get the object that is required for the create instrument
        # function in the redcap_schema.sql file
        field = self.get_field(field_name)
        return {
            'field': field_name,
            'other_table': field_type + '_' + field_name,
            'other_key': 'val',
            'fk_sub_clause': ''
        }

    def get_instrument_table(self, instrument_name):
        # When someone need to support repeating forms
        # add another field to this primary keys thing so
        # that it makes them unique with it
        # also make sure you are pulling the data down
        primary_keys = [
            {'field': self.unique_field['field_name'], 'type': 'TEXT'},
            {'field': 'redcap_event_name', 'type': 'TEXT'}
        ]

        fields = self.fields_for_instrument(instrument_name)
        fields = [field for field in fields if field[0] != self.unique_field['field_name']]
        fields = [field for field in fields if field[0] != 'redcap_event_name']

        return {
            'name': instrument_name,
            'primary_keys': primary_keys,
            'fields': fields,
            'foreign_keys': [self.make_lookup_foreign_keys(field, field_type)
                             for field, field_type
                             in self.fields_for_instrument(instrument_name)
                             if self.is_lookup_field(field)]
        }

    def get_all_instruments(self):
        return [self.get_instrument_table(name) for name in self.instruments]

    def get_all_checkboxes(self):
        return [
            {
                'name': field['field_name'],
                'form_name': field['form_name'],
                'options': self.parse_select_choices(field)
            }
            for field in self.checkboxes
        ]

    def get_all_dropdowns(self):
        return [
            {
                'name': field['field_name'],
                'form_name': field['form_name'],
                'type': 'dropdown',
                'options': [(val, disp) for ex, val, disp in self.parse_select_choices(field)]
            }
            for field in self.dropdowns
        ]

    def get_all_radios(self):
        return [
            {
                'name': field['field_name'],
                'form_name': field['form_name'],
                'type': 'radio',
                'options': [(val, disp) for ex, val, disp in self.parse_select_choices(field)]
            }
            for field in self.radios
        ]
