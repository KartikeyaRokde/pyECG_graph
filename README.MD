# (

A python library for plotting ECG graph

## Installation

- System dependencies `phantomjs`
[Install phantomjs] (http://phantomjs.org/build.html)

- Install dependencies `matplotlib==1.4.0` and `numpy==1.9.2`
```
$ pip install -r requirements.txt
```

- Download the project and run `setup.py`
```
$ python setup.py install
```

## Usage

```python
from pyECG_graph import pyECG
pyECG.generate_ecg_graph(ecg_data='sample_ecg_data.txt', output_dir='/tmp/', export_to='pdf', output_file_name='mygraph')
```

### Arguments
1. ecg_data:
   - Required
   - Accepts a valid list containing ECG graph values
   - Also accepts a valid data file path

2. output_dir:
   - Required
   - Valid path where output file is to be placed

3. export_to:
   - Exports ECG graph to provided format
   - Currently supported formats are 'pdf', 'jpg', 'png'
   - Default is 'pdf'. Gives a very nice output.

4. output_file_name:
   - name of output file generated
   - Default is 'graph'

This will generate `mygraph.pdf` in the provided output directory.

See some sample output files generated:

1. [Exported to PDF] (https://github.com/KartikeyaRokde/pyECG_graph/blob/master/pyECG_graph/output/mygraph.pdf)

2. Exported to PNG

![alt text][logo]
[logo]: https://github.com/KartikeyaRokde/pyECG_graph/blob/master/pyECG_graph/output/mygraph.png "mygraph.png"


2. Exported to JPG

![alt text][logo]
[logo]: https://github.com/KartikeyaRokde/pyECG_graph/blob/master/pyECG_graph/output/mygraph.jpg "mygraph.jpg"


That's it. Happy ECG :)
