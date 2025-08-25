import logging
import yaml
import numpy as np
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
    FileAnnotationWrapper,
    MapAnnotationWrapper,
)
import microscopemetrics_schema.datamodel as mm_schema
from linkml_runtime.loaders import yaml_loader
import pandas as pd
from omero_metrics.tools import omero_tools
import re
import omero
from datetime import datetime
from omero_metrics.tools.data_type import (
    DATASET_IMAGES,
    DATASET_TYPES,
    INPUT_IMAGES_MAPPING,
)

logger = logging.getLogger(__name__)


def get_annotations_tables(conn, group_id):
    all_annotations = conn.getObjects("Annotation", opts={"group": group_id})
    file_ann_cols = [
        "Name",
        "ID",
        "File_ID",
        "Description",
        "Date",
        "Owner",
        "NS",
    ]
    file_ann_rows = []
    map_ann_cols = ["Name", "ID", "Description", "Date", "Owner", "NS"]
    map_ann_rows = []
    for ann in all_annotations:
        if ann.getNs() and ann.getNs().startswith("microscopemetrics"):
            if isinstance(ann, FileAnnotationWrapper):
                file_ann_rows.append(
                    [
                        ann.getFile().getName(),
                        ann.getId(),
                        ann.getFile().getId(),
                        ann.getDescription(),
                        ann.getDate(),
                        ann.getOwner().getName(),
                        ann.getNs(),
                    ]
                )
            elif isinstance(ann, omero.gateway.MapAnnotationWrapper):
                map_ann_rows.append(
                    [
                        ann.getName(),
                        ann.getId(),
                        ann.getDescription(),
                        ann.getDate(),
                        ann.getOwner().getName(),
                        ann.getNs(),
                    ]
                )
    file_ann_df = pd.DataFrame(file_ann_rows, columns=file_ann_cols)
    map_ann_df = pd.DataFrame(map_ann_rows, columns=map_ann_cols)
    file_ann_df["Date"] = pd.to_datetime(file_ann_df["Date"])
    map_ann_df["Date"] = pd.to_datetime(map_ann_df["Date"])
    return file_ann_df, map_ann_df


def get_annotations_list_group(conn, group_id):
    projects = conn.getObjects("Project", opts={"group": group_id})
    data = []
    columns = [
        "Name",
        "ID",
        "File_ID",
        "Description",
        "Date",
        "Owner",
        "Project_ID",
        "Project_Name",
        "NS",
        "Type",
    ]
    for p in projects:
        data.extend(
            [
                ds.getFile().getName(),
                ds.getId(),
                ds.getFile().getId(),
                ds.getDescription(),
                ds.getDate(),
                ds.getOwner().getName(),
                p.getId(),
                p.getName(),
                ds.getNs(),
                ds.__class__.__name__,
            ]
            for ds in p.listAnnotations()
        )

    return pd.DataFrame(data, columns=columns)


def image_exist(image_id, mm_dataset):
    image_found = False
    image_location = None
    index = None
    for k, v in DATASET_IMAGES[mm_dataset.__class__.__name__].items():
        if v:
            images_list = getattr(mm_dataset[k], v[0])
            if not isinstance(images_list, list):
                images_list = [images_list]
            for i, image in enumerate(images_list):
                if image_id == image.data_reference.omero_object_id:
                    image_found = True
                    image_location = k
                    index = i
                    break
    return image_found, image_location, index


def load_config_file_data(project):
    setup = None
    for ann in project.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            ns = ann.getNs()
            if ns in [
                cls.class_class_curie
                for cls in mm_schema.MetricsInputParameters.__subclasses__()
            ]:
                setup = yaml.load(
                    ann.getFileInChunks().__next__().decode(),
                    Loader=yaml.SafeLoader,
                )
    return setup


def load_thresholds_file_data(project):
    thresholds = None
    for ann in project.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            name = ann.getFile().getName()
            if name.startswith("threshold"):
                thresholds = yaml.load(
                    ann.getFileInChunks().__next__().decode(),
                    Loader=yaml.SafeLoader,
                )
    return thresholds


def load_project(
    conn: BlitzGateway, project_id: int
) -> mm_schema.MetricsDatasetCollection:
    collection = mm_schema.MetricsDatasetCollection()
    file_anns = []
    dataset_types = []
    project = conn.getObject("Project", project_id)
    try:
        for file_ann in project.listAnnotations():
            if isinstance(file_ann, FileAnnotationWrapper):
                ds_type = file_ann.getFileName().split("_")[0]
                if ds_type in DATASET_TYPES:
                    file_anns.append(file_ann)
                    dataset_types.append(ds_type)

        for file_ann, ds_type in zip(file_anns, dataset_types):
            collection.dataset_collection.append(
                yaml_loader.loads(
                    file_ann.getFileInChunks().__next__().decode(),
                    target_class=getattr(mm_schema, ds_type),
                )
            )
        return collection
    except Exception as e:
        logger.error(f"Error loading project {project_id}: {e}")
        return collection


def load_dataset(
    dataset: DatasetWrapper, load_images: bool
) -> mm_schema.MetricsDataset:
    mm_datasets = []
    for ann in dataset.listAnnotations():
        if isinstance(ann, FileAnnotationWrapper):
            ns = ann.getNs()
            if ns.startswith("microscopemetrics_schema:analyses"):
                ds_type = ns.split("/")[-1]
                if ds_type in DATASET_TYPES:
                    mm_datasets.append(
                        yaml_loader.loads(
                            ann.getFileInChunks().__next__().decode(),
                            target_class=getattr(mm_schema, ds_type),
                        )
                    )
    if len(mm_datasets) == 1:
        mm_dataset = mm_datasets[0]
    elif len(mm_datasets) > 1:
        logger.warning(
            f"More than one dataset"
            f"found in dataset {dataset.getId()}."
            f"Using the first one"
        )
        mm_dataset = mm_datasets[0]
    else:
        logger.info(f"No dataset found in dataset {dataset.getId()}")
        return None

    if load_images and mm_dataset.__class__.__name__ != "PSFBeadsDataset":
        # First time loading the images the
        # dataset does not know which images to load
        if mm_dataset.processed:
            input_images = getattr(
                mm_dataset.input_data,
                INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__],
            )
            for input_image in input_images:
                image_wrapper = omero_tools.get_omero_obj_from_mm_obj(
                    dataset._conn, input_image
                )
                input_image.array_data = _load_image_intensities(image_wrapper)
        else:
            input_images = [
                load_image(image) for image in dataset.listChildren()
            ]
            setattr(
                mm_dataset,
                INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__],
                input_images,
            )
    else:
        setattr(
            mm_dataset, INPUT_IMAGES_MAPPING[mm_dataset.__class__.__name__], []
        )

    return mm_dataset


def load_dash_data_project(
    processed_datasets: dict,
) -> (dict, str):
    dash_context = {}
    df_list = []
    kkm = list(processed_datasets.values())[0].kkm
    dates = []
    for key, value in processed_datasets.items():
        df = get_km_mm_metrics_dataset(
            mm_dataset=value.mm_dataset, table_name="key_measurements"
        )
        date = datetime.strptime(
            value.mm_dataset.acquisition_datetime, "%Y-%m-%dT%H:%M:%S"
        )
        dates.append(date.date())
        df_list.append(df)
    dash_context["key_measurements_list"] = df_list
    dash_context["kkm"] = kkm
    dash_context["dates"] = dates
    return dash_context


def load_analysis_config(project_wrapper=ProjectWrapper):
    configs = [
        ann
        for ann in project_wrapper.listAnnotations(
            ns="omero-metrics/analysis_config"
        )
        if isinstance(ann, MapAnnotationWrapper)
    ]
    if not configs:
        return None, None
    if len(configs) > 1:
        logger.error(
            f"More than one configuration"
            f" in project {project_wrapper.getId()}."
            f"Using the last one saved"
        )

    return configs[-1].getId(), dict(configs[-1].getValue())


def load_image(
    image: ImageWrapper, load_array: bool = True
) -> mm_schema.Image:
    """Load an image from OMERO and return it as a schema Image"""
    time_series = None
    channel_series = mm_schema.ChannelSeries(
        channels=[
            {
                "name": c.getName(),
                "description": c.getDescription(),
                "data_reference": omero_tools.get_ref_from_object(c),
                "emission_wavelength_nm": c.getEmissionWave(),
                "excitation_wavelength_nm": c.getExcitationWave(),
            }
            for c in image.getChannels()
        ]
    )
    source_images = []
    array_data = _load_image_intensities(image) if load_array else None
    return mm_schema.Image(
        name=image.getName(),
        description=image.getDescription(),
        data_reference=omero_tools.get_ref_from_object(image),
        shape_x=image.getSizeX(),
        shape_y=image.getSizeY(),
        shape_z=image.getSizeZ(),
        shape_c=image.getSizeC(),
        shape_t=image.getSizeT(),
        acquisition_datetime=image.getAcquisitionDate(),
        voxel_size_x_micron=image.getPixelSizeX(),
        voxel_size_y_micron=image.getPixelSizeY(),
        voxel_size_z_micron=image.getPixelSizeZ(),
        time_series=time_series,
        channel_series=channel_series,
        source_images=source_images,
        array_data=array_data,
    )


def _load_image_intensities(image: ImageWrapper) -> np.ndarray:
    return omero_tools.get_image_intensities(image).transpose((2, 0, 3, 4, 1))


def concatenate_images(images: list):
    list_images = []
    list_channels = []
    for mm_image in images:
        image = mm_image.array_data
        result = [image[:, :, :, :, i] for i in range(image.shape[4])]
        channels = [c.name for c in mm_image.channel_series.channels]
        list_images.extend(result)
        list_channels.extend(channels)
    return list_images, list_channels


def roi_finder(roi: mm_schema.Roi):
    if roi.rectangles:
        return {
            "type": "Rectangle",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": rect.name,
                    "x": rect.x,
                    "y": rect.y,
                    "w": rect.w,
                    "h": rect.h,
                }
                for rect in roi.rectangles
            ],
        }
    elif roi.lines:
        return {
            "type": "Line",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": line.name,
                    "x1": line.x1,
                    "y1": line.y1,
                    "x2": line.x2,
                    "y2": line.y2,
                }
                for line in roi.lines
            ],
        }
    elif roi.points:
        return {
            "type": "Point",
            "data": [
                {
                    "roi_name": roi.name,
                    "name": point.name,
                    "x": point.x,
                    "y": point.y,
                    "c": point.c,
                }
                for point in roi.points
            ],
        }
    else:
        return None


def get_image_info_mm_dataset(mm_dataset: mm_schema.MetricsDataset):
    mm_images = getattr(
        mm_dataset["input_data"],
        DATASET_IMAGES[mm_dataset.class_name]["input_data"][0],
    )
    image_info = {
        i.data_reference.omero_object_id: {
            "name": i.name,
            "id": i.data_reference.omero_object_id,
            "n_channel": i.shape_c,
            "roi": {"Rectangle": [], "Line": [], "Point": []},
            "intensity_profiles": [],
        }
        for i in mm_images
    }
    return image_info


def get_rois_mm_dataset(mm_dataset: mm_schema.MetricsDataset):
    images_info = get_image_info_mm_dataset(mm_dataset)
    output = mm_dataset.output
    for i, item in enumerate(images_info.items()):
        for field in output:
            if (
                isinstance(output[field], mm_schema.Roi)
                and isinstance(output[field].linked_references, list)
                and len(output[field].linked_references) == len(images_info)
            ):
                roi = roi_finder(output[field])
                if roi:
                    images_info[item[0]]["roi"][roi["type"]].extend(
                        roi["data"]
                    )
            elif (
                isinstance(output[field], list)
                and len(output[field]) == len(images_info)
                and isinstance(output[field][i], mm_schema.Roi)
            ):
                roi = roi_finder(output[field][i])
                if roi:
                    images_info[item[0]]["roi"][roi["type"]].extend(
                        roi["data"]
                    )
    return images_info


def get_km_mm_metrics_dataset(
    mm_dataset,
    table_name,
    columns_exceptions=[
        "omero_object_type",
        "data_reference",
        "name",
        "description",
        "linked_references",
        "class_class_name",
        "table_data",
    ],
):
    table = mm_dataset.output[table_name]
    table_date = {
        k: v
        for k, v in table.__dict__.items()
        if k not in columns_exceptions and v
    }
    df = pd.DataFrame(table_date)
    df = df.replace("nan", np.nan)
    df = df.apply(lambda col: pd.to_numeric(col, errors="ignore"))
    return df


def load_table_mm_metrics(table):
    if table and isinstance(table, mm_schema.Table):
        table_date = {v.name: v.values for v in table.columns if v}
        df = pd.DataFrame(table_date)
        df = df.replace("nan", np.nan)
        df = df.apply(lambda col: pd.to_numeric(col, errors="ignore"))
        return df
    elif (
        table
        and isinstance(table, list)
        and isinstance(table[0], mm_schema.Table)
    ):
        df_list = []
        start = 0
        for i, t in enumerate(table):
            table_date = {v.name: v.values for v in t.columns if v}
            df = pd.DataFrame(table_date)
            df = df.apply(lambda col: pd.to_numeric(col, errors="ignore"))
            df.columns = [modify_column_name(col, start) for col in df.columns]
            df = df.replace("nan", np.nan)
            start = df.columns.str.extract(r"ch(\d+)").astype(int)[0].max() + 1
            df_list.append(df)
        return pd.concat(df_list, axis=1)
    else:
        return None


def modify_column_name(col, i):
    match = re.search(r"ch(\d+)", col)
    if match:
        new_ch = int(match.group(1)) + i
        return col.replace(match.group(0), f"ch{new_ch}")
    return col
