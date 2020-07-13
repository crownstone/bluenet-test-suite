from ipywidgets import HBox, VBox, Layout


def MakeHBox(widgetlistlist, widgetwidthlist):
    hbox_layout = Layout(
        overflow='scroll',
        height='',
        margin='5px 5px 0 0',
        flex_flow='row',
        display='stretch'
    )

    marge = '5px'

    columns = [
        VBox(children=widgetlistlist[i],
             layout=Layout(width=widgetwidthlist[i], margin=marge)
             ) for i in range(min(len(widgetlistlist), len(widgetwidthlist)))
    ]

    return HBox(children=columns, layout=hbox_layout)


def MakeHBox_single(widgetlist, widgetwidthlist):
    return MakeHBox([[widg] for widg in widgetlist], widgetwidthlist)
