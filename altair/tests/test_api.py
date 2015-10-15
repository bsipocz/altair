import numpy as np
import pandas as pd
import numpy as np
import pandas as pd
from traitlets import TraitError

from altair import api

from .. import api, spec


VALID_MARKTYPES = spec.SPEC['properties']['marktype']['enum']

def build_simple_spec():
    data = dict(x=[1, 2, 3],
                y=[4, 5, 6])
    return api.Viz(data), data


def test_empty_data():
    d = api.Data()
    assert d.formatType=='json'
    assert 'formatType' in d
    assert 'url' not in d
    assert 'values' not in d


def test_dict_data():
    spec, data = build_simple_spec()
    assert np.all(spec.data == pd.DataFrame(data))


def test_dataframe_data():
    spec, data = build_simple_spec()
    data = data = pd.DataFrame(data)
    spec = api.Viz(data)
    assert np.all(spec.data == data)


def test_to_dict():
    data = pd.DataFrame({'x': [1, 2, 3],
                         'y': [4, 5, 6]})
    spec = api.Viz(data).encode(x='x', y='y')

    D = spec.to_dict()

    assert D == {'config': {'gridColor': 'black',
                            'gridOpacity': 0.08,
                            'height': 400,
                            'width': 600},
                 'data': {'formatType': 'json',
                          'values': [{'x': 1, 'y': 4},
                                     {'x': 2, 'y': 5},
                                     {'x': 3, 'y': 6}]},
                 'encoding': {'x': {'bin': False, 'name': 'x', 'type': 'Q'},
                              'y': {'bin': False, 'name': 'y', 'type': 'Q'}},
                 'marktype': 'point'}


def test_vl_spec_for_scale_defaults():
    """Check that defaults are according to spec"""

    # This scale object is the property used for X, Y, Size
    scale = api.Scale()
    assert scale.type == 'linear'
    assert scale.reverse == False
    assert scale.zero == True
    assert scale.nice is None
    assert scale.useRawDomain is None

    # Scale object for property in Color
    scale = api.ColorScale()
    assert scale.type == 'linear'
    assert scale.reverse == False
    assert scale.zero == True
    assert scale.nice is None
    assert scale.useRawDomain is None
    assert scale.range is None
    assert scale.c10palette == 'category10'
    assert scale.c20palette == 'category20'
    assert scale.ordinalPalette == 'BuGn'


def test_vl_spec_for_scale_changes():
    """Check that changes are possible and sticky"""

    # This scale object is the property used for X, Y, Size
    scale = api.Scale(type='log', reverse=True, zero=False, nice='second', useRawDomain=True)
    assert scale.type == 'log'
    assert scale.reverse == True
    assert scale.zero == False
    assert scale.nice == 'second'
    assert scale.useRawDomain == True

    scale.type = 'linear'
    scale.reverse = False
    scale.zero = True
    scale.nice = None
    scale.useRawDomain = None
    assert scale.type == 'linear'
    assert scale.reverse == False
    assert scale.zero == True
    assert scale.nice is None
    assert scale.useRawDomain is None

    # Scale object for property in Color
    scale = api.ColorScale(type='log', reverse=True, zero=False, nice='second', useRawDomain=True,
                           range='category10', c10palette='Set1', c20palette='category20c', ordinalPalette='Spectral')
    assert scale.type == 'log'
    assert scale.reverse == True
    assert scale.zero == False
    assert scale.nice == 'second'
    assert scale.useRawDomain == True
    assert scale.range == 'category10'
    assert scale.c10palette == 'Set1'
    assert scale.c20palette == 'category20c'
    assert scale.ordinalPalette == 'Spectral'

    scale.range = ['category10']
    scale.c10palette = 'Set3'
    scale.c20palette = 'category20b'
    scale.ordinalPalette = 'Dark2'
    assert scale.range == ['category10']
    assert scale.c10palette == 'Set3'
    assert scale.c20palette == 'category20b'
    assert scale.ordinalPalette == 'Dark2'


def test_vl_spec_for_band_defaults():
    """Check that defaults are according to spec"""

    band = api.Band()
    assert band.size == 600
    assert band.padding == 1


def test_vl_spec_for_band_changes():
    """Check that changes are possible and sticky"""

    band = api.Band(size=300, padding=15)
    assert band.size == 300
    assert band.padding == 15


def test_vl_spec_for_band_edge_values():
    """Check edge values"""

    band = api.Band()

    try:
        band.size = -1
        raise Exception('Should have thrown for illegal size min value.')
    except TraitError:
        pass

    try:
        band.padding = -1
        raise Exception('Should have thrown for illegal padding min value.')
    except TraitError:
        pass


def test_markers():
    spec, data = build_simple_spec()

    # call, e.g. spec.mark('point')
    for marktype in VALID_MARKTYPES:
        spec.mark(marktype)
        assert spec.marktype == marktype

    # call, e.g. spec.point()
    for marktype in VALID_MARKTYPES:
        method = marktype
        getattr(spec, method)()
        assert spec.marktype == marktype


def test_vl_spec_for_x_y__defaults():
    """Check that defaults are according to spec"""

    for x in [api.X('foobar'), api.Y('foobar')]:
        assert x.name == 'foobar'
        assert x.type is None       # TODO: None?! Spec says type is required
        assert x.aggregate is None
        assert x.timeUnit is None
        assert x.bin == False
        assert x.scale is None
        assert x.axis is None
        assert x.band is None
        assert x.sort == []

    for x in [api.X('foobar:O'), api.Y('foobar:O')]:
        assert x.name == 'foobar'
        assert x.type == 'O'
        assert x.aggregate is None
        assert x.timeUnit is None
        assert x.bin == False
        assert x.scale is None
        assert x.axis is None
        assert x.band is None
        assert x.sort == []

    for x in [api.X('sum(foobar):Q'), api.Y('sum(foobar):Q')]:
        assert x.name == 'foobar'
        assert x.type == 'Q'
        assert x.aggregate == 'sum'
        assert x.timeUnit is None
        assert x.bin == False
        assert x.scale is None
        assert x.axis is None
        assert x.band is None
        assert x.sort == []


def test_vl_spec_for_x_y_changes():
    """Check that changes are possible and sticky"""
    for x in [api.X('foobar:O', type='N', aggregate='median', timeUnit='seconds', bin=api.Bin(), scale = api.Scale(),
                    axis=api.Axis(), band=api.Band(), sort=[api.SortItems()]),
              api.Y('foobar:O', type='N', aggregate='median', timeUnit='seconds', bin=api.Bin(), scale = api.Scale(),
                    axis=api.Axis(), band=api.Band(), sort=[api.SortItems()])]:
        assert x.name == 'foobar'
        assert x.type == 'N'
        assert x.aggregate == 'median'
        assert x.timeUnit == 'seconds'
        assert x.bin.to_dict() == api.Bin().to_dict()
        assert x.scale.to_dict() == api.Scale().to_dict()
        assert x.axis.to_dict() == api.Axis().to_dict()
        assert x.band.to_dict() == api.Band().to_dict()
        assert x.sort[0].to_dict() == api.SortItems().to_dict()

        x.shorthand = 'sum(foobar):Q'
        assert x.name == 'foobar'
        assert x.type == 'Q'
        assert x.aggregate == 'sum'
        assert x.timeUnit == 'seconds'
        assert x.bin.to_dict() == api.Bin().to_dict()
        assert x.scale.to_dict() == api.Scale().to_dict()
        assert x.axis.to_dict() == api.Axis().to_dict()
        assert x.band.to_dict() == api.Band().to_dict()
        assert x.sort[0].to_dict() == api.SortItems().to_dict()


def test_vl_spec_for_size__defaults():
    """Check that defaults are according to spec"""
    size = api.Size('foobar')
    assert size.name == 'foobar'
    assert size.type is None
    assert size.aggregate is None
    assert size.timeUnit is None
    assert size.bin == False
    assert size.scale is None
    assert size.legend == True
    assert size.value == 30
    assert size.sort == []

    size = api.Size('foobar:O')
    assert size.name == 'foobar'
    assert size.type == 'O'
    assert size.aggregate is None
    assert size.timeUnit is None
    assert size.bin == False
    assert size.scale is None
    assert size.legend == True
    assert size.value == 30
    assert size.sort == []

    size = api.Size('sum(foobar):Q')
    assert size.name == 'foobar'
    assert size.type == 'Q'
    assert size.aggregate == 'sum'
    assert size.timeUnit is None
    assert size.bin == False
    assert size.scale is None
    assert size.legend == True
    assert size.value == 30
    assert size.sort == []


def test_vl_spec_for_size_changes():
    """Check that changes are possible and sticky"""
    size = api.Size('foobar', type='Q', aggregate='sum', timeUnit='minutes', bin=api.Bin(), scale=api.Scale(),
                    legend=False, value=0, sort=[api.SortItems()])
    assert size.name == 'foobar'
    assert size.type == 'Q'
    assert size.aggregate == 'sum'
    assert size.timeUnit == 'minutes'
    assert size.bin.to_dict() == api.Bin().to_dict()
    assert size.scale.to_dict() == api.Scale().to_dict()
    assert size.legend == False
    assert size.value == 0
    assert size.sort[0].to_dict() == api.SortItems().to_dict()

    size.shorthand = 'avg(foobar):O'
    assert size.name == 'foobar'
    assert size.type == 'O'
    assert size.aggregate == 'avg'
    assert size.timeUnit == 'minutes'
    assert size.bin.to_dict() == api.Bin().to_dict()
    assert size.scale.to_dict() == api.Scale().to_dict()
    assert size.legend == False
    assert size.value == 0
    assert size.sort[0].to_dict() == api.SortItems().to_dict()


def test_vl_spec_for_color__defaults():
    """Check that defaults are according to spec"""
    color = api.Color('foobar')
    assert color.name == 'foobar'
    assert color.type is None
    assert color.aggregate is None
    assert color.timeUnit is None
    assert color.bin == False
    assert color.scale is None
    assert color.legend == True
    assert color.value == '#4682b4'
    assert color.opacity == 1.0

    color = api.Color('foobar:O')
    assert color.name == 'foobar'
    assert color.type == 'O'
    assert color.aggregate is None
    assert color.timeUnit is None
    assert color.bin == False
    assert color.scale is None
    assert color.legend == True
    assert color.value == '#4682b4'
    assert color.opacity == 1.0

    color = api.Color('sum(foobar):Q')
    assert color.name == 'foobar'
    assert color.type == 'Q'
    assert color.aggregate == 'sum'
    assert color.timeUnit is None
    assert color.bin == False
    assert color.scale is None
    assert color.legend == True
    assert color.value == '#4682b4'
    assert color.opacity == 1.0


def test_vl_spec_for_color_changes():
    """Check that changes are possible and sticky"""
    color = api.Color('foobar', type='O', aggregate='avg', timeUnit='minutes', bin=api.Bin(), scale=api.ColorScale(),
                      legend=False, value='Dark2', opacity=0.5)
    assert color.name == 'foobar'
    assert color.type == 'O'
    assert color.aggregate == 'avg'
    assert color.timeUnit == 'minutes'
    assert color.bin.to_dict() == api.Bin().to_dict()
    assert color.scale.to_dict() == api.ColorScale().to_dict()
    assert color.legend == False
    assert color.value == 'Dark2'
    assert color.opacity == 0.5

    color.shorthand = 'sum(foobar):Q'
    assert color.name == 'foobar'
    assert color.type == 'Q'
    assert color.aggregate == 'sum'
    assert color.timeUnit == 'minutes'
    assert color.bin.to_dict() == api.Bin().to_dict()
    assert color.scale.to_dict() == api.ColorScale().to_dict()
    assert color.legend == False
    assert color.value == 'Dark2'
    assert color.opacity == 0.5


def test_encode():
    data = dict(col1=[1.0, 2.0, 3.0],
                col2=[0.1, 0.2, 0.3],
                col3=['A', 'B', 'C'],
                col4=[True, False, True],
                col5=[0.1, 0.2, 0.3],
                col6=pd.date_range('2012', periods=3, freq='A'),
                col7=np.arange(3))
    kwargs = dict(x='col1', y='col2', row='col3', col='col4',
                  size='col5', color='col6', shape='col7')

    spec = api.Viz(data).encode(**kwargs)
    for key, name in kwargs.items():
        assert getattr(spec.encoding, key).name == name


def test_encode_aggregates():
    data = dict(col1=[1.0, 2.0, 3.0],
                col2=[0.1, 0.2, 0.3],
                col3=['A', 'B', 'C'],
                col4=[True, False, True],
                col5=[0.1, 0.2, 0.3],
                col6=pd.date_range('2012', periods=3, freq='A'),
                col7=np.arange(3))
    kwargs = dict(x=('count', 'col1'), y=('count', 'col2'),
                  row=('count', 'col3'), col=('count', 'col4'),
                  size=('avg', 'col5'), color=('max', 'col6'),
                  shape=('count', 'col7'))

    spec = api.Viz(data).encode(**{key:"{0}({1})".format(*val)
                                   for key, val in kwargs.items()})
    for key, val in kwargs.items():
        agg, name = val
        assert getattr(spec.encoding, key).name == name
        assert getattr(spec.encoding, key).aggregate == agg


def test_encode_types():
    data = dict(col1=[1.0, 2.0, 3.0],
                col2=[0.1, 0.2, 0.3],
                col3=['A', 'B', 'C'],
                col4=[True, False, True],
                col5=[0.1, 0.2, 0.3],
                col6=pd.date_range('2012', periods=3, freq='A'),
                col7=np.arange(3))
    kwargs = dict(x=('col1', 'Q'), y=('col2', 'Q'),
                  row=('col3', 'O'), col=('col4', 'N'),
                  size=('col5', 'Q'), color=('col6', 'T'),
                  shape=('col7', 'O'))

    spec = api.Viz(data).encode(**{key:"{0}:{1}".format(*val)
                                   for key, val in kwargs.items()})
    for key, val in kwargs.items():
        name, typ = val
        assert getattr(spec.encoding, key).name == name
        assert getattr(spec.encoding, key).type == typ

def test_infer_types():
    data = dict(col1=[1.0, 2.0, 3.0],
                col2=[0.1, 0.2, 0.3],
                col3=['A', 'B', 'C'],
                col4=[True, False, True],
                col5=[0.1, 0.2, 0.3],
                col6=pd.date_range('2012', periods=3, freq='A'),
                col7=np.arange(3))
    kwargs = dict(x=('col1', 'Q'), y=('col2', 'Q'),
                  row=('col3', 'N'), col=('col4', 'N'),
                  size=('col5', 'Q'), color=('col6', 'T'),
                  shape=('col7', 'Q'))

    spec = api.Viz(data).encode(**{key: val[0]
                                   for key, val in kwargs.items()})
    for key, val in kwargs.items():
        name, typ = val
        assert getattr(spec.encoding, key).name == name
        assert getattr(spec.encoding, key).type == typ


def test_configure():
  spec, data = build_simple_spec()
  spec.configure(height=100, width=200)
  res = spec.to_dict()
  assert res['config']['height'] == 100
  assert res['config']['width'] == 200


def test_single_dim_setting():
    spec, data = build_simple_spec()
    spec.encode(x="x:N", y="y:Q").set_single_dims(100, 100)
    res = spec.to_dict()

    assert res['config']['width'] == 100
    assert res['config']['height'] == 100
    assert res['config']['singleWidth'] == 75
    assert res['config']['singleHeight'] == 75

    assert res['encoding']['x']['band']['size'] == 10
    assert res['encoding']['y'].get('band') is None


def test_hist():
    data = dict(x=[1, 2, 3],
                y=[4, 5, 6])

    viz1 = api.Viz(data).hist(x='x')
    assert viz1.encoding.x.name == "x"
    assert viz1.encoding.x.bin.maxbins == 10
    assert viz1.encoding.y.name == "x"
    assert viz1.encoding.y.type == "Q"
    assert viz1.encoding.y.aggregate == "count"

    viz2 = api.Viz(data).hist(x="x", bins=30)
    assert viz2.encoding.x.bin.maxbins == 30
    expected = {'config': {'gridColor': 'black',
                           'gridOpacity': 0.08,
                           'height': 400,
                           'width': 600},
                'data': {'formatType': 'json',
                         'values': [{'x': 1, 'y': 4},
                                    {'x': 2, 'y': 5},
                                    {'x': 3, 'y': 6}]},
                'encoding': {'x': {'bin': {'maxbins': 30},
                                   'name': 'x',
                                   'type': 'Q'},
                             'y': {'aggregate': 'count',
                                   'bin': False,
                                   'name': 'x',
                                   'type': 'Q'}},
                 'marktype': 'bar'}

    assert viz2.to_dict() == expected

    viz3 = api.Viz(data).hist(x="x:O",
        color=api.Color(shorthand="bar", type="N")
    )
    assert viz3.encoding.x.name == "x"
    assert viz3.encoding.x.type == "O"

    expected = {'config': {'gridColor': 'black',
                           'gridOpacity': 0.08,
                           'height': 400,
                           'width': 600},
                'data': {'formatType': 'json',
                'values': [{'x': 1, 'y': 4}, {'x': 2, 'y': 5},
                           {'x': 3, 'y': 6}]},
                'encoding': {'x': {'bin': {'maxbins': 10},
                                   'name': 'x', 'type': 'O'},
                             'y': {'aggregate': 'count',
                                   'bin': False,
                                   'name': 'x',
                                   'type': 'Q'},
                             'color': {'bin': False,
                                       'name': 'bar',
                                       'opacity': 1.0,
                                       'type': 'N',
                                       'value': '#4682b4',
                                       'legend': True}},
                'marktype': 'bar'}


    assert viz3.to_dict() == expected

    viz4 = api.Viz(data).hist(
        x=api.X(shorthand="x", bin=api.Bin(maxbins=40)))
    assert viz4.encoding.x.name == "x"
    assert viz4.encoding.x.bin.maxbins == 40
