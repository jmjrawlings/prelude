"""
Altair utilities
"""
import altair as alt
from collections import to_list


def val(x):
  """
  Return an Altair value, wraps it in `alt.value` if the given
  argument is a simple type
  """

  if isinstance(x, float) or isinstance(x, int) or (':' not in str(x)):
    return alt.value(x)

  return x


def cond(condition, t=1, f=0):
  """ 
  Altair Condition based on the selector, makes conditional
  properties easier to read.
    
  instead of:
    chart.encode(x = alt.condition(condition, alt.value(0.2), alt.value(1.0)))
  you can:
    chart.encode(x = alt_cond(condition, 0.2, 1.0))
  """
  if_true = val(t)
  if_false = val(f)
  return alt.condition(condition, if_true, if_false)


def tooltip(field:str, time_format="%Y-%m-%d %H:%M") -> alt.Tooltip:
  """
  Return an altair tooltip given the field
  definition.  This allows us to avoid
  specifying data types everywhere when specifying
  tooltips.
  """
  
  # Assume datetime tooltip
  if ':T' in field:
    return alt.Tooltip(field, format=time_format)
  
  # No type was specified
  if ':' not in field:
    
    # Assume time based on column name
    if 'time' in field.lower():
      return alt.Tooltip(field, format=time_format)
    # Otherwise nominal
    else:
      return alt.Tooltip(field + ':N')
  
  # Pass as normal
  return field


def tooltips(*args):
  """
  Helper function to specify tooltip encodings for a chart.
  
  instead of:
    chart.encode(tooltip=['name:N','type:N','amount:Q','time:T'])
  you can:
    chart.encode(tooltip=alt_tooltips('name','type','amount','time'))
  """

  return to_list(*args, ) list(map(alt_tooltip, args))
  


def select(*fields, empty='none', on='mouseover', clear='mouseout', **kwargs):
  """
  Create an altair selection as a well as
  a function that returns an altair condition
  based on the value
  """
  selection = alt.selection_single(
    fields=fields,
    empty=empty,
    on=on,
    clear=clear,
    **kwargs)
  
  def condition(t, f):
    return alt_cond(selection, t, f)
  
  return selection, condition


def configure_chart(chart):
    def tft(str):
        return f"timeFormat(datum.value, '{str}')"

    daystart = f"{tft('%H%M')} == '0000'"
    hourstart = f"{tft('%M')} == '00'"
    minstart = f"{tft('%S')} == '00'"
    dayfmt = tft("%b %-d")
    minfmt = tft("%H%M")

    return (
        chart.configure_title(fontSize=14, color=black, font="monospace")
        .configure_text(
            fontSize=16,
            color=black,
            font="monospace",
            baseline="middle",
        )
        .configure_axisY(gridWidth=0.5)
        .configure_axisTemporal(
            labelExpr=f"{daystart} ? {dayfmt} : {minfmt}",
            title=None,
            tickCount=10,
            gridOpacity=cond(minstart, 1.0, 0.0),
            labelFontSize=16,
            gridWidth=cond(hourstart, 0.5, 0.3),
            labelFont="monospace",
            labelFontStyle=cond(daystart, "bold", "normal"),
            labelColor=cond(
                f"(parseInt({tft('%M')}) % 5 == 0) && {tft('%S')} == '00'", "gray", ""
            ),
        )
    )