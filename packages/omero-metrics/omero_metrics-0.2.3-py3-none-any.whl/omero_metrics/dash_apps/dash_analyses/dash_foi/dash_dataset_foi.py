from time import sleep
from omero_metrics import views
import dash
import pandas as pd
from dash import dcc, html
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
from linkml_runtime.dumpers import YAMLDumper, JSONDumper
from skimage.exposure import rescale_intensity
from omero_metrics.styles import (
    THEME,
    MANTINE_THEME,
    CONTAINER_STYLE,
    CONTENT_PAPER_STYLE,
    GRAPH_STYLE,
    PLOT_LAYOUT,
    LINE_CHART_SERIES,
    INPUT_BASE_STYLES,
    TABLE_MANTINE_STYLE,
)
import math
import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.tools import load

dashboard_name = "omero_dataset_foi"
omero_dataset_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

omero_dataset_foi.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.NotificationProvider(position="top-center"),
        html.Div(id="notifications-container"),
        dmc.Modal(
            title="Confirm Delete",
            id="confirm_delete",
            children=[
                dmc.Text(
                    "Are you sure you want to delete this dataset outputs?"
                ),
                dmc.Space(h=20),
                dmc.Group(
                    [
                        dmc.Button(
                            "Submit",
                            id="modal-submit-button",
                            color="red",
                        ),
                        dmc.Button(
                            "Close",
                            color="gray",
                            variant="outline",
                            id="modal-close-button",
                        ),
                    ],
                    justify="flex-end",
                ),
            ],
        ),
        my_components.header_component(
            "Field Illumination", "Dataset Analysis", "FOI Analysis"
        ),
        dmc.Container(
            [
                # Main Content
                dmc.Grid(
                    gutter="md",
                    align="stretch",
                    children=[
                        # Left Column - Intensity Map
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Intensity Map",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Select(
                                                            id="channel_dropdown_foi",
                                                            clearable=False,
                                                            allowDeselect=False,
                                                            w="200",
                                                            value="0",
                                                            leftSection=my_components.get_icon(
                                                                icon="material-symbols:layers"
                                                            ),
                                                            rightSection=my_components.get_icon(
                                                                icon="radix-icons:chevron-down"
                                                            ),
                                                            styles=INPUT_BASE_STYLES,
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    id="intensity_map",
                                                    config={
                                                        "displayModeBar": True,
                                                        "scrollZoom": True,
                                                        "modeBarButtonsToRemove": [
                                                            "lasso2d",
                                                            "select2d",
                                                        ],
                                                    },
                                                    style=GRAPH_STYLE,
                                                ),
                                            ],
                                            gap="md",
                                            justify="space-between",
                                            h="100%",
                                        ),
                                    ],
                                    **CONTENT_PAPER_STYLE,
                                ),
                            ],
                        ),
                        # Right Column - Key Measurements
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Key Measurements",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                my_components.download_table,
                                                                dmc.Tooltip(
                                                                    label="Statistical measurements for all the channels",
                                                                    children=[
                                                                        my_components.get_icon(
                                                                            icon="material-symbols:info",
                                                                            color=THEME[
                                                                                "primary"
                                                                            ],
                                                                        )
                                                                    ],
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dmc.ScrollArea(
                                                    offsetScrollbars=True,
                                                    children=[
                                                        dmc.Table(
                                                            id="km_table",
                                                            striped=True,
                                                            highlightOnHover=True,
                                                            withTableBorder=False,
                                                            withColumnBorders=True,
                                                            fz="sm",
                                                            style=TABLE_MANTINE_STYLE,
                                                        ),
                                                        dmc.Group(
                                                            mt="md",
                                                            children=[
                                                                dmc.Pagination(
                                                                    id="pagination",
                                                                    total=0,
                                                                    value=1,
                                                                    withEdges=True,
                                                                )
                                                            ],
                                                            justify="center",
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            gap="md",
                                            justify="space-between",
                                            h="100%",
                                        ),
                                    ],
                                    **CONTENT_PAPER_STYLE,
                                ),
                            ],
                        ),
                    ],
                ),
                # Hidden element for callbacks
                html.Div(id="blank-input"),
                # Intensity Profiles Section
                dmc.Paper(
                    children=[
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Intensity Profiles",
                                            fw=500,
                                            size="lg",
                                        ),
                                        dmc.SegmentedControl(
                                            id="profile-type",
                                            data=[
                                                {
                                                    "value": "natural",
                                                    "label": "Smooth",
                                                },
                                                {
                                                    "value": "linear",
                                                    "label": "Linear",
                                                },
                                            ],
                                            value="natural",
                                            color=THEME["primary"],
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dmc.LineChart(
                                    id="intensity_profile",
                                    h=300,
                                    dataKey="Pixel",
                                    data={},
                                    series=LINE_CHART_SERIES,
                                    xAxisLabel="Position (pixels)",
                                    yAxisLabel="Intensity",
                                    tickLine="y",
                                    gridAxis="x",
                                    withXAxis=True,
                                    withYAxis=True,
                                    withLegend=True,
                                    strokeWidth=2,
                                    withDots=False,
                                ),
                            ],
                            gap="xl",
                        ),
                    ],
                    shadow="xs",
                    p="md",
                    radius="md",
                    mt="md",
                ),
            ],
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
        ),
    ],
)


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("channel_dropdown_foi", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown_menu(*args, **kwargs):
    try:
        channel = kwargs["session_state"]["context"]["channel_names"]
        return [
            {"label": f"{name}", "value": f"{i}"}
            for i, name in enumerate(channel)
        ]
    except Exception as e:
        return [{"label": "Error loading channels", "value": "0"}]


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("km_table", "data"),
    dash.dependencies.Output("pagination", "total"),
    [
        dash.dependencies.Input("pagination", "value"),
    ],
)
def update_km_table(pagination_value, **kwargs):
    try:
        page = int(pagination_value)
        kkm = kwargs["session_state"]["context"]["kkm"]
        table_km = load.get_km_mm_metrics_dataset(
            mm_dataset=kwargs["session_state"]["context"]["mm_dataset"],
            table_name="key_measurements",
        )
        start_idx = (page - 1) * 4
        end_idx = start_idx + 4
        metrics_df = table_km.filter(["channel_name", *kkm])
        metrics_df = metrics_df.round(3)
        metrics_df.columns = metrics_df.columns.str.replace(
            "_", " ", regex=True
        ).str.title()
        page_data = metrics_df.iloc[start_idx:end_idx]
        return {
            "head": page_data.columns.tolist(),
            "body": page_data.values.tolist(),
            "caption": "Statistical measurements across channels",
        }, math.ceil(len(metrics_df) / 4)
    except Exception as e:
        return {
            "head": ["Error"],
            "body": [[str(e)]],
            "caption": "Error loading measurements",
        }, 1


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("intensity_map", "figure"),
    [
        dash.dependencies.Input("channel_dropdown_foi", "value"),
    ],
)
def update_intensity_map(channel, **kwargs):
    try:
        channel = int(channel)
        images = kwargs["session_state"]["context"]["image"]
        image = images[channel]
        image_channel = image[0, 0, :, :]
        image_channel = rescale_intensity(
            image_channel,
            in_range=(0, image_channel.max()),
            out_range=(0.0, 1.0),
        )
        # Create intensity map
        fig = px.imshow(
            image_channel,
            color_continuous_scale="hot",
            labels={"color": "Intensity"},
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="X Position (pixels)",
            yaxis_title="Y Position (pixels)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            coloraxis_colorbar=dict(
                thickness=15,
                len=0.7,
                title=dict(text="Intensity", side="right"),
                tickfont=dict(size=10),
            ),
        )
        return fig
    except Exception as e:
        fig = px.imshow([[0]])
        fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    dash.dependencies.Output("intensity_profile", "curveType"),
    [
        dash.dependencies.Input("channel_dropdown_foi", "value"),
        dash.dependencies.Input("profile-type", "value"),
    ],
)
def update_profile_type(channel, curve_type, **kwargs):
    try:
        df_intensity_profiles = load.load_table_mm_metrics(
            kwargs["session_state"]["context"]["mm_dataset"].output[
                "intensity_profiles"
            ]
        )
        df_profile = df_intensity_profiles.filter(regex=f"ch0*{channel}_")
        df_profile.columns = (
            df_profile.columns.str.replace(
                "ch\d+_leftTop_to_rightBottom", "Diagonal (↘)", regex=True
            )
            .str.replace(
                "ch\d+_leftBottom_to_rightTop", "Diagonal (↗)", regex=True
            )
            .str.replace(
                "ch\d+_center_horizontal", "Horizontal (→)", regex=True
            )
            .str.replace("ch\d+_center_vertical", "Vertical (↓)", regex=True)
        )
        return df_profile.to_dict("records"), curve_type

    except Exception as e:
        return [{"Pixel": 0}], "linear"


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Improve column names for better readability."""
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(df, col, value)
    return df


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("confirm_delete", "opened"),
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("modal-submit-button", "loading"),
    [
        dash.dependencies.Input("delete_data", "n_clicks"),
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.Input("modal-close-button", "n_clicks"),
        dash.dependencies.State("confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_dataset(*args, **kwargs):
    triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
    dataset_id = kwargs["session_state"]["context"][
        "mm_dataset"
    ].data_reference.omero_object_id
    request = kwargs["request"]
    opened = not args[3]
    if triggered_button == "modal-submit-button.n_clicks" and args[0] > 0:
        sleep(1)
        msg, color = views.delete_dataset(request, dataset_id=dataset_id)
        message = dmc.Notification(
            title="Notification!",
            id="simple-notify",
            action="show",
            message=msg,
            icon=my_components.get_icon(
                icon=(
                    "akar-icons:circle-check"
                    if color == "green"
                    else "akar-icons:circle-x"
                )
            ),
            color=color,
        )
        return opened, message, False
    else:
        return opened, None, False


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("download", "data"),
    [
        dash.dependencies.Input("download-yaml", "n_clicks"),
        dash.dependencies.Input("download-json", "n_clicks"),
        dash.dependencies.Input("download-text", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def download_dataset_data(*args, **kwargs):
    if not kwargs["callback_context"].triggered:
        raise dash.no_update

    triggered_id = (
        kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
    )
    mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
    file_name = mm_dataset.name
    yaml_dumper = YAMLDumper()
    json_dumper = JSONDumper()
    if triggered_id == "download-yaml":
        return dict(
            content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.yaml"
        )

    elif triggered_id == "download-json":
        return dict(
            content=json_dumper.dumps(mm_dataset), filename=f"{file_name}.json"
        )

    elif triggered_id == "download-text":
        return dict(
            content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.txt"
        )

    raise dash.no_update


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("table-download", "data"),
    [
        dash.dependencies.Input("table-download-csv", "n_clicks"),
        dash.dependencies.Input("table-download-xlsx", "n_clicks"),
        dash.dependencies.Input("table-download-json", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def download_table_data(*args, **kwargs):
    if not kwargs["callback_context"].triggered:
        raise dash.no_update

    triggered_id = (
        kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
    )
    table_km = load.get_km_mm_metrics_dataset(
        mm_dataset=kwargs["session_state"]["context"]["mm_dataset"],
        table_name="key_measurements",
    )
    kkm = kwargs["session_state"]["context"]["kkm"]
    metrics_df = table_km.filter(["channel_name", *kkm])
    metrics_df = metrics_df.round(3)
    metrics_df.columns = metrics_df.columns.str.replace(
        "_", " ", regex=True
    ).str.title()
    if triggered_id == "table-download-csv":
        return dcc.send_data_frame(metrics_df.to_csv, "km_table.csv")
    elif triggered_id == "table-download-xlsx":
        return dcc.send_data_frame(metrics_df.to_excel, "km_table.xlsx")
    elif triggered_id == "table-download-json":
        return dcc.send_data_frame(metrics_df.to_json, "km_table.json")
    raise dash.no_update


omero_dataset_foi.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "modal-submit-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)
