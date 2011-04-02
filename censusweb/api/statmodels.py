def compute_value(d,value):
    if d is None: return None
    if isinstance(value,basestring):
        return int(d[value])
    return sum(map(int,[d[x] for x in value]))
        
class AggregateStatistic(object):
    """Collect a number of statistics so that a total and pct can be computed."""
    def __init__(self,label):
        self.label = label
        self.census2010 = None
        self.census2000 = None
        self.delta = None
        self.stats = []

    def add(self,stat):
        self.stats.append(stat)
        if stat.census2010: 
            try: self.census2010 += stat.census2010
            except TypeError: self.census2010 = stat.census2010
        if stat.census2000: 
            try: self.census2000 += stat.census2000
            except TypeError: self.census2000 = stat.census2000
        stat.parent = self
        if self.census2000 and self.census2010:
            self.delta = float(self.census2010 + self.census2000) / self.census2000
        else:
            self.delta = None

    @property
    def pct2010(self):
        if self.census2010: return 100 # will we have rounding error issues?
        return None

    @property
    def pct2000(self):
        if self.census2000: return 100 # will we have rounding error issues?
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
    """Wrap a logical statistical value for a place, offering values for multiple censuses"""
    def __init__(self, label, census2010=None, census2000=None, full_label=None):
        super(Statistic, self).__init__()
        self.label = label
        self.delta = None
        if full_label is not None:
            self.full_label = full_label
        else:
            self.full_label =  self.label
        self.census2010 = census2010
        self.census2000 = census2000
        if census2010 is not None and census2000 is not None:
            self.delta = float(census2010 + census2000) / census2000
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

class Report(object):
    """Encapsulate any number of StatsBundles (where are multiple places going?)"""
    def __init__(self):
        super(Report, self).__init__()
        self.bundles = []
    
    def add(self,bundle):
        self.bundles.append(bundle)
        
    def __iter__(self):
        for bundle in self.bundles:
            yield { 'label': bundle.name, 'header': True }
            for item in bundle:
                yield item

class StatsBundle(object):
    """docstring for StatsBundle"""
    def __init__(self, census2010=None, census2000=None, name="Unnamed Bundle"):
        super(StatsBundle, self).__init__()
        self.census2010 = census2010
        self.census2000 = census2000
        self.name = name

        
class AgeSex(StatsBundle):
    """Wrapper for a bundle of place statistics that exposes the age/sex stats.
        TODO: Will we pass in multiple args for different comparison years?
    """
    labels_and_keys = { # for Age/Sex the column headers are the same for 2010 and 2000 census.
        'male': (
            # ('Age Total','p012002'),
            ('Age Under 5 years','p012003'),
            ('Age 5 to 9 years','p012004'),
            ('Age 10 to 14 years','p012005'),
            # ('Age 15 to 17 years','p012006'),
            # ('Age 18 and 19 years','p012007'),
            ('Age 15 to 19 years',['p012006','p012007']),
            # ('Age 20 years','p012008'),
            # ('Age 21 years','p012009'),
            # ('Age 22 to 24 years','p012010'),
            ('Age 20 to 24 years',['p012008','p012009','p012010']),
            ('Age 25 to 29 years','p012011'),
            ('Age 30 to 34 years','p012012'),
            ('Age 35 to 39 years','p012013'),
            ('Age 40 to 44 years','p012014'),
            ('Age 45 to 49 years','p012015'),
            ('Age 50 to 54 years','p012016'),
            ('Age 55 to 59 years','p012017'),
            ('Age 60 and 61 years','p012018'),
            ('Age 62 to 64 years','p012019'),
            ('Age 65 and 66 years','p012020'),
            ('Age 67 to 69 years','p012021'),
            ('Age 70 to 74 years','p012022'),
            ('Age 75 to 79 years','p012023'),
            ('Age 80 to 84 years','p012024'),
            ('Age 85 years and over','p012025'),
        ),
        'female': (
            # ('Age Total','p012026'),
            ('Age Under 5 years','p012027'),
            ('Age 5 to 9 years','p012028'),
            ('Age 10 to 14 years','p012029'),
            # ('Age 15 to 17 years','p012030'),
            # ('Age 18 and 19 years','p012031'),
            ('Age 15 to 19 years',['p012030','p012031']),
            # ('Age 20 years','p012032'),
            # ('Age 21 years','p012033'),
            # ('Age 22 to 24 years','p012034'),
            ('Age 20 to 24 years',['p012032','p012033','p012034']),
            ('Age 25 to 29 years','p012035'),
            ('Age 30 to 34 years','p012036'),
            ('Age 35 to 39 years','p012037'),
            ('Age 40 to 44 years','p012038'),
            ('Age 45 to 49 years','p012039'),
            ('Age 50 to 54 years','p012040'),
            ('Age 55 to 59 years','p012041'),
            ('Age 60 and 61 years','p012042'),
            ('Age 62 to 64 years','p012043'),
            ('Age 65 and 66 years','p012044'),
            ('Age 67 to 69 years','p012045'),
            ('Age 70 to 74 years','p012046'),
            ('Age 75 to 79 years','p012047'),
            ('Age 80 to 84 years','p012048'),
            ('Age 85 years and over','p012049'),
        )
    }
    
    
    
    def __init__(self, census2010=None,census2000=None):
        super(AgeSex, self).__init__(census2010=census2010,census2000=census2000,name="Sex and Age")

        self.male_population = AggregateStatistic("Male population")
        for label, value in self.labels_and_keys['male']:
            stat = Statistic(label, 
                             census2010=compute_value(self.census2010,value), 
                             census2000=compute_value(self.census2000,value), 
                             full_label="Male %s" % label)
            self.male_population.add(stat)

        self.female_population = AggregateStatistic("Female population")
        for label, value in self.labels_and_keys['female']:
            stat = Statistic(label, 
                             census2010=compute_value(self.census2010,value), 
                             census2000=compute_value(self.census2000,value),
                             full_label="Female %s" % label)
            self.female_population.add(stat)

        self.total_population = AggregateStatistic("Total population")
        female_lookup = dict(self.labels_and_keys['female'])
        for label, value in self.labels_and_keys['male']:
            fvalue = female_lookup[label]
            tot2010 = tot2000 = None
            try: tot2010 = compute_value(self.census2010,value) + compute_value(self.census2010,fvalue)
            except TypeError: pass
            try: tot2000 = compute_value(self.census2000,value) + compute_value(self.census2000,fvalue)
            except TypeError: pass

            stat = Statistic(label, 
                             census2010=tot2010,
                             census2000=tot2000,
                             full_label="Total %s" % label)
            self.total_population.add(stat)

    def __repr__(self):
        return self.name    
        
    def __iter__(self):
        yield self.total_population
        for child in self.total_population:
            yield child

        yield self.male_population
        for child in self.male_population:
            yield child

        yield self.female_population
        for child in self.female_population:
            yield child

