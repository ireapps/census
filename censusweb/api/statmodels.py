class AggregateStatistic(object):
    """Collect a number of statistics so that a total and pct can be computed."""
    def __init__(self,label):
        self.label = label
        self.census2010 = 0
        self.census2000 = 0
        self.delta = None
        self.stats = []

    def add(self,stat):
        self.stats.append(stat)
        self.census2010 += stat.census2010
        self.census2000 += stat.census2000
        stat.parent = self
        if self.census2000 != 0:
            self.delta = float(self.census2010 + self.census2000) / self.census2000
        else:
            self.delta = None

    @property
    def children(self):
        for kid in self.stats:
            yield kid

class Statistic(object):
    """Wrap a logical statistical value for a place, offering values for multiple censuses"""
    def __init__(self, label, census2010, census2000, full_label=None):
        super(Statistic, self).__init__()
        self.label = label
        if full_label is not None:
            self.full_label = full_label
        else:
            self.full_label =  self.label
        self.census2010 = census2010
        self.census2000 = census2000
        if census2010 is not None and census2000 is not None:
            self.delta = float(census2010 + census2000) / census2000
        # children?

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



class StatsBundle(object):
    """docstring for StatsBundle"""
    def __init__(self, stats, name="Unnamed Bundle"):
        super(AgeSex, self).__init__()
        self.stats = stats
        self.name = name

class AgeSex(StatsBundle):
    """Wrapper for a bundle of place statistics that exposes the age/sex stats.
        TODO: Will we pass in multiple args for different comparison years?
    """
    labels_and_keys = {
        'male': (
            # ('Age Total','P012002'),
            ('Age Under 5 years','P012003'),
            ('Age 5 to 9 years','P012004'),
            ('Age 10 to 14 years','P012005'),
            # ('Age 15 to 17 years','P012006'),
            # ('Age 18 and 19 years','P012007'),
            ('Age 15 to 19 years',['P012006','P012007']),
            # ('Age 20 years','P012008'),
            # ('Age 21 years','P012009'),
            # ('Age 22 to 24 years','P012010'),
            ('Age 20 to 24 years',['P012008','P012009','P012010']),
            ('Age 25 to 29 years','P012011'),
            ('Age 30 to 34 years','P012012'),
            ('Age 35 to 39 years','P012013'),
            ('Age 40 to 44 years','P012014'),
            ('Age 45 to 49 years','P012015'),
            ('Age 50 to 54 years','P012016'),
            ('Age 55 to 59 years','P012017'),
            ('Age 60 and 61 years','P012018'),
            ('Age 62 to 64 years','P012019'),
            ('Age 65 and 66 years','P012020'),
            ('Age 67 to 69 years','P012021'),
            ('Age 70 to 74 years','P012022'),
            ('Age 75 to 79 years','P012023'),
            ('Age 80 to 84 years','P012024'),
            ('Age 85 years and over','P012025'),
        ),
        'female': (
            # ('Age Total','P012026'),
            ('Age Under 5 years','P012027'),
            ('Age 5 to 9 years','P012028'),
            ('Age 10 to 14 years','P012029'),
            # ('Age 15 to 17 years','P012030'),
            # ('Age 18 and 19 years','P012031'),
            ('Age 15 to 19 years',['P012030','P012031']),
            # ('Age 20 years','P012032'),
            # ('Age 21 years','P012033'),
            # ('Age 22 to 24 years','P012034'),
            ('Age 20 to 24 years',['P012032','P012033','P012034']),
            ('Age 25 to 29 years','P012035'),
            ('Age 30 to 34 years','P012036'),
            ('Age 35 to 39 years','P012037'),
            ('Age 40 to 44 years','P012038'),
            ('Age 45 to 49 years','P012039'),
            ('Age 50 to 54 years','P012040'),
            ('Age 55 to 59 years','P012041'),
            ('Age 60 and 61 years','P012042'),
            ('Age 62 to 64 years','P012043'),
            ('Age 65 and 66 years','P012044'),
            ('Age 67 to 69 years','P012045'),
            ('Age 70 to 74 years','P012046'),
            ('Age 75 to 79 years','P012047'),
            ('Age 80 to 84 years','P012048'),
            ('Age 85 years and over','P012049'),
        )
    }
    
    
    
    def __init__(self, stats):
        super(AgeSex, self).__init__(stats,name="Sex and Age")
        self.male_population = AggregateStatistic("Male population")
        for label, value in self.labels_and_keys['male']:
            stat = Statistic(label, compute_value(self.stats,value),None,full_label="Male %s" % label)
            self.male_population.add(stat)

        self.female_population = AggregateStatistic("Female population")
        for label, value in self.labels_and_keys['female']:
            stat = Statistic(label, compute_value(self.stats,value),None,full_label="Female %s" % label)
            self.female_population.add(stat)

        self.total_population = AggregateStatistic("Total population")
        female_lookup = dict(self.labels_and_keys['female'])
        for label, value in self.labels_and_keys['male']:
            fvalue = female_lookup[label]
            stat = Statistic(label, compute_value(self.stats,value) + compute_value(self.stats,fvalue),None,full_label="Total %s" % label)
            self.total_population.add(stat)

            