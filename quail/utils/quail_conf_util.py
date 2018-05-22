from copy import copy

import yaml

from quail.utils.file_manipulation_mixin import FileManipulationMixin as file_util

class QuailConfig(file_util):
    """
    This class returns copied objects a lot so that the underlying data
    is not changed by a consumer of the data
    """
    def __init__(self, path):
        self.path = path
        self.data = self.read(path, 'yaml')

    def serialize(self):
        return yaml.dump(self.data,
                         indent=2,
                         width=80,
                         allow_unicode=True,
                         default_flow_style=False)

    def get_data(self):
        """
        Returns a copy of the data so you can look at it.
        Changes should not propagate back since it is a copy
        """
        return copy(self.data)

    def add_source(self, source_name, source_data):
        """
        Makes a copy of the source_data and puts it inside the config
        """
        if source_name in self.data['sources']:
            exit('You are trying to add a source that already exists, please pick a new name.')
        self.data['sources'][source_name] = copy(source_data)
        self.data['batches'].setdefault(source_name, {})
        return self.get_data()

    def get_source(self, source_name):
        if source_name not in self.data['sources']:
            exit('You are trying to get details for a source that does not exist. Please add the source.')
        return copy(self.data['sources'][source_name])

    def add_source_notes(self, source_name, note_key, note_data):
        """
        A source can have a notes section. This is for storing additional data that one may need.
        This is different from the top level keys in a source which govern connecting to that
        source and where to find it on the system
        """
        if source_name not in self.data['sources']:
            exit('You are trying to add notes for a source that does not exist. Please add the source.')
        self.data['sources'][source_name]['notes'][note_key] = copy(note_data)

    def add_batch(self, source_name, batch_name, batch_data, overwrite=True):
        """
        Makes a copy of the source_data and puts it inside the config
        """
        if source_name not in self.data['sources']:
            exit('You are trying to add a batch for a source that does not exist. Please add the source.')
        self.data['batches'][source_name].setdefault(batch_name, copy(batch_data))
        return self.get_data()

    def get_root(self):
        return copy(self.data['quail_root'])

    def get_most_recent_batch(self, source_name):
        """
        Returns the most recent batch path for a given source
        """
        try:
            source_batches = list(self.data['batches'][source_name].values())
            most_recent_batch_path = sorted(source_batches, key=lambda i: i['date'])[-1]['path']
        except:
            raise Exception("""
            Check that batches exist for project {proj}
            You may need to run:
            quail redcap get_meta {proj}
            quail redcap get_data {proj}
            """.format(proj=source_name))
        return copy(most_recent_batch_path)

    def get_passed_batch(self, source_name, batch):
        """
        Returns the path of a particular batch
        """
        try:
            source_batches = list(self.data['batches'][source_name].values())
            batch_path = [b['path'] for b in source_batches if b['date']==batch][0]
        except:
            raise Exception("""
            Check that batches exist for project {proj}, batch requested: {batch}
            You may need to run:
            quail redcap get_meta {proj}
            quail redcap get_data {proj}
            """.format(proj=source_name,batch=batch))
        return copy(batch_path)


    def save(self, path=None, backup_path=None):
        """
        Saves the config back to disk at the path specified,
        if not specified, it will save over the file at self.path
        this function will also first make a backup of the old file
        at the backup_path. If left blank, it will use the same
        directory as the quail conf with a bak added to the end
        """
        if not path:
            path = self.path
        if not backup_path:
            backup_path = self.path + '.bak'
        self.copyfile(path, backup_path)
        self.write(path, self.data, 'yaml')
