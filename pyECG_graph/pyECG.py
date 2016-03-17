##############################################################
# ECG graph generator
# Author: Kartikeya Rokde
##############################################################

import os
import sys
import ast
import math
import numpy
import json
import logging
import subprocess
import matplotlib
matplotlib.use('Agg')

import matplotlib.pylab as p
from matplotlib import pyplot as plt
from pkg_resources import resource_string, resource_listdir, resource_stream

#------------------------------------------------------------------------------

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def generate_ecg_graph(ecg_data, output_dir, output_file_name='graph', export_to='pdf', meta={}, *args, **kwargs):
    """
    Generates ECG graph for given data
    @param ecg_data: Required. ECG graph data.
                        - Data should be a valid list OR a valid file path.
    @param output_dir: Required. Valid directory path where generated output files are to be placed.
    @param export_to: Exports graph to provided format. Supported export file types are 'pdf', 'jpg', 'png'. 
                        Default is 'pdf'.
    @param meta: Optional dictionary containing any information. It will be printed on top of the output file.
    @param kwargs: 
            record_frequency: Default=250.0. Specifies the frequency on which ECG data was taken. 
                              Assuming default frequency 250 Hz.
    """
    
    def get_ecg_data(record_path):
        """
            Method to get ecg data from file
            @param record_path: Path of ECG record
            @return: list of ECG records
        """
        logger.debug("Reading ECG data from data file = %s" % record_path)
        # Check if record path is provided
        if record_path is None or record_path == "":
            sys.exit("ECG GRAPH GENERATOR: Record path not provided")
            return None
        
        # Reading graph data from record
        try:    
            with open(record_path, 'r') as graph_data_file:
                graph_data = graph_data_file.read()
                
        # Record path provided is invalid
        except:
            sys.exit("ECG GRAPH GENERATOR: Record path is invalid. Record path: %s" % record_path)
            return None
        
        # Converting record data to list
        try:
            graph_list = ast.literal_eval(graph_data)
            if not isinstance(graph_list, list):
                raise Exception
        except:
            sys.exit("ECG GRAPH GENERATOR: Record is not a valid list")
            return None
        
        # Returning graph list
        return graph_list

    def chunks(l, n):
        """
            Method to chunk list to list of lists
            @param l: list to be chunk
            @param n: number to which list needs to be chunk
            @return: generator object of list of lists
        """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]
            
    def padwithnone(vector, pad_width, iaxis, kwargs):
        """
            Method to pad numpy array with None
        """
        if pad_width != (0,0):
            vector[:pad_width[0]] = None    
            vector[-pad_width[1]:] = None
        return vector
    
    def prepadwithnone(vector, pad_width, iaxis, kwargs):
        """
            Method to prepad numpy array with None
        """
        if pad_width != (0,0):
            vector[pad_width[0]:pad_width[1]] = None
        
        return vector[ 0 : (( len(vector )) - ( 2 * pad_width[1] )) ]
    
    def partition(lst, n):
        """
            Method to partition list to lists
            @param lst: list to be partitioned
            @param n: number of lists for the list to be partitioned to
        """
        division = len(lst) / float(n)
        return [ lst[int(round(division * i)): int(round(division * (i + 1)))] for i in xrange(n) ]
    
    logger.debug("Started executing pyECG.generate_ecg_graph()")
    
    # # Constants
    
    # Strip time
    one_strip_time = 8 # seconds
    
    # ECG record frequency
    default_frequency = 250.0 # Hz
    
    # Plot scale
    plot_scale = "25mm/s, 10mm/mV"
    
    # Graph plotting resolution
    resolution = 72 # ppi (pixels per inch)
    
    # No. of pixels in 1 cm for current resolution
    cm = 28.35 # pixels
    
    # Image size
    image_size = (int(20*cm), int(20*cm)) # 567x567 px
    
    # Limits of graph on Y axis
    y_limit = (-2.5, 2.5) # cm
    
    # One page strips limit
    strips_per_page = 4
    
    # Checking if export to format is supported
    if export_to not in ['pdf', 'jpg', 'png']:
        logger.error("Exporting to '%s' is not supported. export_to must be one of ['pdf', 'svg', 'jpg', 'png']" % str(export_to))
        return None
    
    # Getting data from kwargs
    record_frequency = kwargs.get('record_frequency', default_frequency)
    logger.debug("Record frequency = %s" % record_frequency)
    
    # Check if ecg_data is a valid list, else getting data from file
    if isinstance(ecg_data, list):
        record = ecg_data
    else:
        record = get_ecg_data(ecg_data)
    
    # Checking if data is a valid list
    if not isinstance(record, list):
        logger.error("ECG record provided must be a valid list")
        return None
    
    # Prepending initial 125 records with none for ECG legend
    for _ in range(0, 125):
        record.insert(0, None)
    
    # Calculating number of records
    signals_num = len(record)
    logger.debug("ECG Signals count = %s" % signals_num)
    
    # Calculating no. of records needed in a strip
    one_strip_length = one_strip_time * record_frequency
    
    # No. of strips need to plot    
    no_of_strips = float(math.ceil(float(signals_num) / float(one_strip_length)))
    
    extra_strips_needed = 0
    # Calculating difference for number of strips on page
    if no_of_strips%strips_per_page:
        extra_strips_needed = strips_per_page - (no_of_strips%strips_per_page)
    
        # Appending none in the extra strips
        for a in range(int(extra_strips_needed)):
            for _ in range(0, int(one_strip_length)):
                record.append(None)
        
    record_list = partition(record, int((no_of_strips+extra_strips_needed)/strips_per_page))
    
    record_time = int(round((signals_num - 125) / record_frequency))
    logger.debug("ECG record time = %s seconds for Record Frequency %s" % (record_time, record_frequency))
    
    if no_of_strips < strips_per_page:
        no_of_strips += extra_strips_needed
    
    # Output files dict
    output_files = {}
    
    for seq, rec in enumerate(record_list):
    
        # # Graph plotting setup
        plt.axis('off')
        
        # Forming figure
        # figsize 10.13, 9.8 generates a perfect 567x567 pixels svg
        fig = plt.figure(figsize=(10.13,9.8), dpi=resolution)
        fig.subplots_adjust(hspace=0)
        
        # drawing stuff follows
        ylims = y_limit
        start_time = 0
        end_time = 0
        
        # Split record in chunks
        plot_record_list = chunks(rec, int(one_strip_length))
        
        
        # # Plotting graph
        for num, plot in enumerate(plot_record_list):
            
            # read data for specified signal
            # equal to record.read(i, ...
            numpy_plot = numpy.array(plot)
            
            if num == 0:
                # Pre-padding initial 125 data with none for graph to draw after legend 
                data = numpy.pad(numpy_plot, (0,125), prepadwithnone)
                data = data [ 0 : (len(data) - 125) ]
            else:
                # Padding data at the end if length is less than one strip length
                data = numpy.pad(numpy_plot, (0,one_strip_length-len(numpy_plot)), padwithnone)
            
            # Adding to endtime
            end_time += len(data) / record_frequency
            
            # Arranging data to plot grid
            nrange = [start_time + nu*(1/record_frequency) for nu in range(len(data))\
                      if (start_time + nu*(1/record_frequency)) <= end_time] 
            t = numpy.array(nrange)
            
            # Adding subplot to the current figure
            ax = p.subplot(no_of_strips, 1, num+1)
            
            # Switching off drawing of axis lines
            ax.axis('off')
            
            # Setting x & y limits
            p.ylim(*ylims)
            p.xlim(start_time, end_time)
            
            # drawing signal
            try:
                ax.plot(t, data, linewidth=0.4, color='k', alpha=1.0)
            except ValueError as e:
                logger.error("Error in plotting ECG data. Error: %s" % e)
                return None
            
            # New start time
            start_time = end_time
            
            # Removing labels
            p.setp(ax.get_xticklabels(), visible=False)
            p.setp(ax.get_yticklabels(), visible=False)
        
        
        file_name = output_dir
        file_name += str(seq+1) + '.svg'
        
        # Saving the plotted graph
        fig.savefig(file_name,
                    dpi=resolution,
                    transparent=True, bbox_inches='tight', pad_inches=0.01)        
        
        # # Merging ecg graph and ecg grid
        
        # Opening graph svg file plotted above by matplotlib
        graph_svg_file = open(file_name, 'rw+')
        graph_svg = graph_svg_file.read()
        
        # Opening grid svg file template
        grid_svg = resource_string('pyECG_graph.resources', 'ecg_grid.svg')
        
        # # Adding graph data to grid data
        
        # Deleting data other than graph
        graph_data = graph_svg[462:]
        graph_data = graph_data[:-7]
        grid_data = grid_svg.replace('$$ecg_graph$$',graph_data)
        
        # Truncating file data
        graph_svg_file.truncate()
        graph_svg_file.close()
        
        # Merging graph data with grid data
        with open(file_name, 'w') as graph_svg_file:
            graph_svg_file.write(str(grid_data))
        
        # Graph plotted successfully
        output_files [seq+1] = str(output_dir + output_file_name + '.' + export_to)
        logger.debug("SVG file written successfully. File = %s" % file_name)
    
    # Writing meta data file
    display_information = {'Record frequency' : str(record_frequency) + ' Hz',
                           'Scale' : plot_scale,
                           'No. of signals' : signals_num, 
                           'Duration' : str(int(math.ceil(record_time))) + ' seconds'}
    meta_data = dict(record_frequency=record_frequency,
                     scale=plot_scale, 
                     signals_num=signals_num,
                     record_time=record_time,
                     output_files=output_files,
                     display_information=display_information)

    # Writing graph to PDF
    page_2_template = resource_string('pyECG_graph.resources', 'ecg_graph_template.svg')
    # Writing ECG meta data
    page_2_template = page_2_template.replace('$$recorded_time$$', str(record_time))
    page_2_template = page_2_template.replace('$$duration$$', meta_data['display_information']['Duration'])
    page_2_template = page_2_template.replace('$$graph_image$$', str(file_name))

    # # Writing meta data display info
    meta_data['display_information'].update(meta)
    # Forming xml syntax
    meta_xml = ''
    y = 0
    for info_key, info_value in meta_data['display_information'].iteritems():
        meta_xml += '<tspan x="0" y="' + str(y) + '" font-size="10">' + str(info_key) + ': ' + str(info_value) + '</tspan>'
        y += 16
        
    page_2_template = page_2_template.replace('$$meta$$', str(meta_xml))
    
    # Converting svg to pdf using phantomjs
    # Saving to temp svg
    graph_page_svg_path = output_dir + 'graph_page.svg'
    with open(graph_page_svg_path,'w') as fout_svg2:
        fout_svg2.write(page_2_template)

    # Replacing phantom pdf js file placeholders to temp2 js
    temp_phantom_js_path2 = output_dir + '/temp2.js'

    with open(temp_phantom_js_path2, 'w') as temp_phantom_js2:
        #phantom_template = f.read()
        phantom_template = resource_string('pyECG_graph.resources', 'phantompdf.js')
        write_data = phantom_template.replace('$$file_path$$',graph_page_svg_path)
        write_data = write_data.replace('$$output_dir$$', (output_dir + output_file_name + '.' + export_to) )
        temp_phantom_js2.write(write_data)

    # subprocess call for converting svg to pdf using phantom js
    subprocess.call(['phantomjs', temp_phantom_js_path2])

    # Removing temporary files
    os.remove(file_name)
    os.remove(graph_page_svg_path)
    os.remove(temp_phantom_js_path2)
    
    # Returning meta data
    logger.info("ECG graph plotted successfully to %s" % (output_dir + output_file_name + '.' + export_to))
    return meta_data
