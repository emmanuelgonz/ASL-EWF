ASL-CLI
=======
ASL-CLI provides a command line interface (CLI) for the AirSurf-Lettuce application created by the `Crops Phenomics Group
<https://github.com/Crop-Phenomics-Group/>`_. This CLI allows you to quickly feed inputs through the command line, rather than using a GUI. 

Analyzing lettuce & generating images
-------------------------------------
To use the CLI, download the repo and run the whole_pipe function found in the aslfire2.py file as follows:

* First install all dependencies by running:

.. code::
   
   git clone https://github.com/emmanuelgonz/ASL-EWF.git
   cd ASL-EWF
   cd src/
   ./depend.sh

* Now you're ready to run the pipeline! Continue by running the following command:

.. code::

   python3 aslwindow.py run_pipeline <image file directory> <image file name>

* Here is an example to run a sample image. This is an example, make sure to change to your own directory.

.. code::
   
   python3 aslwindow.py run_pipeline '/home/emmanuel/Documents/ASL-EWF/test_images/sample_region1.png' 'sample_region1'

After running this file, the following files will be output into ..data/<filename>/:
- boxes.npy

- loop_vars.npy

- probs.npy

- size_labels.npy

- sizes.png

- counts.png

- grey_conversion.png

- harvest_regions.png

Generating CSV file with counts/size categorization
---------------------------------------------------
The next step is to run **aslsizefile.py** for lettuce head counting and size categorization (small, medium, large).

* Lets count some lettuce!

.. code::
   python3 aslsizefile.py create_quadrant_file '<output_directory> <name>
   
* Below is an example:

.. code::
   
   python3 aslfile.py create_quadrant_file '/home/emmanuel/Documents/ASL-EWF/data/medium_grey_conv/' 'grey_conversion'
   
