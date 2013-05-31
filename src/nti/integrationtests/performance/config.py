import ConfigParser
import itertools
import inspect
import os.path

""" Config files are typically partitioned into sections. This object represents the values stored in a single section by
    creating dictionaries of attribute-value pairs for each unique combination of comma-separated parameters in config-file. 
    This allows suites of tests to be created, which use different parameter values, using a single config file. """
class _SectionConfigs:
    # List of dictionaries, where each dictionary is a unique combination of the comma-separated values specified in config-file
    sectionConfigs = []

    # If necessary values are not provided in config file, provide default values when appropriate
    default_values = { 'serialize': True,
                    'database_file': None,
                    'db_batch': False,
                    'run_time': None,
                    'max_iterations': None,
                    'runners': 8,
                    'target_args': None,
                    'use_threads': False,
                    'call_wait_time': 0,
                    'target_args': None,
                    'test_setup': None,
                    'test_teardown': None,
                    'section_setup': None,
                    'section_teardown': None }

    """ If a critical value was not provided in config file, and a reasonable default value can be assumed, insert it into list """
    def _insert_default_values(self, labels, values):
        missing = set(self.default_values) - set(labels)

        for label in missing:
            labels = labels + (label,)
            values.append( [self.default_values[label]] )

        return labels, values

    """ Is this string a boolean? """
    def _is_boolean(self, value):
        value = value.lower()
        return value in ['true', 'false', 'yes', 'no', 'on', 'off']

    """ Determine if this string is True or False """
    def _evaluate_boolean(self, value):
        assert self._is_boolean(value), "value is not boolean and cannot be evaluated: %r" % value
        return value.lower() in ['true', 'yes', 'on']

    """ Is this string a float? """
    def _is_float(self, value):
        # String is not of form ##.##, so cannot be a float
        if len(value.split('.')) != 2: return False

        # If string is in form ##.## and both sides are numbers, then string is a float
        num, dec = value.split('.')
        return num.isdigit() and dec.isdigit()

    """ Is this string a number? """
    def _is_num(self, value):
        return value.isdigit()

    """ Convert each string in list to a bool, int, float, or string, depending on its type """
    def _evaluate_strings(self, strngs):
        for idx in range(len(strngs)):
            strng = strngs[idx]

            # If this item is boolean, convert it to boolean
            if self._is_boolean(strng):
                strngs[idx] = self._evaluate_boolean(strng)
                continue

            # If this item is a number, conver it to a number
            if self._is_float(strng) or self._is_num(strng):
                strngs[idx] = eval(strng)
                continue

        return strngs
    
    """ Determine if the config-file is valid """
    def _validate_section_configs(self):
        for config in self.sectionConfigs:
            assert config['run_time'] or config['max_iterations'], "must specify a valid run time in secs or max number of iterations"

            if config['run_time']: assert config['run_time'] > 0, "must specify a valid run time in secs"

            if config['max_iterations']: assert config['max_iterations'] > 0, "must specify a valid number of max iterations"

            assert config['runners'] > 0, "must specify a valid number of runners"
            
            # TO-DO: Create test and section inspections and move to appropriate classes
            #assert inspect.isfunction(config['target']) or callable(config['target']), "must specify a valid target"

            if config['target_args']: assert tuple(config['target_args']),  "must specify a valid target arguments"

            assert config['test_name'],  "must specify a valid runner group name"

    def __init__(self, parser, section_name):
        # Create two tuples of all attributes and values specified in dictionary
        items = parser.items(section_name)
        labels, values = zip(*items)

        # Split comma-separated values
        values = [value.split(',') for value in values]

        # Convert strings to ints, bools, or floats when appropriate
        values = [self._evaluate_strings(value) for value in values]

        # If critical value wasn't provided, use the default value
        labels, values = self._insert_default_values(labels, values)

        # Create a list of dictionaries using Cartesian product of all sets of possible values
        self.sectionConfigs = [dict(zip(labels, value)) for value in itertools.product(*values)]

        self._validate_section_configs()

    """ Defining __iter__ allows us to iterate over _SectionConfigs object """
    def __iter__(self):
        return iter(self.sectionConfigs)

    """ Return the number of unique combinations of comma-separated values in this section """
    def __len__(self):
        return len(self.sectionConfigs)
          
class Config(dict):
    def __init__(self, config_dict):
        super(Config, self).__init__(config_dict)
        
    def globalConfigProperties(self, key):
        sectionConfig = self.values()[0]
        return sectionConfig[key]
    
""" Generator object which yields each unique combination of comma-separated parameters in config-file. By
    iterating over the Config object, a sequence of tests with different parameters can be run in sequence """
class ConfigGenerator:
    def __init__(self, filename):
        assert os.path.exists(filename), "Configuration file could not be found: %r" % filename

        # Dictionary which maps a section-name to its _SectionConfigs object
        self.sectionConfigs = {}

        # Create object for parsing config file
        parser = ConfigParser.SafeConfigParser()
        parser.read(filename)

        # Loop through each section of config file and create sectionConfigs
        for section_name in parser.sections():
            self.sectionConfigs[section_name] = _SectionConfigs(parser, section_name)

    def __iter__(self):
        # Create two tuples for all attributes and values specified in dictionary
        labels, configs = zip(*self.sectionConfigs.items())
        
        # Create a dictionary for each combination of comma-separated parameters in config file 
        for config_dict in [dict(zip(labels, sc)) for sc in itertools.product(*configs)]:
            yield Config(config_dict)

    """ Return number of unique combinations of comma-separated values in entire config-file. """ 
    def __len__(self):
        # Product of the number of combinations in each section
        return reduce(lambda x, y: x * len(y), self.sectionConfigs.values(), 1)        
