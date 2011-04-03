from models import get_state_name, get_county_name

def compute_value(d,value):
    if d is None: return None
    if isinstance(value,basestring):
        return int(d[value])
    return sum(map(int,[d[x] for x in value]))

class AggregateStatistic(object):
    """Collect a number of statistics so that a total and pct can be computed."""
    def __init__(self,label):
        self.label = label
        self.indent = 0
        self.census2010 = None
        self.census2000 = None
        self.stats = []

    def add(self,stat):
        self.stats.append(stat)
        stat.parent = self
        if stat.atomic:
            if stat.census2010:
                try: self.census2010 += stat.census2010
                except TypeError: self.census2010 = stat.census2010
            if stat.census2000:
                try: self.census2000 += stat.census2000
                except TypeError: self.census2000 = stat.census2000

    @property
    def pct2010(self):
        if self.census2010: return 100 # will we have rounding error issues?
        return None

    @property
    def pct2000(self):
        if self.census2000: return 100 # will we have rounding error issues?
        return None

    @property
    def delta(self):
        if self.census2000 and self.census2010:
            return float(self.census2010 + self.census2000) / self.census2000
        else:
            return None

    @property
    def children(self):
        for kid in self.stats:
            yield kid

    def __iter__(self):
        return iter(self.stats)

    def __unicode__(self):
        return self.label

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.label

class Statistic(object):
    """Wrap a logical statistical value for a place, offering values for multiple censuses.
       A statistic which should be included in an Aggregate Statistic for logical grouping purposes
       but not used to increment the total of that Aggregate should be have a False value for atomic.
    """
    def __init__(self, label, census2010=None, census2000=None, full_label=None, atomic=True):
        super(Statistic, self).__init__()
        self.label = label
        self.atomic = atomic

        if full_label is not None:
            self.full_label = full_label
        else:
            self.full_label =  self.label
        self.census2010 = census2010
        self.census2000 = census2000
        # children?

    def __repr__(self):
        parts = []
        if self.full_label is not None: parts.append( self.full_label )
        else: parts.append(self.label)
        parts.append('2010: %s' % self.census2010)
        parts.append('2000: %s' % self.census2010)
        parts.append('delta: %s' % self.delta)
        return "Statistic: %s [%s] [%s] [%s]" % tuple(parts)


    @property
    def pct2010(self):
        if self.census2010 is None: return None
        try:
            return float(self.census2010)/self.parent.census2010
        except:
            pass
        try:
            return self.pct2010
        except:
            return None

    @property
    def pct2000(self):
        if self.census2000 is None: return None
        try:
            return float(self.census2000)/self.parent.census2000
        except:
            pass
        try:
            return self.pct2000
        except:
            return None

    @property
    def delta(self):
        if self.census2010 and self.census2000:
            return float(self.census2010 - self.census2000)/self.census2000
        return None

    @property
    def indent(self):
        try:
            return self.parent.indent + 1
        except: return 0

class Report(object):
    """Encapsulate any number of StatsBundles (where are multiple places going?)"""
    def __init__(self, state_code=None, county_fips=None, tract_id=None):
        super(Report, self).__init__()
        self.bundles = []

        self.state_name = get_state_name(state_code)
        self.county_name = get_county_name(county_fips)
        self.tract_id = tract_id

    def add(self,bundle):
        self.bundles.append(bundle)

    def __iter__(self):
        for bundle in self.bundles:
            yield { 'label': bundle.name, 'header': True, 'help_text': bundle.help_text }
            for item in bundle:
                yield item

class StatsBundle(object):
    """docstring for StatsBundle"""
    def __init__(self, census2010=None, census2000=None, name="Unnamed Bundle"):
        super(StatsBundle, self).__init__()
        self.census2010 = census2010
        self.census2000 = census2000
        self.name = name

class StatisticFactory(object):
    def __init__(self, label, full_label=None,atomic=True):
        self.label = label
        self.full_label = full_label
        self.atomic = atomic
    
class ssf(StatisticFactory):
    """ssf == SimpleStatisticFactory. When called with dicts for census years and produces Statistic objects which simply fish out a dict value."""
    def __init__(self, label, column,full_label=None,atomic=True):
        super(ssf, self).__init__(label, full_label=None,atomic=True)
        self.column = column
        
    def __call__(self,census2010=None,census2000=None):
        if census2010:
            census2010 = int(census2010[self.column])
        if census2000:
            census2000 = int(census2000[self.column])
        return Statistic(self.label, census2010=census2010, census2000=census2000, full_label=self.full_label, atomic=self.atomic)

class sumsf(StatisticFactory):
    def __init__(self, label, columns, full_label=None,atomic=True):
        super(sumsf, self).__init__(label, full_label=None,atomic=True)
        self.columns = columns

    def __call__(self,census2010=None,census2000=None):
        if census2010:
            census2010 = sum(map(int,[census2010[x] for x in self.columns]))
        if census2000:
            census2000 = sum(map(int,[census2000[x] for x in self.columns]))
        return Statistic(self.label, census2010=census2010, census2000=census2000, full_label=self.full_label, atomic=self.atomic)
        
class AgeSex(StatsBundle):
    """Wrapper for a bundle of place statistics that exposes the age/sex stats.
        TODO: Will we pass in multiple args for different comparison years?
    """
    
    help_text = """
At invenire oportere erroribus mea. Pri ne odio patrioque adolescens, his
ex esse aeterno takimata. Cum at eros conclusionemque, sea et novum nobis.
Ne sea liber nostrum lobortis, odio nisl omittam ex nam. Zzril placerat
nec id, mutat omnes utamur ut sed.

Nonumy regione pri no. Has ad moderatius philosophia. Ius quod signiferumque
ne. Modo quaestio reprehendunt at eum. Fabulas alienum percipit an eum,
id quo facilisi conclusionemque, sit amet soluta at. Usu ullum ancillae
dissentiet te, cu cum equidem gloriatur, prima facilisi delicata no est.
        """
    
    stat_factories = { # for Age/Sex the column headers are the same for 2010 and 2000 census.
        'male': (
            # ('Age Total','p012002'),
            ssf('Age Under 5 years','p012003'),
            ssf('Age 5 to 9 years','p012004'),
            ssf('Age 10 to 14 years','p012005'),
            # ('Age 15 to 17 years','p012006'),
            # ('Age 18 and 19 years','p012007'),
            sumsf('Age 15 to 19 years',['p012006','p012007']),
            # ('Age 20 years','p012008'),
            # ('Age 21 years','p012009'),
            # ('Age 22 to 24 years','p012010'),
            sumsf('Age 20 to 24 years',['p012008','p012009','p012010']),
            ssf('Age 25 to 29 years','p012011'),
            ssf('Age 30 to 34 years','p012012'),
            ssf('Age 35 to 39 years','p012013'),
            ssf('Age 40 to 44 years','p012014'),
            ssf('Age 45 to 49 years','p012015'),
            ssf('Age 50 to 54 years','p012016'),
            ssf('Age 55 to 59 years','p012017'),
            # ('Age 60 and 61 years','p012018'),
            # ('Age 62 to 64 years','p012019'),
            sumsf('Age 60 to 64 years',['p012018','p012019']),
            # ('Age 65 and 66 years','p012020'),
            # ('Age 67 to 69 years','p012021'),
            sumsf('Age 65 to 69 years',['p012020','p012021']),
            ssf('Age 70 to 74 years','p012022'),
            ssf('Age 75 to 79 years','p012023'),
            ssf('Age 80 to 84 years','p012024'),
            ssf('Age 85 years and over','p012025'),

            # ('Age 18 years and over',
            #     ['P012007', 'P012008', 'P012009', 'P012010', 'P012011', 'P012012', 'P012013', 'P012014', 'P012015', 'P012016', 'P012017', 'P012018', 'P012019', 'P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025'], False),
            # ('Age 21 years and over', ['P012009', 'P012010', 'P012011', 'P012012', 'P012013', 'P012014', 'P012015', 'P012016', 'P012017', 'P012018', 'P012019', 'P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025'], False),
            # ('Age 62 years and over', ['P012019', 'P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025'], False)
            # ('Age 65 years and over', ['P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025'], False)
        ),
        'female': (
            # ('Age Total','p012026'),
            ssf('Age Under 5 years','p012027'),
            ssf('Age 5 to 9 years','p012028'),
            ssf('Age 10 to 14 years','p012029'),
            # ('Age 15 to 17 years','p012030'),
            # ('Age 18 and 19 years','p012031'),
            sumsf('Age 15 to 19 years',['p012030','p012031']),
            # ('Age 20 years','p012032'),
            # ('Age 21 years','p012033'),
            # ('Age 22 to 24 years','p012034'),
            sumsf('Age 20 to 24 years',['p012032','p012033','p012034']),
            ssf('Age 25 to 29 years','p012035'),
            ssf('Age 30 to 34 years','p012036'),
            ssf('Age 35 to 39 years','p012037'),
            ssf('Age 40 to 44 years','p012038'),
            ssf('Age 45 to 49 years','p012039'),
            ssf('Age 50 to 54 years','p012040'),
            ssf('Age 55 to 59 years','p012041'),
            # ('Age 60 and 61 years','p012042'),
            # ('Age 62 to 64 years','p012043'),
            sumsf('Age 60 to 64 years',['p012042','p012043']),
            # ('Age 65 and 66 years','p012044'),
            # ('Age 67 to 69 years','p012045'),
            sumsf('Age 65 to 69 years',['p012044','p012045']),
            ssf('Age 70 to 74 years','p012046'),
            ssf('Age 75 to 79 years','p012047'),
            ssf('Age 80 to 84 years','p012048'),
            ssf('Age 85 years and over','p012049'),

            # ('Age 18 years and over',
            #     ['P012031', 'P012032', 'P012033', 'P012034', 'P012035', 'P012036', 'P012037', 'P012038', 'P012039', 'P012040', 'P012041', 'P012042', 'P012043', 'P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049'], False),
            # ('Age 21 years and over', ['P012033', 'P012034', 'P012035', 'P012036', 'P012037', 'P012038', 'P012039', 'P012040', 'P012041', 'P012042', 'P012043', 'P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049'], False),
            # ('Age 62 years and over', ['P012043', 'P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049'], False)
            # ('Age 65 years and over', ['P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049'], False)
        )
        'total': (
            sumsf('Total', ['P012002', 'P012026']),
            sumsf('Under 5 years', ['P012003', 'P012027']),
            sumsf('5 to 9 years', ['P012004', 'P012028']),
            sumsf('10 to 14 years', ['P012005', 'P012029']),
            sumsf('15 to 17 years', ['P012006', 'P012030']),
            sumsf('15 to 19 years', ['P012006', 'P012007', 'P012030', 'P012031']),
            sumsf('18 and 19 years', ['P012007', 'P012031']),
            sumsf('20 to 24 years', ['P012008', 'P012009', 'P012010', 'P012032', 'P012033', 'P012034']),
            sumsf('20 years', ['P012008', 'P012032']),
            sumsf('21 years', ['P012009', 'P012033']),
            sumsf('22 to 24 years', ['P012010', 'P012034']),
            sumsf('25 to 29 years', ['P012011', 'P012035']),
            sumsf('30 to 34 years', ['P012012', 'P012036']),
            sumsf('35 to 39 years', ['P012013', 'P012037']),
            sumsf('40 to 44 years', ['P012014', 'P012038']),
            sumsf('45 to 49 years', ['P012015', 'P012039']),
            sumsf('50 to 54 years', ['P012016', 'P012040']),
            sumsf('55 to 59 years', ['P012017', 'P012041']),
            sumsf('60 and 61 years', ['P012018', 'P012042']),
            sumsf('60 to 64 years', ['P012018', 'P012019', 'P012042', 'P012043']),
            sumsf('62 to 64 years', ['P012019', 'P012043']),
            sumsf('62 years and over', ['P012019', 'P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025', 'P012043', 'P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049'],  '65 and 66 years', ['P012020', 'P012044']),
            sumsf('65 to 69 years', ['P012020', 'P012021', 'P012044', 'P012045']),
            sumsf('65 years and over', ['P012020', 'P012021', 'P012022', 'P012023', 'P012024', 'P012025', 'P012044', 'P012045', 'P012046', 'P012047', 'P012048', 'P012049']),
            sumsf('67 to 69 years', ['P012021', 'P012045']),
            sumsf('70 to 74 years', ['P012022', 'P012046']),
            sumsf('75 to 79 years', ['P012023', 'P012047']),
            sumsf('80 to 84 years', ['P012024', 'P012048']),
            sumsf('85 years and over', ['P012025', 'P012049']),
        )

    }

    def __init__(self, census2010=None,census2000=None):
        super(AgeSex, self).__init__(census2010=census2010,census2000=census2000,name="Sex and Age")

        self.male_population = AggregateStatistic("Male population")
        for factory in self.stat_factories['male']:
            self.male_population.add(factory(census2010=self.census2010,census2000=self.census2000))

            self.female_population = AggregateStatistic("Female population")
            for factory in self.stat_factories['female']:
                self.female_population.add(factory(census2010=self.census2010,census2000=self.census2000))

            self.total_population = AggregateStatistic("Total population")
            for factory in self.stat_factories['total']:
                self.total_population.add(factory(census2010=self.census2010,census2000=self.census2000))

    def __repr__(self):
        return self.name

    def __iter__(self):
        # yield self.total_population
        # for child in self.total_population:
        #     yield child

        yield self.male_population
        for child in self.male_population:
            yield child

        yield self.female_population
        for child in self.female_population:
            yield child

class Race(StatsBundle):
    """docstring for Race"""
    def __init__(self, arg):
        super(Race, self).__init__()
        self.arg = arg
