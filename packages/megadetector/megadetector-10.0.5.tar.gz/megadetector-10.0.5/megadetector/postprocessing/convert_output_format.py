"""

convert_output_format.py

Converts between file formats output by our batch processing API.  Currently
supports json <--> csv conversion, but this should be the landing place for any
conversion - including between hypothetical alternative .json versions - that we support
in the future.

The .csv format is largely obsolete, don't use it unless you're super-duper sure you need it.

"""

#%% Constants and imports

import argparse
import json
import csv
import sys
import os

from tqdm import tqdm

from megadetector.postprocessing.load_api_results import load_api_results_csv
from megadetector.data_management.annotations import annotation_constants
from megadetector.utils import ct_utils

CONF_DIGITS = 3


#%% Conversion functions

def convert_json_to_csv(input_path,
                        output_path=None,
                        min_confidence=None,
                        omit_bounding_boxes=False,
                        output_encoding=None,
                        overwrite=True):
    """
    Converts a MD results .json file to a totally non-standard .csv format.

    If [output_path] is None, will convert x.json to x.csv.

    TODO: this function should obviously be using Pandas or some other sensible structured
    representation of tabular data.  Even a list of dicts.  This implementation is quite
    brittle and depends on adding fields to every row in exactly the right order.

    Args:
        input_path (str): the input .json file to convert
        output_path (str, optional): the output .csv file to generate; if this is None, uses
            [input_path].csv
        min_confidence (float, optional): the minimum-confidence detection we should include
            in the "detections" column; has no impact on the other columns
        omit_bounding_boxes (bool, optional): whether to leave out the json-formatted bounding
            boxes that make up the "detections" column, which are not generally useful for someone
            who wants to consume this data as a .csv file
        output_encoding (str, optional): encoding to use for the .csv file
        overwrite (bool, optional): whether to overwrite an existing .csv file; if this is False and
            the output file exists, no-ops and returns

    """

    if output_path is None:
        output_path = os.path.splitext(input_path)[0]+'.csv'

    if os.path.isfile(output_path) and (not overwrite):
        print('File {} exists, skipping json --> csv conversion'.format(output_path))
        return

    print('Loading json results from {}...'.format(input_path))
    json_output = json.load(open(input_path))

    rows = []

    fixed_columns = ['image_path', 'max_confidence', 'detections']

    # We add an output column for each class other than 'empty',
    # containing the maximum probability of  that class for each image
    # n_non_empty_detection_categories = len(annotation_constants.annotation_bbox_categories) - 1
    n_non_empty_detection_categories = annotation_constants.NUM_DETECTOR_CATEGORIES
    detection_category_column_names = []
    assert annotation_constants.detector_bbox_category_id_to_name[0] == 'empty'
    for cat_id in range(1,n_non_empty_detection_categories+1):
        cat_name = annotation_constants.detector_bbox_category_id_to_name[cat_id]
        detection_category_column_names.append('max_conf_' + cat_name)

    n_classification_categories = 0

    if 'classification_categories' in json_output.keys():
        classification_category_id_to_name = json_output['classification_categories']
        classification_category_ids = list(classification_category_id_to_name.keys())
        classification_category_id_to_column_number = {}
        classification_category_column_names = []
        for i_category,category_id in enumerate(classification_category_ids):
            category_name = classification_category_id_to_name[category_id].\
                replace(' ','_').replace(',','')
            classification_category_column_names.append('max_classification_conf_' + category_name)
            classification_category_id_to_column_number[category_id] = i_category

        n_classification_categories = len(classification_category_ids)

    # There are several .json fields for which we add .csv columns; other random bespoke fields
    # will be ignored.
    optional_fields = ['width','height','datetime','exif_metadata']
    optional_fields_present = set()

    # Iterate once over the data to check for optional fields
    print('Looking for optional fields...')

    for im in tqdm(json_output['images']):
        # Which optional fields are present for this image?
        for k in im.keys():
            if k in optional_fields:
                optional_fields_present.add(k)

    optional_fields_present = sorted(list(optional_fields_present))
    if len(optional_fields_present) > 0:
        print('Found {} optional fields'.format(len(optional_fields_present)))

    expected_row_length = len(fixed_columns) + len(detection_category_column_names) + \
        n_classification_categories + len(optional_fields_present)

    print('Formatting results...')

    # i_image = 0; im = json_output['images'][i_image]
    for im in tqdm(json_output['images']):

        image_id = im['file']

        if 'failure' in im and im['failure'] is not None:
            row = [image_id, 'failure', im['failure']]
            rows.append(row)
            # print('Skipping failed image {} ({})'.format(im['file'],im['failure']))
            continue

        max_conf = ct_utils.get_max_conf(im)
        detections = []
        max_detection_category_probabilities = [None] * n_non_empty_detection_categories
        max_classification_category_probabilities = [0] * n_classification_categories

        # d = im['detections'][0]
        for d in im['detections']:

            # Skip sub-threshold detections
            if (min_confidence is not None) and (d['conf'] < min_confidence):
                continue

            input_bbox = d['bbox']

            # Our .json format is xmin/ymin/w/h
            #
            # Our .csv format was ymin/xmin/ymax/xmax
            xmin = input_bbox[0]
            ymin = input_bbox[1]
            xmax = input_bbox[0] + input_bbox[2]
            ymax = input_bbox[1] + input_bbox[3]
            output_detection = [ymin, xmin, ymax, xmax]

            output_detection.append(d['conf'])

            # Category 0 is empty, for which we don't have a column, so the max
            # confidence for category N goes in column N-1
            detection_category_id = int(d['category'])
            assert detection_category_id > 0 and detection_category_id <= \
                n_non_empty_detection_categories
            detection_category_column = detection_category_id - 1
            detection_category_max = max_detection_category_probabilities[detection_category_column]
            if detection_category_max is None or d['conf'] > detection_category_max:
                max_detection_category_probabilities[detection_category_column] = d['conf']

            output_detection.append(detection_category_id)
            detections.append(output_detection)

            if 'classifications' in d:
                assert n_classification_categories > 0,\
                    'Oops, I have classification results, but no classification metadata'
                for c in d['classifications']:
                    category_id = c[0]
                    p = c[1]
                    category_index = classification_category_id_to_column_number[category_id]
                    if (max_classification_category_probabilities[category_index] < p):
                        max_classification_category_probabilities[category_index] = p

                # ...for each classification

            # ...if we have classification results for this detection

        # ...for each detection

        detection_string = ''
        if not omit_bounding_boxes:
            detection_string = json.dumps(detections)

        row = [image_id, max_conf, detection_string]
        row.extend(max_detection_category_probabilities)
        row.extend(max_classification_category_probabilities)

        for field_name in optional_fields_present:
            if field_name not in im:
                row.append('')
            else:
                row.append(str(im[field_name]))

        assert len(row) == expected_row_length
        rows.append(row)

    # ...for each image

    print('Writing to csv...')

    with open(output_path, 'w', newline='', encoding=output_encoding) as f:
        writer = csv.writer(f, delimiter=',')
        header = fixed_columns
        header.extend(detection_category_column_names)
        if n_classification_categories > 0:
            header.extend(classification_category_column_names)
        for field_name in optional_fields_present:
            header.append(field_name)
        writer.writerow(header)
        writer.writerows(rows)

# ...def convert_json_to_csv(...)


def convert_csv_to_json(input_path,output_path=None,overwrite=True):
    """
    Convert .csv to .json.  If output_path is None, will convert x.csv to x.json.

    Args:
        input_path (str): .csv filename to convert to .json
        output_path (str, optional): the output .json file to generate; if this is None, uses
            [input_path].json
        overwrite (bool, optional): whether to overwrite an existing .json file; if this is
            False and the output file exists, no-ops and returns

    """

    if output_path is None:
        output_path = os.path.splitext(input_path)[0]+'.json'

    if os.path.isfile(output_path) and (not overwrite):
        print('File {} exists, skipping csv --> json conversion'.format(output_path))
        return

    # Format spec:
    #
    # https://github.com/agentmorris/MegaDetector/tree/main/megadetector/api/batch_processing

    print('Loading csv results...')
    df = load_api_results_csv(input_path)

    info = {
        "format_version":"1.2",
        "detector": "unknown",
        "detection_completion_time" : "unknown",
        "classifier": "unknown",
        "classification_completion_time": "unknown"
    }

    classification_categories = {}
    detection_categories = annotation_constants.detector_bbox_categories

    images = []

    # i_file = 0; row = df.iloc[i_file]
    for i_file,row in df.iterrows():

        image = {}
        image['file'] = row['image_path']
        image['max_detection_conf'] = round(row['max_confidence'], CONF_DIGITS)
        src_detections = row['detections']
        out_detections = []

        for i_detection,detection in enumerate(src_detections):

            # Our .csv format was ymin/xmin/ymax/xmax
            #
            # Our .json format is xmin/ymin/w/h
            ymin = detection[0]
            xmin = detection[1]
            ymax = detection[2]
            xmax = detection[3]
            bbox = [xmin, ymin, xmax-xmin, ymax-ymin]
            conf = detection[4]
            i_class = detection[5]
            out_detection = {}
            out_detection['category'] = str(i_class)
            out_detection['conf'] = conf
            out_detection['bbox'] = bbox
            out_detections.append(out_detection)

        # ...for each detection

        image['detections'] = out_detections
        images.append(image)

    # ...for each image
    json_out = {}
    json_out['info'] = info
    json_out['detection_categories'] = detection_categories
    json_out['classification_categories'] = classification_categories
    json_out['images'] = images

    json.dump(json_out,open(output_path,'w'),indent=1)

# ...def convert_csv_to_json(...)


#%% Interactive driver

if False:

    #%%

    input_path = r'c:\temp\test.json'
    min_confidence = None
    output_path = input_path + '.csv'
    convert_json_to_csv(input_path,output_path,min_confidence=min_confidence,
                        omit_bounding_boxes=False)

    #%%

    base_path = r'c:\temp\json'
    input_paths = os.listdir(base_path)
    input_paths = [os.path.join(base_path,s) for s in input_paths]

    min_confidence = None
    for input_path in input_paths:
        output_path = input_path + '.csv'
        convert_json_to_csv(input_path,output_path,min_confidence=min_confidence,
                            omit_bounding_boxes=True)

    #%% Concatenate .csv files from a folder

    import glob
    csv_files = glob.glob(os.path.join(base_path,'*.json.csv' ))
    master_csv = os.path.join(base_path,'all.csv')

    print('Concatenating {} files to {}'.format(len(csv_files),master_csv))

    header = None
    with open(master_csv, 'w') as fout:

        for filename in tqdm(csv_files):

            with open(filename) as fin:

                lines = fin.readlines()

                if header is not None:
                    assert lines[0] == header
                else:
                    header = lines[0]
                    fout.write(header)

                for line in lines[1:]:
                    if len(line.strip()) == 0:
                        continue
                    fout.write(line)

        # ...for each .csv file

    # with open(master_csv)


#%% Command-line driver

def main():
    """
    Command-line driver for convert_output_format(), which converts
    json <--> csv.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('input_path',type=str,
                        help='Input filename ending in .json or .csv')
    parser.add_argument('--output_path',type=str,default=None,
                        help='Output filename ending in .json or .csv (defaults to ' + \
                             'input file, with .json/.csv replaced by .csv/.json)')
    parser.add_argument('--omit_bounding_boxes',action='store_true',
                        help='Output bounding box text from .csv output (large and usually not useful)')

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.output_path is None:
        if args.input_path.endswith('.csv'):
            args.output_path = args.input_path[:-4] + '.json'
        elif args.input_path.endswith('.json'):
            args.output_path = args.input_path[:-5] + '.csv'
        else:
            raise ValueError('Illegal input file extension')

    if args.input_path.endswith('.csv') and args.output_path.endswith('.json'):
        assert not args.omit_bounding_boxes, \
            '--omit_bounding_boxes does not apply to csv --> json conversion'
        convert_csv_to_json(args.input_path,args.output_path)
    elif args.input_path.endswith('.json') and args.output_path.endswith('.csv'):
        convert_json_to_csv(args.input_path,args.output_path,omit_bounding_boxes=args.omit_bounding_boxes)
    else:
        raise ValueError('Illegal format combination')

if __name__ == '__main__':
    main()
